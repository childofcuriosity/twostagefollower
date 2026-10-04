"""Audit saved outputs without changing historical predictions or scores."""
import json,re
from pathlib import Path
from dsl import execute,expand
ROOT=Path(__file__).resolve().parents[1]
records=[]
for domain in ['', 'secondary']:
 for p in sorted((ROOT/domain/'runs').glob('*/predictions.jsonl')):
  result=dict(domain=domain or 'original',run=p.parent.name,n=0,strict_prediction_differences=0,false_positive_under_loose_parser=0,multiple_answer_lines=0)
  for line in p.open():
   r=json.loads(line)
   pattern=r'^Answer:[ \t]*([0-9](?:[ \t]+[0-9]){3})[ \t]*$' if not domain else r'^Answer:[ \t]*([ab](?:[ \t]+[ab]){2,7})[ \t]*$'
   m=re.findall(pattern,r['raw'],re.M)
   pred=(list(map(int,m[-1].split())) if not domain else ''.join(m[-1].split())) if m else None
   result['n']+=1
   result['strict_prediction_differences']+=pred!=r['prediction']
   result['false_positive_under_loose_parser']+=bool(r['correct'] and pred!=r['expected'])
   result['multiple_answer_lines']+=len(re.findall(r'^Answer:',r['raw'],re.M))>1
  records.append(result)
world=json.loads((ROOT/'data/worlds.json').read_text())['original']
routing=[]
for p in sorted((ROOT/'analysis/routing-probe').glob('*.jsonl')):
 n=0
 for line in p.open():
  r=json.loads(line);state=r['x']
  for i,call in enumerate(r['calls']):
   assert call['input']==state and call['position']==i and call['macro_index']==r['chain'][i]
   state=call['prediction']
  assert state==r['prediction']
  assert list(execute(r['x'],expand(r['chain'],world['library'])))==r['expected']
  assert r['correct']==(r['prediction']==r['expected'])
  n+=1
 routing.append(dict(run=p.stem,n=n,chain_inputs_and_truth='verified'))
assert not any(r['false_positive_under_loose_parser'] for r in records)
out={'runs':records,'routing':routing,'false_positive_total':0,'policy':'Last complete Answer line; historical raw outputs and scores preserved.'}
(ROOT/'analysis/parser-audit-final.json').write_text(json.dumps(out,indent=2))
print('Audited',len(records),'runs and',len(routing),'routing probes; no false positive score inflation')
