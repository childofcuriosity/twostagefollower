"""Classify observed failures, without changing scores or excluding cases."""
import collections,json,random
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def main():
 counts=collections.defaultdict(collections.Counter);examples=collections.defaultdict(list);cost=[]
 for run in sorted((R/'runs').iterdir()):
  tr=run/'training-complete.json'
  if run.name.endswith('-probe') or not tr.exists():continue
  t=json.loads(tr.read_text());ev=run/'evaluation-complete.json';e=json.loads(ev.read_text()) if ev.exists() else {}
  cost.append(dict(run=run.name,training_seconds=t['train_seconds'],training_total_seconds=t['total_seconds'],evaluation_seconds=sum(x['seconds'] for x in e.values()),counts=t['counts'],evaluation_finished=ev.exists(),peak_memory_bytes=t['peak_memory_bytes']))
  for p in sorted(run.glob('evaluation-*.jsonl')):
   for line in p.read_text().splitlines():
    try:r=json.loads(line)
    except json.JSONDecodeError:continue
    key=(t['config']['args']['model'],t['config']['args']['condition'],r['mode'],r['split']);c=counts[key];c['n']+=1
    if r['grade']['complete']:c['complete']+=1;continue
    tools=[x['tool'] for x in r['calls']];wanted=r['chain'];firstwrong=next((i for i,(x,y) in enumerate(zip(tools,wanted)) if x!=y),None)
    if r['stop'] not in ['done','oracle_done']:category=r['stop']
    elif firstwrong is not None:category='wrong_tool_choice'
    elif len(tools)<len(wanted):category='early_done_correct_name_prefix'
    elif len(tools)>len(wanted):category='extra_tools'
    elif any(not x.get('body',{}).get('ops_ok',False) for x in r['calls']):category='wrong_or_incomplete_primitive_sequence'
    elif any(not x.get('body',{}).get('numeric_ok',False) for x in r['calls']):category='numeric_error'
    else:category='other'
    c[category]+=1;examples[key+(category,)].append(dict(source=str(p.relative_to(R)),id=r['id'],first_wrong_name_position=firstwrong,requested=wanted,emitted=tools,stop=r['stop']))
 rng=random.Random(20260925);samples=[]
 for key,rs in sorted(examples.items()):samples.append(dict(group=key,n=len(rs),random_examples=rng.sample(rs,min(3,len(rs)))))
 (R/'analysis/failure-diagnostics.json').write_text(json.dumps(dict(counts=[dict(group=k,counts=dict(v)) for k,v in counts.items()],samples=samples),indent=2))
 (R/'analysis/cost.json').write_text(json.dumps(dict(runs=cost,training_total_gpu_hours=sum(x['training_total_seconds'] for x in cost)/3600,evaluation_excluding_loading_gpu_hours=sum(x['evaluation_seconds'] for x in cost)/3600,note='Per-process wall time on one GPU; includes training load/checkpoint overhead, evaluation load excluded. Not GPU-core active time; probe costs separate.'),indent=2));print('Failure categories and cost recorded')
if __name__=='__main__':main()
