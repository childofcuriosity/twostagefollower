from common import *
import contextlib,hashlib,os,time
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM,GenerationConfig
from peft import LoraConfig,get_peft_model,PeftModel

def load(cfg,seed,device,adapter=None,train=True):
 torch.set_num_threads(4)
 if cfg.get("deterministic_algorithms",False):
  os.environ["CUBLAS_WORKSPACE_CONFIG"]=":4096:8"
  torch.use_deterministic_algorithms(True)
 tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True,padding_side='left')
 base=AutoModelForCausalLM.from_pretrained(MODEL,local_files_only=True,torch_dtype=torch.bfloat16,attn_implementation=cfg['attention']).to(device)
 torch.manual_seed(seed)
 if adapter:
  model=PeftModel.from_pretrained(base,adapter,is_trainable=train)
 else:
  model=get_peft_model(base,LoraConfig(r=cfg['lora_r'],lora_alpha=cfg['lora_alpha'],lora_dropout=cfg['lora_dropout'],target_modules=cfg['lora_targets'],task_type='CAUSAL_LM'))
 # Stable FP32 master trainable adapters; BF16 base/forward, no quantization.
 for p in model.parameters():
  if p.requires_grad:p.data=p.data.float()
 if cfg['gradient_checkpointing'] and train:
  model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False})
  model.enable_input_require_grads()
 return model,tok

def adapter_hash(model):
 h=hashlib.sha256()
 for n,p in sorted(model.named_parameters()):
  if p.requires_grad:h.update(n.encode());h.update(p.detach().cpu().contiguous().view(torch.uint8).numpy().tobytes())
 return h.hexdigest()

def generate(model,tok,rows,c,cfg,sample,G=1):
 device=next(model.parameters()).device;model.eval();out=[]
 eos=model.generation_config.eos_token_id;eos=[eos] if isinstance(eos,int) else eos
 repeated=[row for row in rows for _ in range(G)]
 gcfg=GenerationConfig(do_sample=sample,num_beams=1,max_new_tokens=cfg['max_new_tokens'],eos_token_id=eos,pad_token_id=tok.pad_token_id,bos_token_id=tok.bos_token_id,use_cache=True,**(dict(temperature=cfg['sample_temperature'],top_p=cfg['sample_top_p'],top_k=cfg['sample_top_k']) if sample else {}))
 start=time.time()
 for offset in range(0,len(repeated),cfg['generation_batch'] if sample else cfg['eval_batch']):
  chunk=repeated[offset:offset+(cfg['generation_batch'] if sample else cfg['eval_batch'])]
  prompts=[tok.apply_chat_template([dict(role='user',content=prompt(x,c))],tokenize=True,add_generation_prompt=True) for x in chunk]
  size=max(map(len,prompts));ids=torch.tensor([[tok.pad_token_id]*(size-len(p))+p for p in prompts],device=device)
  mask=torch.tensor([[0]*(size-len(p))+[1]*len(p) for p in prompts],device=device)
  torch.cuda.synchronize();t=time.time()
  with torch.inference_mode():outputs=model.generate(input_ids=ids,attention_mask=mask,generation_config=gcfg)
  torch.cuda.synchronize();seconds=time.time()-t
  for j,(row,p,seq) in enumerate(zip(chunk,prompts,outputs[:,size:].tolist())):
   stop=next((k for k,t in enumerate(seq) if t in eos),None);tokens=seq if stop is None else seq[:stop+1]
   text=tok.decode(tokens,skip_special_tokens=True);finish='length' if stop is None else 'eos'
   out.append(dict(row,condition=c,candidate=(offset+j)%G,prompt_ids=p,output_ids=tokens,raw=text,generated_tokens=len(tokens),input_tokens=len(p),finish_reason=finish,allocated_generate_seconds=seconds/len(chunk),grading=score(row,text,c,len(tokens),finish)))
  del ids,mask,outputs
 return out,time.time()-start

def pack(rows,pad,device):
 length=max(len(x['prompt_ids'])+len(x['output_ids']) for x in rows)
 ids=[];attention=[];completion=[]
 for x in rows:
  p=x['prompt_ids'];o=x['output_ids'];n=length-len(p)-len(o)
  # Left padding gives the same position IDs as generation; completion mask explicitly includes true EOS.
  ids.append([pad]*n+p+o);attention.append([0]*n+[1]*(len(p)+len(o)));completion.append([0]*(n+len(p))+[1]*len(o))
 ids=torch.tensor(ids,device=device);att=torch.tensor(attention,device=device);mask=torch.tensor(completion,device=device,dtype=torch.float32)
 return ids,att,mask[:,1:]

def logps(model,ids,attention):
 positions=attention.long().cumsum(-1)-1;positions.masked_fill_(attention==0,1)
 outputs=model(input_ids=ids,attention_mask=attention,position_ids=positions,use_cache=False)
 # Chunk along sequence to avoid materializing another full-vocabulary FP32 tensor.
 logits=outputs.logits[:,:-1,:];target_ids=ids[:,1:];parts=[]
 for k in range(0,logits.shape[1],32):
  z=logits[:,k:k+32,:].float();parts.append(z.gather(-1,target_ids[:,k:k+32,None]).squeeze(-1)-z.logsumexp(-1))
 result=torch.cat(parts,dim=1);del outputs,logits
 return result

def advantages(rewards,G,eps):
 r=torch.tensor(rewards,dtype=torch.float32).reshape(-1,G)
 mean=r.mean(1,keepdim=True);std=r.std(1,keepdim=True,correction=1)
 return ((r-mean)/(std+eps)).reshape(-1),dict(mean_reward=float(r.mean()),mixed_groups=int(((r.sum(1)>0)&(r.sum(1)<G)).sum()),groups=len(r),all_zero_groups=int((r.sum(1)==0).sum()),all_one_groups=int((r.sum(1)==G).sum()),mean_group_std=float(std.mean()))

def loss_terms(logp,ref,mask,adv,cfg):
 # One optimizer update per fresh rollout; old-policy is current policy detached before this update.
 old=logp.detach();ratio=torch.exp(logp-old)
 unclipped=ratio*adv[:,None];clipped=ratio.clamp(1-cfg['clip_epsilon'],1+cfg['clip_epsilon'])*adv[:,None]
 logratio=(ref-logp)*mask;kl=torch.exp(logratio)-logratio-1
 per_token=-torch.minimum(unclipped,clipped)+cfg['beta']*kl
 lengths=mask.sum(1);assert bool((lengths>0).all())
 loss=((per_token*mask).sum(1)/lengths).mean()
 return loss,dict(kl=float(((kl.detach()*mask).sum(1)/lengths).mean()),policy_loss=float(((-unclipped.detach()*mask).sum(1)/lengths).mean()),token_count=int(mask.sum()),ratio_max_deviation=float((ratio.detach()-1).abs().max()))
