import json
from evaluate import Session,Boundary
from protocol import *
from transformers import AutoTokenizer
import torch
tok=AutoTokenizer.from_pretrained(MODELS['qwen1.5b'],local_files_only=True);tok.pad_token=tok.eos_token
row=read('train')[0];checks=[]
for mode in MODES:
 s=Session(row,tok,mode)
 while s.stop is None:
  s.advance_oracle()
  if s.stop:break
  if s.phase=='header':text=NAMES[row['chain'][len(s.calls)]]+':\n' if len(s.calls)<len(row['chain']) else 'Done\n'
  else:text=body(s.calls[-1]['tool'],s.state)[0]
  s.accept(tok.encode(text,add_special_tokens=False))
 assert s.finish()['grade']['complete'];checks.append(mode+'_reference_pass')
# Wrong chosen tool is executed, not replaced by the requested tool.
s=Session(row,tok,'operation_oracle');wrong=(row['chain'][0]+1)%9;s.accept(tok.encode(NAMES[wrong]+':\n',add_special_tokens=False));s.advance_oracle()
assert s.state==dsl.execute(row['x'],LIB[wrong]) and s.calls[0]['tool']==wrong
s.accept(tok.encode('Done\n',add_special_tokens=False));assert not s.finish()['grade']['sequence_correct'];checks.append('wrong_name_not_corrected_and_early_done_allowed')
# Wrong stated numeric result is retained and handed to next oracle-selected tool.
s=Session(row,tok,'order_oracle');s.advance_oracle();s.accept(tok.encode('inc 9 9 9 9\nEndTool\n',add_special_tokens=False));assert s.state==(9,9,9,9);s.advance_oracle();assert s.calls[-1]['input_state']==[9,9,9,9];checks.append('wrong_state_preserved')
# Incomplete segment is failure, not silently completed by program.
s=Session(row,tok,'order_oracle');s.advance_oracle();s.accept(tok.encode('rot 1 2 3 4\n',add_special_tokens=False));assert s.stop and not s.finish()['grade']['complete'];checks.append('missing_boundary_fails')
# Differing completion boundaries per batch item yield per-item masks.
prefix=tok.encode('Trace:\n',add_special_tokens=False);seq=[tok.encode('red:\n',add_special_tokens=False),tok.encode('red',add_special_tokens=False)];n=max(map(len,seq));ids=torch.tensor([prefix+x+[tok.eos_token_id]*(n-len(x)) for x in seq]);assert Boundary(tok,len(prefix),'header')(ids,None).tolist()==[True,False];checks.append('batched_boundary_mask')
(R/'analysis/controller-preflight.json').write_text(json.dumps({'checks':checks},indent=2));print(checks)
# Exercise the complete batched scheduler, including oracle transitions between phases.
from evaluate import evaluate
import re
class FakeModel:
 device='cpu'
 def generate(self,input_ids,attention_mask,stopping_criteria,**kwargs):
  phase=stopping_criteria[0].phase;outputs=[]
  for ids in input_ids:
   text=tok.decode(ids.tolist(),skip_special_tokens=True);chain=re.search(r'^Functions: (.*)$',text,re.M)[1].split();trace=text.split('Trace:\n',1)[1];headers=re.findall(r'^([a-z]+):$',trace,re.M)
   if phase=='header':suffix=(chain[len(headers)]+':\n') if len(headers)<len(chain) else 'Done\n'
   else:
    tool=IDX[headers[-1]];states=re.findall(r'^(?:rev|rot|inc|neg|swap|ends) ([0-9] [0-9] [0-9] [0-9])$',trace,re.M)
    state=list(map(int,(states[-1] if states else re.search(r'^Input: (.*)$',text,re.M)[1]).split()));suffix=body(tool,state)[0]
   outputs.append(tok.encode(suffix,add_special_tokens=False))
  n=max(map(len,outputs));new=torch.tensor([x+[tok.eos_token_id]*(n-len(x)) for x in outputs]);return torch.cat([input_ids,new],dim=1)
for mode in MODES:
 p=R/'analysis'/f'mock-scheduler-{mode}.jsonl'
 result=evaluate(FakeModel(),tok,read('test')[:8],mode,p,batch_size=8);assert result['complete']==8,result
 checks.append(mode+'_batched_scheduler_pass')
(R/'analysis/controller-preflight.json').write_text(json.dumps({'checks':checks,'mock_inference_only':True},indent=2))
print('Complete scheduler checks passed')
