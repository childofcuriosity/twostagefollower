import argparse,hashlib,json,time
from protocol import *
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM,StoppingCriteria,StoppingCriteriaList
from peft import PeftModel

class Boundary(StoppingCriteria):
 def __init__(self,tok,start,phase):self.tok=tok;self.start=start;self.phase=phase
 def __call__(self,ids,scores,**kwargs):
  raw=self.tok.batch_decode(ids[:,self.start:],skip_special_tokens=True,clean_up_tokenization_spaces=False)
  return torch.tensor([('\n' in t if self.phase=='header' else 'EndTool\n' in t) for t in raw],device=ids.device)

class Session:
 def __init__(self,row,tok,mode):
  self.row=row;self.tok=tok;self.mode=mode;self.ids=tok.encode(prompt(row),add_special_tokens=False);self.events=[];self.calls=[];self.state=tuple(row['x']);self.phase='header';self.stop=None;self.generated=0
 def append(self,text,source,phase,ids=None):
  prefix_n=len(self.ids);prefix_hash=hashlib.sha256(json.dumps(self.ids).encode()).hexdigest()
  if ids is None:ids=self.tok.encode(text,add_special_tokens=False)
  assert self.tok.decode(ids,clean_up_tokenization_spaces=False)==text
  self.events.append(dict(source=source,phase=phase,text=text,token_ids=ids,prefix_tokens=prefix_n,prefix_sha256=prefix_hash))
  self.ids+=ids
 def advance_oracle(self):
  if self.stop:return
  if self.mode=='order_oracle' and self.phase=='header':
   if len(self.calls)==len(self.row['chain']):self.append('Done\n','oracle','finish');self.stop='oracle_done';return
   tool=self.row['chain'][len(self.calls)];self.append(NAMES[tool]+':\n','oracle','header');self.calls.append(dict(tool=tool,header_source='oracle',input_state=list(self.state)));self.phase='body'
  if self.mode=='operation_oracle' and self.phase=='body':
   tool=self.calls[-1]['tool'];text,end=body(tool,self.state);self.append(text,'oracle','body');self.calls[-1]['body']=parse_body(text,self.state,tool);self.calls[-1]['body_source']='oracle';self.state=end;self.phase='header'
 def accept(self,ids):
  if self.tok.eos_token_id in ids:ids=ids[:ids.index(self.tok.eos_token_id)];eos=True
  else:eos=False
  text=self.tok.decode(ids,clean_up_tokenization_spaces=False);self.generated+=len(ids);phase=self.phase
  self.append(text,'model',phase,ids)
  self.events[-1]['observed_eos']=eos
  try:
   if phase=='header':
    tool=parse_header(text)
    if tool is None:self.stop='done';return
    if len(self.calls)>=16:self.stop='call_budget';return
    self.calls.append(dict(tool=tool,header_source='model',input_state=list(self.state)));self.phase='body'
   else:
    b=parse_body(text,self.state,self.calls[-1]['tool']);self.calls[-1]['body']=b;self.calls[-1]['body_source']='model';self.state=tuple(b['state']);self.phase='header'
  except ValueError as ex:self.stop='eos_or_protocol_error' if eos else 'protocol_or_fragment_budget';self.events[-1]['error']=str(ex)
 def finish(self):
  if self.mode=='operation_oracle':assert all(e['source']=='oracle' for e in self.events if e['phase']=='body')
  if self.mode=='order_oracle':assert all(e['source']=='oracle' for e in self.events if e['phase']=='header')
  return dict(**self.row,mode=self.mode,stop=self.stop,generated_tokens=self.generated,events=self.events,calls=self.calls,grade=grade(self.row,self.calls,self.stop))

def evaluate(model,tok,rows,mode,path,batch_size=8):
 assert not path.exists();start=time.time();totals=[]
 with path.open('x',buffering=1) as f:
  for offset in range(0,len(rows),batch_size):
   sessions=[Session(row,tok,mode) for row in rows[offset:offset+batch_size]]
   while any(s.stop is None for s in sessions):
    for s in sessions:
     s.advance_oracle()
     if s.stop is None and (s.generated>=2048 or len(s.ids)+128>4096):s.stop='token_or_context_budget'
    for phase in ['header','body']:
     for s in sessions:s.advance_oracle()
     active=[s for s in sessions if s.stop is None and s.phase==phase]
     if not active:continue
     n=max(len(s.ids) for s in active);ids=torch.full((len(active),n),tok.pad_token_id,dtype=torch.long,device=model.device);mask=torch.zeros_like(ids)
     for i,s in enumerate(active):ids[i,-len(s.ids):]=torch.tensor(s.ids,device=model.device);mask[i,-len(s.ids):]=1
     with torch.inference_mode():z=model.generate(input_ids=ids,attention_mask=mask,max_new_tokens=24 if phase=='header' else 128,do_sample=False,pad_token_id=tok.pad_token_id,eos_token_id=tok.eos_token_id,stopping_criteria=StoppingCriteriaList([Boundary(tok,n,phase)]),use_cache=True)
     for s,new in zip(active,z[:,n:].tolist()):s.accept(new)
   for s in sessions:
    result=s.finish();f.write(json.dumps(result)+'\n');totals.append(result['grade'])
   if offset%64==0:print(json.dumps(dict(file=path.name,completed=min(offset+batch_size,len(rows)),total=len(rows),seconds=time.time()-start)),flush=True)
 return dict(n=len(totals),complete=sum(g['complete'] for g in totals),sequence_correct=sum(g['sequence_correct'] for g in totals),all_expansions_correct=sum(g['all_expansions_correct'] for g in totals),seconds=time.time()-start)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--model',choices=MODELS,required=True);ap.add_argument('--condition',choices=MODES,required=True);ap.add_argument('--seed',type=int,required=True);ap.add_argument('--calibration',action='store_true');ap.add_argument('--batch-size',type=int,default=8);a=ap.parse_args()
 torch.set_num_threads(4);torch.manual_seed(a.seed);run=R/'runs'/f'{a.model}-{a.condition}-s{a.seed}';assert (run/'training-complete.json').exists()
 tok=AutoTokenizer.from_pretrained(MODELS[a.model],local_files_only=True);tok.pad_token=tok.eos_token
 base=AutoModelForCausalLM.from_pretrained(MODELS[a.model],local_files_only=True,torch_dtype=torch.bfloat16,attn_implementation='sdpa',low_cpu_mem_usage=True).cuda();model=PeftModel.from_pretrained(base,run/'adapter').eval()
 modes=MODES if a.condition=='joint' else [a.condition];summary={}
 for mode in modes:
  for split in (['dev'] if a.calibration else ['test','independent']):
   rows=read(split);rows=rows[:16] if a.calibration else rows
   p=run/f'{"calibration" if a.calibration else "evaluation"}-{mode}-{split}.jsonl'
   summary[p.name]=evaluate(model,tok,rows,mode,p,a.batch_size)
 (run/('calibration-complete.json' if a.calibration else 'evaluation-complete.json')).write_text(json.dumps(summary,indent=2));print(json.dumps(summary),flush=True)
if __name__=='__main__':main()
