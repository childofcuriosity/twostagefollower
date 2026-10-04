import statistics,collections
import numpy as np
from common import *
rows=[];families={f['id']:f for f in load()}
for p in sorted((ROOT/'runs').glob('robust-*/summary.json')):
 meta=json.loads(p.read_text());a=meta['args']
 for line in (p.parent/'proposals.jsonl').read_text().splitlines():
  record=json.loads(line);f=families[record['family']]
  for k in [4,16,64]:
   candidates=[r['candidate'] for r in record['proposals'][:k]];lib=select(f['support'],candidates);freq=collections.Counter(sig(CANDIDATES[c]) for c in candidates);q=np.array(list(freq.values()))/k
   rows.append(dict(model=a['model'],condition=a['condition'],seed=a['seed'],family=f['id'],style=record['style'],temperature=record['temperature'],budget=k,selected=lib,compression=utility(f['test'],lib),unique_semantics=len(freq),empirical_entropy=float(-(q*np.log(q)).sum()),selected_count=len(lib)))
(ROOT/'analysis/robust-rows.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
summary={};comparisons={};rng=np.random.default_rng(937411);indices=rng.integers(0,16,(5000,16))
for model in sorted({r['model'] for r in rows}):
 summary[model]={};comparisons[model]={}
 for style,temp in [('instruction',1.),('concise',1.),('fewshot',1.),('instruction',1.5)]:
  for k in [4,16,64]:
   key=f'{style}-t{temp}-k{k}';summary[model][key]={};comparisons[model][key]={}
   by={}
   for c in ['base','flat','macro']:
    rs=[r for r in rows if r['model']==model and r['style']==style and r['temperature']==temp and r['budget']==k and r['condition']==c]
    if len(rs)!=48:continue
    summary[model][key][c]={field:statistics.mean(r[field] for r in rs) for field in ['compression','unique_semantics','empirical_entropy','selected_count']}
    by[c]=np.array([[next(r['compression'] for r in rs if r['seed']==s and r['family']==f) for f in range(16,32)] for s in [11,22,33]])
   for c in ['flat','macro']:
    if c not in by or 'base' not in by:continue
    dif=by[c]-by['base'];means=dif.mean(axis=0);boot=means[indices].mean(axis=1)
    comparisons[model][key][c+'-base']=dict(mean=float(dif.mean()),seed_differences=dif.mean(axis=1).tolist(),family_differences=means.tolist(),family_bootstrap_95=np.quantile(boot,[.025,.975]).tolist())
result=dict(completed_runs=len(list((ROOT/'runs').glob('robust-*/summary.json'))),expected_runs=27,summary=summary,comparisons=comparisons)
(ROOT/'analysis/robust-results.json').write_text(json.dumps(result,indent=2));print('Robust completed',result['completed_runs'],'of 27')
for model in summary:
 print(model,'main',summary[model].get('instruction-t1.0-k16'),flush=True)
 print(model,'fewshot k64',summary[model].get('fewshot-t1.0-k64'),flush=True)
