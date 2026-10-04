"""Independent raw-trajectory replay and source attribution audit; no GPU needed."""
import collections,hashlib,json,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R.parent
world=json.loads((P/'data/worlds.json').read_text())['original'];lib=world['library'];names=world['names'];idx={n:i for i,n in enumerate(names)}
def apply(x,op):
 a,b,c,d=x
 return {'rev':lambda:(d,c,b,a),'rot':lambda:(b,c,d,a),'inc':lambda:tuple((v+1)%10 for v in x),'neg':lambda:tuple(-v%10 for v in x),'swap':lambda:(b,a,c,d),'ends':lambda:((a+1)%10,b,c,(d+1)%10)}[op]()
def oracle_body(x,tool):
 lines=[]
 for op in lib[tool]:x=apply(x,op);lines.append(op+' '+' '.join(map(str,x))+'\n')
 return ''.join(lines)+'EndTool\n',x

def audit(row):
 state=tuple(row['x']);calls=[];expected_phase='header';generated=0;program=0;done=False
 for e in row['events']:
  phase=e['phase'];raw=e['text'];source=e['source'];generated+=len(e['token_ids']) if source=='model' else 0;program+=len(e['token_ids']) if source=='oracle' else 0
  if phase=='finish':assert source=='oracle' and row['mode']=='order_oracle' and raw=='Done\n' and len(calls)==len(row['chain']);done=True;continue
  if phase=='header':
   assert expected_phase=='header'
   if row['mode']=='order_oracle':assert source=='oracle' and raw==names[row['chain'][len(calls)]]+':\n'
   else:assert source=='model'
   if raw=='Done\n':done=True;continue
   m=re.fullmatch(r'([a-z]+):\n',raw)
   if not m or m[1] not in idx:assert row['stop'] in ['eos_or_protocol_error','protocol_or_fragment_budget'];continue
   if len(calls)>=16:assert row['stop']=='call_budget';continue
   calls.append({'tool':idx[m[1]],'correct':False});expected_phase='body'
  elif phase=='body':
   assert expected_phase=='body' and calls
   tool=calls[-1]['tool']
   if row['mode']=='operation_oracle':assert source=='oracle' and raw==oracle_body(state,tool)[0]
   else:assert source=='model'
   if not raw.endswith('EndTool\n'):assert row['stop'] in ['eos_or_protocol_error','protocol_or_fragment_budget'];continue
   ops=[];numeric=True;valid=True;new=state
   for line in raw[:-8].splitlines():
    m=re.fullmatch(r'(rev|rot|inc|neg|swap|ends) ([0-9]) ([0-9]) ([0-9]) ([0-9])',line)
    if not m:valid=False;break
    op=m[1];y=tuple(map(int,m.groups()[1:]));numeric &= y==apply(new,op);new=y;ops.append(op)
   if not valid:assert row['stop'] in ['eos_or_protocol_error','protocol_or_fragment_budget'];continue
   state=new;calls[-1]['correct']=bool(numeric and ops==lib[tool]);expected_phase='header'
 assert generated==row['generated_tokens'];seq=[c['tool'] for c in calls]==row['chain'] and done;allb=bool(calls) and all(c['correct'] for c in calls)
 truth=tuple(row['x'])
 for tool in row['chain']:
  for op in lib[tool]:truth=apply(truth,op)
 complete=seq and allb and state==truth
 assert (seq,allb,complete)==tuple(row['grade'][k] for k in ['sequence_correct','all_expansions_correct','complete']),(row['id'],row['mode'],row['grade'],calls)
 return generated,program

def main():
 counts=collections.defaultdict(collections.Counter);hashes={};n=0
 for run in sorted((R/'runs').iterdir()):
  if not (run/'training-complete.json').exists() or run.name.endswith('-probe'):continue
  model,condition,seed=re.fullmatch(r'(qwen[^-]+)-(joint|order_oracle|operation_oracle)-s(\d+)',run.name).groups()
  for p in sorted(run.glob('evaluation-*.jsonl')):
   data=p.read_bytes();hashes[str(p.relative_to(R))]=hashlib.sha256(data).hexdigest()
   # A currently writing file may end mid-line; skip only its unfinished last record.
   for line in data.splitlines():
    try:row=json.loads(line)
    except json.JSONDecodeError:
     if not (run/'evaluation-complete.json').exists():continue
     raise
    gen,prog=audit(row);n+=1;key=(model,condition,int(seed),row['mode'],row['split'],len(row['chain']));c=counts[key];c['n']+=1
    for metric in ['complete','sequence_correct','all_expansions_correct','local_correct','requested','emitted']:c[metric]+=row['grade'][metric]
    c['model_tokens']+=gen;c['oracle_tokens']+=prog;c['stop:'+row['stop']]+=1
 results=[dict(model=k[0],condition=k[1],seed=k[2],mode=k[3],split=k[4],length=k[5],counts=dict(v)) for k,v in counts.items()]
 out=dict(records=n,source_hashes=hashes,results=results,scope='Independent primitive/state and provenance replay. Partial files explicitly allowed for interim use; completion gate separate.')
 (R/'analysis/results-audit.json').write_text(json.dumps(out,indent=2));print('Audited',n,'trajectories')
if __name__=='__main__':main()
