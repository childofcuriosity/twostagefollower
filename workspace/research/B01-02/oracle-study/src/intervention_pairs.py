"""Same jointly trained checkpoint under two oracle interventions vs autonomous execution."""
import collections,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
out=[];examples=[];exceptions=[]
for run in sorted((R/'runs').glob('*-joint-s*')):
 if not (run/'evaluation-complete.json').exists():continue
 cfg=json.loads((run/'config.json').read_text())['args']
 for split in ['test','independent']:
  base={r['id']:r for r in map(json.loads,(run/f'evaluation-joint-{split}.jsonl').read_text().splitlines())}
  for mode in ['order_oracle','operation_oracle']:
   counts=collections.defaultdict(collections.Counter)
   for row in map(json.loads,(run/f'evaluation-{mode}-{split}.jsonl').read_text().splitlines()):
    ref=base[row['id']];c=counts[row['split'],len(row['chain'])];c['n']+=1
    before=ref['grade'];after=row['grade']
    for metric in ['complete','sequence_correct','all_expansions_correct']:
     c[metric+'_gain']+=int(not before[metric] and after[metric]);c[metric+'_loss']+=int(before[metric] and not after[metric])
    first=None
    for i,(a,b) in enumerate(zip(ref['events'],row['events'])):
     if a['token_ids']!=b['token_ids']:
      first=dict(index=i,base_phase=a['phase'],oracle_phase=b['phase'],prefix_identical=a['prefix_sha256']==b['prefix_sha256'],base_text=a['text'],oracle_text=b['text']);break
    if first is None:
     c['identical_tokens_through_shared_events']+=1
    else:
     expected='header' if mode=='order_oracle' else 'body'
     valid=first['prefix_identical'] and first['oracle_phase']==expected and first['base_phase']==expected
     c['first_difference_at_expected_intervention' if valid else 'first_difference_elsewhere']+=1
     if not valid:exceptions.append(dict(run=run.name,mode=mode,split=split,id=row['id'],first_difference=first,base_stop=ref['stop'],oracle_stop=row['stop'],base_complete=before['complete'],oracle_complete=after['complete']))
     if after['complete'] and not before['complete'] and sum(e['run']==run.name and e['mode']==mode and e['split']==split for e in examples)<3:examples.append(dict(run=run.name,mode=mode,split=split,id=row['id'],first_difference=first,base_stop=ref['stop'],oracle_stop=row['stop']))
   for (s,L),v in counts.items():out.append(dict(model=cfg['model'],seed=cfg['seed'],mode=mode,split=s,length=L,counts=dict(v)))
(R/'analysis/intervention-pairs.json').write_text(json.dumps(dict(results=out,examples=examples,exceptions=exceptions,exception_summary=dict(n=len(exceptions),complete_gains=sum(not e['base_complete'] and e['oracle_complete'] for e in exceptions),complete_losses=sum(e['base_complete'] and not e['oracle_complete'] for e in exceptions),by_model=dict(collections.Counter(e['run'].split('-')[0] for e in exceptions))),note='Same adapter, task and budgets; first differing token event classified. Any divergence before expected oracle content replacement is not claimed as clean token intervention. Identical shared events may end with different truncation/stop source and are separate.'),indent=2));print('Paired oracle intervention cells:',len(out))
