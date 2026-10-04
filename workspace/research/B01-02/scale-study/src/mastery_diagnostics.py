"""All fixed dev checkpoints, with exploratory threshold sensitivity (not preregistered)."""
from pathlib import Path
import json,hashlib,statistics
from audit import check
R=Path(__file__).resolve().parents[1];rows=[];hashes={};selected=[]
for model in ['qwen7b','qwen32b']:
 for c in ['flat','macro']:
  for seed in [11,22,33]:
   run=R/f'{model}/runs/{c}-original-s{seed}';curve=[]
   for step in [0,16,64,128,256,512]:
    p=run/f'step{step:04d}-dev.jsonl';raw=[json.loads(x) for x in p.read_text().splitlines()];assert len(raw)==224
    hashes[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
    short=[check(x) for x in raw if x['split']=='dev'];assert len(short)==128
    entry=dict(model=model,condition=c,seed=seed,step=step,n=128,accuracy=statistics.mean(x['accuracy'] for x in short),strict_trace=statistics.mean(x['strict_trace'] for x in short))
    curve.append(entry);rows.append(entry)
   for threshold in [.90,.95,.99]:
    chosen=next((x for x in curve if x['accuracy']>=threshold),None)
    selected.append(dict(model=model,condition=c,seed=seed,threshold=threshold,step=chosen['step'] if chosen else None,dev_accuracy=chosen['accuracy'] if chosen else None))
# Selection uses dev accuracy only; report all three exploratory thresholds transparently.
missing=[]
for item in selected:
 step=item['step']
 if step is None:continue
 run=R/f"{item['model']}/runs/{item['condition']}-original-s{item['seed']}"
 p=run/'predictions.jsonl' if step==512 else run/f'checkpoint-tests/step{step:04d}-predictions.jsonl'
 if not p.exists():missing.append(str(p.relative_to(R)));continue
 raw=[json.loads(line) for line in p.read_text().splitlines()]
 if len(raw)!=560:missing.append(str(p.relative_to(R)));continue
 hashes[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
 audited=[check(x) for x in raw if x['split']=='ood'];assert len(audited)==384
 item['ood']={metric:statistics.mean(x[metric] for x in audited) for metric in ['accuracy','strict_trace','correct_prefix_early_answer','exact_two_tools_early_answer','wrong_operation']}
contrasts=[]
for model in ['qwen7b','qwen32b']:
 for threshold in [.90,.95,.99]:
  subset=[x for x in selected if x['model']==model and x['threshold']==threshold]
  if not all('ood' in x for x in subset):continue
  for metric in ['accuracy','strict_trace','correct_prefix_early_answer']:
   diffs=[]
   for seed in [11,22,33]:
    pair={x['condition']:x for x in subset if x['seed']==seed}
    diffs.append(pair['macro']['ood'][metric]-pair['flat']['ood'][metric])
   mean=statistics.mean(diffs);margin=4.302652729911275*statistics.stdev(diffs)/(3**.5)
   contrasts.append(dict(model=model,threshold=threshold,metric=metric,direction='macro minus flat',seed_differences=diffs,mean=mean,seed_t95=[mean-margin,mean+margin]))
(R/'analysis/mastery-diagnostics.json').write_text(json.dumps(dict(status='Exploratory descriptive thresholds; no numeric threshold was preregistered. Selection uses dev only. All thresholds reported.',missing_test_files=sorted(set(missing)),paired_comparisons=contrasts,curves=rows,selected=selected,source_sha256=hashes),indent=2))
print('Audited 72 dev checkpoints, 9216 short-task outputs; no model training changed')
for m in ['qwen7b','qwen32b']:
 for c in ['flat','macro']:print(m,c,[(x['seed'],x['step']) for x in selected if x['model']==m and x['condition']==c and x['threshold']==.95])
