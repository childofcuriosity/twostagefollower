import json,csv,math,collections,hashlib,time,re
from pathlib import Path
import numpy as np
from scipy.stats import t
from dsl import expand
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'analysis'
summaries={p.parent.name:json.loads(p.read_text()) for p in (ROOT/'runs').glob('*/summary.json') if 'calibration' not in p.parent.name}
raw={name:[json.loads(s) for s in (ROOT/'runs'/name/'predictions.jsonl').read_text().splitlines()] for name in summaries}
rows=[]
for name,preds in raw.items():
 for split in ['iid','ood','pressure']:
  for depth in ([None,3,4,5] if split=='ood' else [None]):
   rs=[r for r in preds if r['split']==split and (depth is None or r['depth']==depth)]
   if not rs:continue
   rows.append(dict(run=name,split=split,depth=depth,n=len(rs),correct=sum(r['correct'] for r in rs),accuracy=np.mean([r['correct'] for r in rs]),program_accuracy=np.mean([r['primitive_sequence_correct'] for r in rs]),valid_execution=np.mean([r['execution_steps_correct'] for r in rs]),malformed=sum(r['prediction'] is None for r in rs)))
with (out/'metrics.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else ['run']);w.writeheader();w.writerows(rows)
comparisons={}
for cond in ['macro','shuffled','natural']:
 diffs=[];task_diffs=[]
 for seed in [11,22,33]:
  a=f'{cond}-original-s{seed}';b=f'flat-original-s{seed}'
  if a not in raw or b not in raw:continue
  ra={r['id']:r for r in raw[a] if r['split']=='ood'};rb={r['id']:r for r in raw[b] if r['split']=='ood'}
  assert ra.keys()==rb.keys()
  d=np.array([int(ra[i]['correct'])-int(rb[i]['correct']) for i in sorted(ra)])
  diffs.append(float(d.mean()));task_diffs.append(d)
 if diffs:
  mean=float(np.mean(diffs));se=float(np.std(diffs,ddof=1)/math.sqrt(len(diffs))) if len(diffs)>1 else None
  ci=None if se is None or se==0 else [mean-float(t.ppf(.975,len(diffs)-1))*se,mean+float(t.ppf(.975,len(diffs)-1))*se]
  boot=None
  if task_diffs:
   d=np.mean(task_diffs,axis=0)
   clusters=collections.defaultdict(list)
   for ident,value in zip(sorted(ra),d):clusters[tuple(ra[ident]['chain'])].append(value)
   d=np.array([np.mean(values) for values in clusters.values()])
   rng=np.random.default_rng(90);vals=np.array([rng.choice(d,size=len(d),replace=True).mean() for _ in range(2000)])
   boot=np.quantile(vals,[.025,.975]).tolist()
  comparisons[cond+'-vs-flat']={'seed_differences':diffs,'mean_difference':mean,'seed_t_interval_95':ci,'descriptive_ast_bootstrap_95':boot,'n_seeds':len(diffs),'passes_screen':len(diffs)==3 and mean>=.03 and all(d>0 for d in diffs),'warning':'n=3; AST interval conditional on trained checkpoints; zero-variance t interval omitted.'}
cf={}
for name,preds in raw.items():
 if '-semantic-' in name:
  rs=[r for r in preds if r['expected']!=r['old_world_answer']]
  cf[name]={'changed_targets':len(rs),'new_semantics_accuracy':sum(r['correct'] for r in rs)/max(1,len(rs)),'old_semantics_match':sum(r['matches_old_world'] for r in rs)/max(1,len(rs))}
renaming={}
for split in ['iid','ood','pressure']:
 differences=[]
 for seed in [11,22,33]:
  a=f'macro-renamed-s{seed}';b=f'macro-original-s{seed}'
  if a not in raw or b not in raw:continue
  ra={r['id']:r for r in raw[a] if r['split']==split};rb={r['id']:r for r in raw[b] if r['split']==split}
  assert ra.keys()==rb.keys()
  differences.append(float(np.mean([int(ra[i]['correct'])-int(rb[i]['correct']) for i in ra])))
 renaming[split]={'paired_seed_differences':differences,'mean':float(np.mean(differences)) if differences else None}
failures={};worlds=json.loads((ROOT/'data/worlds.json').read_text())
for name,preds in raw.items():
 counts=collections.Counter();lib=worlds[summaries[name]['args']['world']]['library']
 for r in preds:
  if r['split']!='ood' or r['correct']:continue
  ops=re.findall(r'\b(rev|rot|inc|neg|swap|ends)\s+\d\s+\d\s+\d\s+\d',r['raw'])
  expected=list(expand(r['chain'],lib))
  if r['prediction'] is None:key='missing_final_answer'
  elif ops and len(ops)<len(expected) and ops==expected[:len(ops)]:key='correct_prefix_but_stopped_early'
  elif not r['primitive_sequence_correct']:key='wrong_or_extra_primitive_sequence'
  elif not r['execution_steps_correct']:key='execution_error_with_correct_program'
  else:key='final_answer_error_after_correct_trace'
  counts[key]+=1
 failures[name]=dict(counts)
report={'completed_runs':len(summaries),'runs':list(summaries),'primary_comparisons':comparisons,'semantic_interventions':cf,'name_interventions':renaming,'ood_failure_categories':failures,'measured_run_gpu_hours':sum(s['gpu_hours'] for s in summaries.values()),'note':'Run GPU hours include run walltime after model load; installation, downloads, discovery and model-load time reported separately, not silently equated with all experiment costs.'}
(out/'results.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
