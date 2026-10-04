from common import *
import statistics
import numpy as np
rows=[]
for p in (ROOT/'runs').glob('length-*/summary.json'):
 a=json.loads(p.read_text())['args']
 for line in (p.parent/'proposals.jsonl').read_text().splitlines():
  r=json.loads(line);rows.append({**a,'family':r['family'],'compression':r['compression']})
summary={};comparisons={};rng=np.random.default_rng(93321);indices=rng.integers(0,16,(5000,16))
for m in ['qwen1.5b','qwen3b','smol1.7b']:
 summary[m]={};comparisons[m]={}
 for c in ['base','flat','macro']:
  rs=[r for r in rows if r['model']==m and r['condition']==c];assert len(rs)==48
  summary[m][c]={'mean':statistics.mean(r['compression'] for r in rs),'seed_means':[statistics.mean(r['compression'] for r in rs if r['seed']==s) for s in [11,22,33]]}
 for c in ['flat','macro']:
  matrix=[]
  for s in [11,22,33]:
   matrix.append([next(r['compression'] for r in rows if r['model']==m and r['condition']==c and r['seed']==s and r['family']==f)-next(r['compression'] for r in rows if r['model']==m and r['condition']=='base' and r['seed']==s and r['family']==f) for f in range(16,32)])
  values=np.array(matrix);boot=values.mean(axis=0)[indices].mean(axis=1)
  comparisons[m][c+'-base']=dict(mean=float(values.mean()),seed_differences=values.mean(axis=1).tolist(),family_bootstrap_95=np.quantile(boot,[.025,.975]).tolist())
(ROOT/'analysis/length-results.json').write_text(json.dumps(dict(posthoc=True,summary=summary,comparisons=comparisons),indent=2));print(json.dumps(summary,indent=2))
