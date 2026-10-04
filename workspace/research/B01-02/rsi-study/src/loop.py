import argparse,math,time,contextlib
from common import *
from model_utils import load_model,propose
import loop_data as ld
import torch
from transformers import set_seed
from peft import LoraConfig,get_peft_model

def evaluate(model,tok,domain,out):
 model.eval();model.config.use_cache=True;tok.padding_side='left';rows=json.loads((ROOT/f'data/loop-eval-{domain}.json').read_text());results=[]
 for start in range(0,len(rows),16):
  batch=rows[start:start+16];ins=tok([ld.prompt(r,domain) for r in batch],return_tensors='pt',padding=True).to('cuda')
  with torch.inference_mode():z=model.generate(**ins,max_new_tokens=256,do_sample=False,pad_token_id=tok.eos_token_id,eos_token_id=tok.eos_token_id)
  for row,raw in zip(batch,tok.batch_decode(z[:,ins.input_ids.shape[1]:],skip_special_tokens=True)):
   expected=ld.engine(domain).execute(row['x'],row['ops']);expected=list(expected) if domain=='digits' else expected;pred=ld.answer(raw,domain)
   ops=re.findall(r'^(rev|rot|inc|neg|swap|ends)\s',raw,re.M)
   results.append({**row,'raw':raw,'expected':expected,'prediction':pred,'correct':pred==expected,'exact_program':ops==row['ops']})
 out.write_text(''.join(json.dumps(r)+'\n' for r in results))
 return {s:{'n':sum(r['split']==s for r in results),'accuracy':sum(r['correct'] for r in results if r['split']==s)/sum(r['split']==s for r in results),'program_accuracy':sum(r['exact_program'] for r in results if r['split']==s)/sum(r['split']==s for r in results)} for s in ['short','family','pressure']}
def encode(tok,p,t):
 x=tok.encode(p,add_special_tokens=False);y=tok.encode(t,add_special_tokens=False)+[tok.eos_token_id];return x+y,[-100]*len(x)+y
def batchify(tok,examples):
 n=max(len(x) for x,y in examples);ids=torch.full((len(examples),n),tok.eos_token_id,device='cuda',dtype=torch.long);labels=torch.full_like(ids,-100);mask=torch.zeros_like(ids)
 for i,(x,y) in enumerate(examples):ids[i,:len(x)]=torch.tensor(x,device='cuda');labels[i,:len(y)]=torch.tensor(y,device='cuda');mask[i,:len(x)]=1
 return dict(input_ids=ids,labels=labels,attention_mask=mask)
def train_round(model,tok,rows,aux,domain,seed,out,steps=128):
 model.train();model.config.use_cache=False;set_seed(seed);rng=random.Random(seed)
 data=[encode(tok,ld.prompt(r,domain),ld.target(r,domain)) for r in rows];extra=[encode(tok,p,t) for p,t in aux]
 parameters=[p for p in model.parameters() if p.requires_grad];opt=torch.optim.AdamW(parameters,lr=1e-4,weight_decay=.01,fused=True);counts=dict(exec_input_tokens=0,exec_target_tokens=0,aux_input_tokens=0,aux_target_tokens=0,exec_examples=0,aux_examples=0)
 order=list(range(len(data)));rng.shuffle(order);start=time.time()
 with (out/'train.jsonl').open('w',buffering=1) as log:
  for st in range(steps):
   opt.zero_grad(set_to_none=True);b=batchify(tok,[data[order[(st*16+j)%len(order)]] for j in range(16)])
   loss=model(**b).loss;mainloss=float(loss.detach());loss.backward();counts['exec_input_tokens']+=int(b['attention_mask'].sum());counts['exec_target_tokens']+=int((b['labels']!=-100).sum());counts['exec_examples']+=16
   extra_loss=None
   if extra:
    b=batchify(tok,rng.choices(extra,k=4));loss=model(**b).loss;extra_loss=float(loss.detach());(.2*loss).backward();counts['aux_input_tokens']+=int(b['attention_mask'].sum());counts['aux_target_tokens']+=int((b['labels']!=-100).sum());counts['aux_examples']+=4
   grad=torch.nn.utils.clip_grad_norm_(parameters,1.);opt.step();log.write(json.dumps(dict(step=st+1,execution_loss=mainloss,aux_loss=extra_loss,grad_norm=float(grad),seconds=time.time()-start,**counts))+'\n')
   if (st+1)%32==0:print('step',st+1,'loss',mainloss,flush=True)
 model.save_pretrained(out/'adapter');model.config.use_cache=True;return dict(seconds=time.time()-start,counts=counts,trainable_parameters=sum(p.numel() for p in parameters))
def collect(model,tok,families,seed,out,frozen=False,n=16):
 records=[];libraries={}
 ctx=model.disable_adapter() if frozen else contextlib.nullcontext()
 with ctx:
  for f in families:
   r=propose(model,tok,f,n=n,seed=seed+f['id']);records.append(r);lib=select(f['support'],[p['candidate'] for p in r['proposals']]);libraries[str(f['id'])]=lib
 out.write_text(''.join(json.dumps(r)+'\n' for r in records));return records,libraries

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--condition',choices=['shared','frozen','replay','joint','shuffled'],required=True);ap.add_argument('--seed',type=int,required=True);ap.add_argument('--domain',choices=['digits','strings'],default='digits');a=ap.parse_args()
 out=ROOT/'runs'/f'loop-{a.domain}-{a.condition}-s{a.seed}';out.mkdir(exist_ok=False);start=time.time();set_seed(a.seed);torch.set_num_threads(4)
 if a.domain=='strings':
  import common
  common.sig=lru_cache(None)(ld.secondary.signature);common.IDENTITY=common.sig(())
 model,tok=load_model('qwen1.5b');model=get_peft_model(model,LoraConfig(r=16,lora_alpha=32,lora_dropout=0.,target_modules=['q_proj','k_proj','v_proj','o_proj','gate_proj','up_proj','down_proj'],task_type='CAUSAL_LM'))
 families=load();train=[f for f in families if f['split']=='train'];test=[f for f in families if f['split']=='test'];metrics=[]
 initial,_=collect(model,tok,train,a.seed*100000,out/'initial-replay.jsonl',True)
 replay=[(r['prompt'],p['raw']) for r in initial for p in r['proposals']]
 if a.condition=='shuffled':
  groups={}
  for i,(p,t) in enumerate(replay):groups.setdefault(len(tok.encode(t,add_special_tokens=False)),[]).append(i)
  targets=[t for p,t in replay];shuffle_rng=random.Random(a.seed+9301)
  for indices in groups.values():
   texts=[targets[i] for i in indices];shuffle_rng.shuffle(texts)
   for i,t in zip(indices,texts):targets[i]=t
  replay=[(p,t) for (p,_),t in zip(replay,targets)]
 for rnd in range(4):
  stage=out/f'round{rnd}';stage.mkdir();result={'round':rnd}
  if rnd:
   rec,libraries=collect(model,tok,train,a.seed*100000+rnd*1000,stage/'train-proposals.jsonl',a.condition=='frozen')
   rows=ld.training_data(libraries,a.seed*100000+rnd*1000,a.domain);(stage/'training-data.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows));(stage/'libraries.json').write_text(json.dumps(libraries))
   aux=[]
   if a.condition in ['replay','shuffled']:aux=replay
   if a.condition=='joint':
    for r in rec:
     for c in libraries[str(r['family'])]:aux.append((r['prompt'],','.join(CANDIDATES[c])+'\n'))
   (stage/'auxiliary.jsonl').write_text(''.join(json.dumps(dict(prompt=p,target=t))+'\n' for p,t in aux));result['training']=train_round(model,tok,rows,aux,a.domain,a.seed+rnd*100,stage)
  else:model.save_pretrained(stage/'adapter')
  result['execution']=evaluate(model,tok,a.domain,stage/'execution.jsonl')
  rec,libraries=collect(model,tok,test,a.seed*100000+50000,stage/'test-proposals.jsonl',a.condition=='frozen')
  result['proposal']=[dict(family=f['id'],selected=libraries[str(f['id'])],compression=utility(f['test'],libraries[str(f['id'])]),unique_semantics=len({ld.engine(a.domain).signature(CANDIDATES[p['candidate']]) for p in r['proposals']})) for f,r in zip(test,rec)]
  (stage/'summary.json').write_text(json.dumps(result,indent=2));metrics.append(result);print('ROUND COMPLETE',a.condition,a.domain,a.seed,rnd,flush=True)
 (out/'summary.json').write_text(json.dumps(dict(args=vars(a),wall_seconds=time.time()-start,rounds=metrics),indent=2))
if __name__=='__main__':main()
