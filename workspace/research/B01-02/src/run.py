import argparse,json,math,time,random,hashlib,os,re
from pathlib import Path
import numpy as np
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM,set_seed
from peft import LoraConfig,get_peft_model,PeftModel
from dsl import prompt,target,expand,execute,answer,step
ROOT=Path(__file__).resolve().parents[1]
def read(name):return [json.loads(l) for l in (ROOT/f'data/{name}.jsonl').read_text().splitlines()]
def evaluate(model,tok,rows,world,out,with_library=False,fewshot=False):
 model.eval();tok.padding_side='left';results=[];start=time.time()
 lib=world['library'];names=world['names'];old=json.loads((ROOT/'data/worlds.json').read_text())['original']['library']
 prefix=''
 if fewshot:
  prefix=''.join(prompt(r,names,lib if with_library else None)+target(r,lib,'flat',names)+'\n' for r in read('train')[:2])
 for ix in range(0,len(rows),32):
  batch=rows[ix:ix+32]
  ins=tok([prefix+prompt(r,names,lib if with_library else None) for r in batch],padding=True,return_tensors='pt').to('cuda')
  with torch.inference_mode():generated=model.generate(**ins,max_new_tokens=256,do_sample=False,pad_token_id=tok.pad_token_id,eos_token_id=tok.eos_token_id)
  tokens=generated[:,ins.input_ids.shape[1]:];texts=tok.batch_decode(tokens,skip_special_tokens=True)
  for r,txt,ids in zip(batch,texts,tokens):
   expected=execute(r['x'],expand(r['chain'],lib));pred=answer(txt)
   traces=re.findall(r'\b(rev|rot|inc|neg|swap|ends)\s+(\d)\s+(\d)\s+(\d)\s+(\d)',txt)
   state=tuple(r['x']);valid=bool(traces)
   for tr in traces:
    state=step(state,tr[0]);valid=valid and state==tuple(map(int,tr[1:]))
   generated_ops=[tr[0] for tr in traces]
   results.append({**r,'raw':txt,'expected':expected,'prediction':pred,'correct':pred==expected,'old_world_answer':execute(r['x'],expand(r['chain'],old)),'matches_old_world':pred==execute(r['x'],expand(r['chain'],old)),'primitive_sequence_correct':generated_ops==list(expand(r['chain'],lib)),'execution_steps_correct':valid,'generated_tokens':int((ids!=tok.pad_token_id).sum())})
  if ix%128==0:print('eval',out.name,ix,len(rows),flush=True)
 out.write_text(''.join(json.dumps(r)+'\n' for r in results))
 groups={}
 for key in sorted({r['split'] for r in results}):
  rs=[r for r in results if r['split']==key];groups[key]={'n':len(rs),'accuracy':sum(r['correct'] for r in rs)/len(rs),'program_accuracy':sum(r['primitive_sequence_correct'] for r in rs)/len(rs),'valid_execution':sum(r['execution_steps_correct'] for r in rs)/len(rs)}
 return {'groups':groups,'elapsed_seconds':time.time()-start,'generated_tokens':sum(r['generated_tokens'] for r in results)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--condition',choices=['flat','macro','natural','shuffled','frozen'],required=True);ap.add_argument('--seed',type=int,default=11);ap.add_argument('--world',default='original');ap.add_argument('--steps',type=int,default=512);ap.add_argument('--microbatch',type=int,default=16);ap.add_argument('--accum',type=int,default=2);ap.add_argument('--calibrate',action='store_true');ap.add_argument('--eval-only',action='store_true');ap.add_argument('--with-library',action='store_true');ap.add_argument('--tag',default='');args=ap.parse_args()
 runid=f'{args.condition}-{args.world}-s{args.seed}'+('-calibration' if args.calibrate else '')+args.tag
 out=ROOT/'runs'/runid;out.mkdir(exist_ok=True);set_seed(args.seed);torch.set_num_threads(4)
 tok=AutoTokenizer.from_pretrained(ROOT/'model',local_files_only=True);tok.pad_token=tok.eos_token
 world=json.loads((ROOT/'data/worlds.json').read_text())[args.world]
 model=AutoModelForCausalLM.from_pretrained(ROOT/'model',torch_dtype=torch.bfloat16,attn_implementation='sdpa',local_files_only=True).cuda()
 total_start=time.time();meta={'args':vars(args),'torch':torch.__version__,'cuda':torch.version.cuda,'gpu':torch.cuda.get_device_name(),'model_revision':json.loads((ROOT/'model/download-manifest.json').read_text())['revision'],'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
 (out/'config.json').write_text(json.dumps(meta,indent=2))
 if args.condition!='frozen':
  if args.eval_only:model=PeftModel.from_pretrained(model,out/'adapter')
  else:
   model=get_peft_model(model,LoraConfig(r=16,lora_alpha=32,lora_dropout=0.0,target_modules=['q_proj','k_proj','v_proj','o_proj','gate_proj','up_proj','down_proj'],task_type='CAUSAL_LM'))
   model.config.use_cache=False
   train=read('train');encoded=[]
   for row in train:
    p=tok(prompt(row,world['names']),add_special_tokens=False).input_ids
    t=tok(target(row,world['library'],args.condition,world['names']),add_special_tokens=False).input_ids+[tok.eos_token_id]
    encoded.append((p+t,[-100]*len(p)+t))
   maxlen=max(len(a) for a,b in encoded)
   if maxlen>256:raise RuntimeError(f'Unexpected training sequence length {maxlen}')
   parameters=[p for p in model.parameters() if p.requires_grad]
   meta.update(trainable_parameters=sum(p.numel() for p in parameters),total_parameters=sum(p.numel() for p in model.parameters()),max_train_sequence=maxlen)
   opt=torch.optim.AdamW(parameters,lr=3e-4,weight_decay=.01,eps=1e-8,fused=True)
   rng=random.Random(args.seed);order=list(range(len(encoded)));rng.shuffle(order);cursor=0
   def batch():
    nonlocal cursor
    if cursor+args.microbatch>len(order):rng.shuffle(order);cursor=0
    items=[encoded[i] for i in order[cursor:cursor+args.microbatch]];cursor+=args.microbatch
    n=max(len(x[0]) for x in items)
    ids=torch.full((len(items),n),tok.pad_token_id,dtype=torch.long,device='cuda');labels=torch.full_like(ids,-100);mask=torch.zeros_like(ids)
    for i,(x,y) in enumerate(items):ids[i,:len(x)]=torch.tensor(x,device='cuda');labels[i,:len(y)]=torch.tensor(y,device='cuda');mask[i,:len(x)]=1
    return dict(input_ids=ids,labels=labels,attention_mask=mask)
   model.train();t0=time.time();counts={'input_tokens':0,'target_tokens':0,'examples':0};losses=[]
   with (out/'train.jsonl').open('w',buffering=1) as log:
    for st in range(args.steps):
     frac=(st+1)/max(1,min(20,args.steps));decay=.1+.9*.5*(1+math.cos(math.pi*st/args.steps));lr=3e-4*min(1,frac)*decay
     for group in opt.param_groups:group['lr']=lr
     opt.zero_grad(set_to_none=True);lossval=0
     for _ in range(args.accum):
      b=batch();z=model(**b);loss=z.loss/args.accum;loss.backward();lossval+=float(loss.detach());counts['input_tokens']+=int(b['attention_mask'].sum());counts['target_tokens']+=int((b['labels']!=-100).sum());counts['examples']+=len(b['input_ids'])
     grad=torch.nn.utils.clip_grad_norm_(parameters,1.0);opt.step();elapsed=time.time()-t0
     row={'step':st+1,'loss':lossval,'lr':lr,'grad_norm':float(grad),'elapsed':elapsed,**counts};log.write(json.dumps(row)+'\n');losses.append(lossval)
     if st%20==0 or st+1==args.steps:print(runid,row,flush=True)
   torch.cuda.synchronize();meta['training']={'seconds':time.time()-t0,'counts':counts,'first_loss':losses[0],'last_loss':losses[-1],'peak_memory_bytes':torch.cuda.max_memory_allocated()}
   model.save_pretrained(out/'adapter');meta['training']['adapter_only']=True
   (out/'config.json').write_text(json.dumps(meta,indent=2))
   model.config.use_cache=True
 evalrows=read('dev' if args.calibrate else 'test')
 if args.calibrate:evalrows=evalrows[:64]+evalrows[128:160]
 meta['evaluation']=evaluate(model,tok,evalrows,world,out/'predictions.jsonl',args.with_library,args.condition=='frozen')
 meta['total_seconds']=time.time()-total_start;meta['gpu_hours']=meta['total_seconds']/3600
 (out/'summary.json').write_text(json.dumps(meta,indent=2));print('DONE',runid,json.dumps(meta['evaluation']),flush=True)
if __name__=='__main__':main()
