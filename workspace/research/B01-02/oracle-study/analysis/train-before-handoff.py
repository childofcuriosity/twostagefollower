import argparse,collections,hashlib,json,math,os,random,socket,subprocess,time,traceback
from protocol import *
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM,set_seed
from peft import LoraConfig,get_peft_model

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--model',choices=MODELS,required=True);ap.add_argument('--condition',choices=MODES,required=True);ap.add_argument('--seed',type=int,required=True);ap.add_argument('--steps',type=int,default=512);ap.add_argument('--microbatch',type=int,default=4);ap.add_argument('--probe',action='store_true');a=ap.parse_args()
 assert 16%a.microbatch==0
 out=R/'runs'/f'{a.model}-{a.condition}-s{a.seed}{"-probe" if a.probe else ""}'
 out.mkdir(exist_ok=False);set_seed(a.seed);torch.set_num_threads(4);t0=time.time()
 config=dict(args=vars(a),pid=os.getpid(),host=socket.gethostname(),start_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),torch=torch.__version__,cuda=torch.version.cuda,gpu=torch.cuda.get_device_name(),visible_gpu=os.environ.get('CUDA_VISIBLE_DEVICES'),source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/'src').glob('*.py')},gpu_inventory=subprocess.run(['nvidia-smi','--query-gpu=index,uuid,name,driver_version','--format=csv,noheader'],capture_output=True,text=True).stdout)
 (out/'config.json').write_text(json.dumps(config,indent=2))
 tok=AutoTokenizer.from_pretrained(MODELS[a.model],local_files_only=True);tok.pad_token=tok.eos_token
 encoded=[encode(row,tok,a.condition) for row in read('train')]
 model=AutoModelForCausalLM.from_pretrained(MODELS[a.model],local_files_only=True,torch_dtype=torch.bfloat16,attn_implementation='sdpa',low_cpu_mem_usage=True).cuda()
 model=get_peft_model(model,LoraConfig(r=16,lora_alpha=32,lora_dropout=0.,target_modules=['q_proj','k_proj','v_proj','o_proj','gate_proj','up_proj','down_proj'],task_type='CAUSAL_LM'))
 model.config.use_cache=False;model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False});model.enable_input_require_grads();model.train()
 params=[p for p in model.parameters() if p.requires_grad];opt=torch.optim.AdamW(params,lr=3e-4,weight_decay=.01,eps=1e-8,fused=True)
 rng=random.Random(a.seed);order=list(range(len(encoded)));rng.shuffle(order);cursor=0;counts=collections.Counter();start=time.time()
 def batch():
  nonlocal cursor
  if cursor+a.microbatch>len(order):rng.shuffle(order);cursor=0
  items=[encoded[i] for i in order[cursor:cursor+a.microbatch]];cursor+=a.microbatch;n=max(len(x['ids']) for x in items)
  ids=torch.full((len(items),n),tok.pad_token_id,dtype=torch.long,device='cuda');labels=torch.full_like(ids,-100);mask=torch.zeros_like(ids)
  for i,e in enumerate(items):ids[i,:len(e['ids'])]=torch.tensor(e['ids'],device='cuda');labels[i,:len(e['labels'])]=torch.tensor(e['labels'],device='cuda');mask[i,:len(e['ids'])]=1
  return dict(input_ids=ids,labels=labels,attention_mask=mask)
 with (out/'train.jsonl').open('x',buffering=1) as log:
  for st in range(a.steps):
   lr=3e-4*min(1,(st+1)/20)*(.1+.9*.5*(1+math.cos(math.pi*st/512)))
   for g in opt.param_groups:g['lr']=lr
   opt.zero_grad(set_to_none=True);value=0
   for logical in range(2):
    bs=[batch() for _ in range(16//a.microbatch)];ns=[int((b['labels'][:,1:]!=-100).sum()) for b in bs];den=sum(ns)
    for b,n in zip(bs,ns):
     loss=model(**b).loss*(n/den)/2
     if not torch.isfinite(loss):raise RuntimeError('Nonfinite loss')
     loss.backward();value+=float(loss.detach());counts['examples']+=len(b['input_ids']);counts['input_tokens']+=int(b['attention_mask'].sum());counts['supervised_tokens']+=n
   grad=torch.nn.utils.clip_grad_norm_(params,1.);opt.step()
   rec=dict(step=st+1,loss=value,lr=lr,grad_norm=float(grad),seconds=time.time()-start,**counts);log.write(json.dumps(rec)+'\n')
   if st==0 or (st+1)%32==0:print(json.dumps(rec),flush=True)
   if not a.probe and st+1 in [64,128,256,512]:model.save_pretrained(out/f'checkpoints/step{st+1:04d}/adapter')
 if not a.probe:model.save_pretrained(out/'adapter')
 result=dict(config=config,train_seconds=time.time()-start,total_seconds=time.time()-t0,steps=a.steps,counts=dict(counts),trainable_parameters=sum(p.numel() for p in params),peak_memory_bytes=torch.cuda.max_memory_allocated(),status='probe_passed' if a.probe else 'training_complete')
 (out/'training-complete.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
if __name__=='__main__':main()
