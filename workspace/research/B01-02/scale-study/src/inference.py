# Deliberately not imported as stdlib statistics; executed as script.
import json,csv,sys,collections,hashlib
from pathlib import Path
import numpy as np
from scipy.stats import t
from audit import check
R=Path(__file__).resolve().parents[1]
rs=[json.loads(l) for l in (R/'analysis/final-case-audit.jsonl').read_text().splitlines()]
metrics=['accuracy','strict_trace','correct_prefix_early_answer','exact_two_tools_early_answer','two_output_segments']
def contrasts(rows,split,model):
 sub=[r for r in rows if r['split']==split and r['model']==model];lookup={(r['seed'],r['condition'],r['id']):r for r in sub};seeds=sorted({r['seed'] for r in sub});chains=sorted({tuple(r['chain']) for r in sub})
 if len(seeds)!=3:return None
 rng=np.random.default_rng(20260924);result={}
 for metric in metrics:
  a=np.empty((3,len(chains)))
  for j,seed in enumerate(seeds):
   for k,chain in enumerate(chains):
    group=[r for r in sub if r['seed']==seed and r['condition']=='flat' and tuple(r['chain'])==chain]
    vals=[lookup[(seed,'macro',r['id'])][metric]-r[metric] for r in group];assert vals;a[j,k]=np.mean(vals)
  sd=a.mean(axis=1);sem=sd.std(ddof=1)/np.sqrt(3);margin=float(t.ppf(.975,2)*sem)
  # Program-cluster bootstrap averages all three observed training seeds; separate seed t interval.
  boot=np.array([a[:,rng.integers(0,len(chains),len(chains))].mean() for _ in range(5000)])
  result[metric]=dict(mean=float(a.mean()),seed_differences=sd.tolist(),seed_t95=[float(sd.mean()-margin),float(sd.mean()+margin)],program_bootstrap95=np.quantile(boot,[.025,.975]).tolist(),program_clusters=len(chains))
 return result
paired={}
for model in ['qwen1.5b','qwen3b','qwen7b','qwen32b']:
 paired[model]={split:contrasts(rs,split,model) for split in ['iid','ood','pressure']}
(R/'analysis/paired-inference.json').write_text(json.dumps({'direction':'macro minus flat; negative early-answer difference means macro less early stopping','seed_interval':'3 training seeds, t df2; wide intervals expected','program_interval':'paired bootstrap over exact program chains, averaging observed seeds; conditional on these seeds','comparisons':paired},indent=2))
ext=[];frozen=[];manifest={}
for model in paired:
 for p in (R/'extended'/model).glob('*.jsonl'):
  records=[json.loads(l) for l in p.read_text().splitlines()];assert len(records)==480
  manifest[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
  for row in records:
   item=check(row)|{'model':model,'tag':p.stem}
   if p.stem.startswith('frozen'):frozen.append(item)
   else:
    condition,seed=p.stem.split('-s');ext.append(item|{'condition':condition,'seed':int(seed)})
exstats={};summaries=[]
for model in paired:
 exstats[model]={split:contrasts(ext,split,model) for split in ['length3','length4','length5','length6','length8']}
 for condition in ['flat','macro','frozen']:
  source=frozen if condition=='frozen' else [r for r in ext if r['condition']==condition]
  for split in ['length3','length4','length5','length6','length8']:
   group=[r for r in source if r['model']==model and r['split']==split]
   if group:summaries.append(dict(model=model,condition=condition,split=split,n=len(group),**{m:float(np.mean([r[m] for r in group])) for m in metrics}))
(R/'analysis/extended-results.json').write_text(json.dumps({'records_checked':len(ext)+len(frozen),'training_rows':len(ext),'frozen_rows':len(frozen),'summary':summaries,'paired_inference':exstats,'manifest':manifest,'frozen_condition':'full tool definitions provided; not comparable as same-prompt original no-definition task'},indent=2))
(R/'analysis/extended-case-audit.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in ext+frozen))
print('Paired program/seed intervals and extended audits complete',len(ext)+len(frozen),flush=True)
