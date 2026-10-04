"""Compare step0 and step512 using exactly the same prompt information.
Never compare a definition-provided baseline to a definition-free final run.
"""
from pathlib import Path
import json, hashlib, statistics
from audit import check
R=Path(__file__).resolve().parents[1]
METRICS=['accuracy','strict_trace','exact_two_tools_early_answer','correct_prefix_early_answer','budget_hit']
def main():
 summaries=[];hashes={};frozen_reference={};n=0
 for model in ['qwen7b','qwen32b']:
  for context in ['no_definitions','definitions']:
   initial='step0000-predictions.jsonl' if context=='no_definitions' else 'step0000-with-library.jsonl'
   final='predictions.jsonl' if context=='no_definitions' else 'predictions-with-library.jsonl'
   for condition in ['flat','macro']:
    for seed in [11,22,33]:
     run=R/f'{model}/runs/{condition}-original-s{seed}'
     paths=[run/'checkpoint-tests'/initial,run/final]
     raw=[]
     for p in paths:
      hashes[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
      records=[json.loads(l) for l in p.read_text().splitlines()]
      assert len(records)==560 and len({x['id'] for x in records})==560
      raw.append({x['id']:x for x in records});n+=len(records)
     assert raw[0].keys()==raw[1].keys()
     fingerprint={i:x['raw'] for i,x in raw[0].items()}
     key=(model,context)
     if key in frozen_reference:assert frozen_reference[key]==fingerprint,(key,'frozen outputs differ across seeds/conditions')
     else:frozen_reference[key]=fingerprint
     pairs=[]
     for i in raw[0]:
      a,b=raw[0][i],raw[1][i]
      assert all(a[k]==b[k] for k in ['chain','x','expected','split'])
      pairs.append((check(a),check(b)))
     for split in ['iid','ood','pressure']:
      subset=[(a,b) for a,b in pairs if a['split']==split]
      values={}
      for metric in METRICS:
       before=statistics.mean(a[metric] for a,b in subset);after=statistics.mean(b[metric] for a,b in subset)
       values[metric]=dict(before=before,after=after,delta=after-before,zero_to_one=sum(a[metric]==0 and b[metric]==1 for a,b in subset),one_to_zero=sum(a[metric]==1 and b[metric]==0 for a,b in subset))
      summaries.append(dict(model=model,context=context,condition=condition,seed=seed,split=split,n=len(subset),metrics=values))
 assert n==26880 and len(summaries)==72
 out=dict(records_checked=n,summary=summaries,source_sha256=hashes,notes='Matched prompt information and question IDs. Frozen outputs verified identical across seeds and label conditions; these are repeated measurements, not independent baseline replicates. Changes do not establish general capability loss or prior protection.')
 (R/'analysis/matched-context.json').write_text(json.dumps(out,indent=2))
 print('Matched-context baseline/final comparison verified:',n,'records')
if __name__=='__main__':main()
