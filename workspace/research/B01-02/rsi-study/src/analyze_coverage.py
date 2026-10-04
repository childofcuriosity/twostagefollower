from common import *
import statistics,collections
import numpy as np
families={f['id']:f for f in load()};rows=[];primitive_rows=[]
for run in sorted((ROOT/'runs').glob('robust-*')):
 if not run.is_dir():continue
 meta=json.loads((run/'summary.json').read_text());a=meta['args']
 for line in (run/'proposals.jsonl').read_text().splitlines():
  r=json.loads(line)
  if r['style']!='instruction' or r['temperature']!=1.:continue
  cs=[x['candidate'] for x in r['proposals'][:16]]
  primitive_rows.append({**a,'family':r['family'],'proposal_contains_ends':statistics.mean('ends' in CANDIDATES[c] for c in cs),'length3_fraction':statistics.mean(len(CANDIDATES[c])==3 for c in cs),'unique_syntax':len(set(cs))})
for p in (ROOT/'runs').glob('coverage-*/summary.json'):
 meta=json.loads(p.read_text());seed=meta['seed']
 for line in (p.parent/'proposals.jsonl').read_text().splitlines():
  r=json.loads(line);f=families[r['family']]
  for k in [4,16,64]:
   cs=[x['candidate'] for x in r['proposals'][:k]];lib=select(f['support'],cs)
   rows.append(dict(seed=seed,family=f['id'],style=r['style'],temperature=r['temperature'],budget=k,selected=lib,compression=utility(f['test'],lib),proposal_contains_ends=statistics.mean('ends' in CANDIDATES[c] for c in cs)))
summary={}
for model in ['qwen1.5b','qwen3b','smol1.7b']:
 summary[model]={}
 for c in ['base','flat','macro']:
  rs=[r for r in primitive_rows if r['model']==model and r['condition']==c]
  summary[model][c]={k:statistics.mean(r[k] for r in rs) for k in ['proposal_contains_ends','length3_fraction','unique_syntax']}
coverage={};old=json.loads((ROOT/'analysis/robust-results.json').read_text());rs=[r for r in rows if r['style']=='instruction' and r['temperature']==1. and r['budget']==16]
if len(rs)==48:
 for setting in sorted({(r['style'],r['temperature'],r['budget']) for r in rows}):
  style,temp,k=setting;vs=[r for r in rows if (r['style'],r['temperature'],r['budget'])==setting];key=f'{style}-t{temp}-k{k}'
  coverage[key]=dict(compression=statistics.mean(r['compression'] for r in vs),contains_ends=statistics.mean(r['proposal_contains_ends'] for r in vs),seed_means=[statistics.mean(r['compression'] for r in vs if r['seed']==s) for s in [11,22,33]],base=old['summary']['qwen1.5b'][key]['base']['compression'],original_macro=old['summary']['qwen1.5b'][key]['macro']['compression'])
 original=[json.loads(line) for line in (ROOT/'analysis/robust-rows.jsonl').read_text().splitlines()]
 rng=np.random.default_rng(94207);indices=rng.integers(0,16,(5000,16))
 for key,value in coverage.items():
  dif=[]
  for seed in [11,22,33]:
   one=[]
   for fid in range(16,32):
    nv=next(x['compression'] for x in rows if x['seed']==seed and x['family']==fid and f"{x['style']}-t{x['temperature']}-k{x['budget']}"==key)
    ov=next(x['compression'] for x in original if x['model']=='qwen1.5b' and x['condition']=='macro' and x['seed']==seed and x['family']==fid and f"{x['style']}-t{x['temperature']}-k{x['budget']}"==key)
    one.append(nv-ov)
   dif.append(one)
  matrix=np.array(dif);boot=matrix.mean(axis=0)[indices].mean(axis=1)
  value['coverage_minus_original_macro']={'mean':float(matrix.mean()),'seed_differences':matrix.mean(axis=1).tolist(),'family_bootstrap_95':np.quantile(boot,[.025,.975]).tolist()}
 audit=[]
 for seed in [11,22,33]:
  new=json.loads((ROOT/f'coverage/runs/macro-original-s{seed}/summary.json').read_text());oldrun=json.loads((PARENT/f'runs/macro-original-s{seed}/summary.json').read_text());assert new['training']['counts']==oldrun['training']['counts']
  audit.append(dict(seed=seed,identical_training_counts=new['training']['counts'],new_execution=new['evaluation']['groups']))
else:audit=[]
baselines={}
for method in ['random','frequency','exhaustive']:
 values=[]
 for f in families.values():
  if f['split']!='test':continue
  for seed in [11,22,33]:
   if method=='random':cs=random.Random(seed*10000+f['id']).choices(range(252),k=16)
   elif method=='frequency':
    counts=collections.Counter(tuple(p[i:i+n]) for p in f['support'] for n in [2,3] for i in range(len(p)-n+1));cs=sorted(range(252),key=lambda c:(-counts[CANDIDATES[c]]*(len(CANDIDATES[c])-1),c))[:16]
   else:cs=list(range(252))
   values.append(dict(family=f['id'],seed=seed,compression=utility(f['test'],select(f['support'],cs))))
  baselines[method]=dict(mean=statistics.mean(r['compression'] for r in values),rows=values)
(ROOT/'analysis/coverage-rows.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows));(ROOT/'analysis/coverage-results.json').write_text(json.dumps(dict(posthoc=True,primitive_diagnostics=summary,coverage=coverage,matched_training_audit=audit,proposal_baselines=baselines),indent=2));print(json.dumps(dict(primitive_diagnostics=summary,coverage_main=coverage.get('instruction-t1.0-k16'),baselines={k:v['mean'] for k,v in baselines.items()}),indent=2))
