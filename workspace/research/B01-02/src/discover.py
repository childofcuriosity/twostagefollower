import json,random,time,collections,itertools
from pathlib import Path
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM,set_seed
from dsl import OPS,parse,execute,signature,digits
ROOT=Path(__file__).resolve().parents[1]
started=time.time();set_seed(710);rng=random.Random(710)
tok=AutoTokenizer.from_pretrained(ROOT/'model',local_files_only=True);tok.padding_side='left';tok.pad_token=tok.eos_token
model=AutoModelForCausalLM.from_pretrained(ROOT/'model',torch_dtype=torch.bfloat16,attn_implementation='sdpa',local_files_only=True).cuda().eval()
def generate(prompts):
 out=[]
 for i in range(0,len(prompts),24):
  ins=tok(prompts[i:i+24],return_tensors='pt',padding=True).to('cuda')
  with torch.inference_mode():z=model.generate(**ins,max_new_tokens=28,do_sample=True,temperature=.85,top_p=.95,pad_token_id=tok.pad_token_id)
  out+=tok.batch_decode(z[:,ins.input_ids.shape[1]:],skip_special_tokens=True)
 return out
rules='Operations on four digits: rev reverses; rot rotates left; inc adds 1 mod 10 to all; neg negates mod 10; swap swaps first two; ends adds 1 mod 10 to first and last. Use only these words separated by commas.\n'
examples='Input 1 2 3 4 -> Output 5 4 3 2\nProgram: rev,inc\nInput 1 2 3 4 -> Output 3 2 4 1\nProgram: rot,swap\n'
rows=[];prompts=[]
for i in range(128):
 x=tuple(rng.randrange(10) for _ in range(4));ops=tuple(rng.choices(OPS,k=rng.choice([2,3])));y=execute(x,ops)
 p=rules+examples+f'Input {digits(x)} -> Output {digits(y)}\nProgram:'
 rows.append({'id':i,'input':x,'output':y,'oracle_program':ops,'prompt':p});prompts.append(p)
for r,text in zip(rows,generate(prompts)):
 r['raw']=text;p=parse(text);r['parsed']=p;r['success']=p is not None and execute(r['input'],p)==tuple(r['output'])
(ROOT/'data/discovery-traces.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
# Ask the same model to propose reusable functions from its own scored traces.
proposals=[];pp=[]
for i in range(160):
 subset=rng.sample(rows,8)
 history='\n'.join(f"Program {','.join(r['parsed']) if r['parsed'] else 'INVALID'}; success={r['success']}" for r in subset)
 p=rules+'Your previous attempts:\n'+history+'\nPropose one reusable subprogram of exactly two or three operations. No explanation.\nReusable program:'
 proposals.append({'id':i,'prompt':p});pp.append(p)
counts=collections.Counter()
for r in rows:
 if r['parsed']:
  for n in [2,3]:
   for j in range(len(r['parsed'])-n+1):counts[r['parsed'][j:j+n]]+=1
valid={};allprops=generate(pp)
for r,text in zip(proposals,allprops):
 r['raw']=text;p=parse(text);r['parsed']=p
 r['valid']=p is not None and len(p) in (2,3)
 if r['valid']:
  # Exhaustively execute all 10^4 inputs: totality/range; no equivalence oracle claim.
  good=all(len(y:=execute(x,p))==4 and all(0<=a<=9 for a in y) for x in itertools.product(range(10),repeat=4))
  r['exhaustive_totality']=good
  if good and signature(p)!=signature(()):
   score=counts[p]*(len(p)-1)-len(p)
   sig=signature(p)
   if sig not in valid or score>valid[sig]['compression_score']:valid[sig]={'ops':p,'compression_score':score,'proposal_id':r['id'],'count_in_traces':counts[p]}
(ROOT/'data/proposals.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in proposals))
selected=sorted(valid.values(),key=lambda r:(-r['compression_score'],r['ops']))[:20]
report={'model':'Qwen2.5-1.5B','seed':710,'solver_attempts':len(rows),'solver_successes':sum(r['success'] for r in rows),'proposal_attempts':len(proposals),'valid_proposals':sum(r['valid'] for r in proposals),'unique_nonidentity_semantics':len(valid),'selected':selected,'wall_seconds':time.time()-started,'note':'Selection from actual model proposals; executable totality is not a proof of utility. Negative compression scores are retained transparently for mechanism testing.'}
(ROOT/'data/library.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if len(selected)<6:raise RuntimeError('Too few model-proposed abstractions; do not substitute human macros')
