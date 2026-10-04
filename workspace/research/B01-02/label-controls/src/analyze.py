from common import *
from grading import grade
import collections,time,numpy as np
jobs=json.loads((R/'analysis/jobs.json').read_text());pre=json.loads((R/'analysis/preflight.json').read_text())

launch=json.loads((R/'analysis/launch.json').read_text())
for f,h in launch['generation_sources_sha256'].items():assert sha(R/f)==h,('Generation code changed',f)
assert sha(R/'REGISTRATION.md')==launch['registration_sha256']
assert sha(R/'src/grading.py')==launch['sources']['src/grading.py'], 'Scoring implementation changed since launch'
for p,h in pre['frozen_source_data_hashes'].items():assert sha(B/p)==h,('Source/data mutated',p)
for p,h in json.loads((R/'analysis/baseline-freeze.json').read_text())['files'].items():assert sha(B/p)==h,('Baseline mutated',p)
records=[];hashes={};training=[]
for model,root in ROOTS.items():
 for condition in ['flat','macro','position','alias']:
  for seed in [11,22,33]:
   if condition in ['flat','macro']:
    paths={'main':root/f'runs/{condition}-original-s{seed}/predictions.jsonl','independent':S/f'extended/{model}/{condition}-s{seed}.jsonl'}
   else:
    base=R/f'runs/{model}-{condition}-s{seed}';done=json.loads((base/'complete.json').read_text());legacy=Path(done['legacy_output'])
    assert (base/'driver_snapshot.py').read_text()==code(model), 'Training driver differs from prescribed legacy wrapper'
    paths={'main':legacy/'predictions.jsonl','independent':base/'independent.jsonl'}
    log=[json.loads(l) for l in (legacy/'train.jsonl').read_text().splitlines()];assert len(log)==512 and log[-1]['examples']==16384
    assert all(np.isfinite(x['loss']) and np.isfinite(x['grad_norm']) for x in log)

    cfg=json.loads((legacy/'config.json').read_text());old=json.loads((root/f'runs/macro-original-s{seed}/config.json').read_text())
    for k in ['torch','cuda','gpu','model_revision','trainable_parameters','total_parameters']:assert cfg[k]==old[k],(model,condition,seed,k)
    for k in ['steps','microbatch','accum','seed','world']:assert cfg['args'][k]==old['args'][k],(model,condition,seed,k)
    assert cfg['training']['counts']['target_tokens']==271656*4

    if model in ['qwen7b','qwen32b']:
     old_initial=root/f'runs/macro-original-s{seed}/checkpoints/step0000/adapter/adapter_model.safetensors'
     new_initial=legacy/'checkpoints/step0000/adapter/adapter_model.safetensors'
     assert sha(old_initial)==sha(new_initial),('Initial adapter mismatch',model,condition,seed)
    training.append(dict(model=model,condition=condition,seed=seed,steps=512,examples=16384,target_tokens=log[-1]['target_tokens'],first_loss=log[0]['loss'],last_loss=log[-1]['loss'],seconds=done['seconds'],trainable_parameters=done['summary']['trainable_parameters']))
   for dataset,path in paths.items():
    raw=[json.loads(l) for l in path.read_text().splitlines()];assert len(raw)==(560 if dataset=='main' else 480)
    ref=[json.loads(l) for l in ((root/'data/test.jsonl') if dataset=='main' else S/'data/extended-test.jsonl').read_text().splitlines()]
    assert [(r['id'],r['x'],r['chain']) for r in raw]==[(r['id'],r['x'],r['chain']) for r in ref]
    hashes[str(path.relative_to(B))]=sha(path)
    for row in raw:
     g=grade(row,condition)
     records.append(dict(model=model,condition=condition,seed=seed,dataset=dataset,source=str(path.relative_to(B)),id=row['id'],split=row['split'],length=len(row['chain']),chain=row['chain'],x=row['x'],metrics=g))
assert len(records)==49920
(R/'analysis/graded.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in records))
metrics=['strict_trace','accuracy','label_sequence_correct','all_emitted_segments_correct','label_aware_complete','correct_prefix_early_answer','exact_two_tools_early_answer','internal_short_any','numeric_step_error','budget_hit']
summary=[];lookup=collections.defaultdict(list)
for row in records:lookup[row['model'],row['condition'],row['seed'],row['dataset']].append(row)
def select(rows,dataset,group):
 if group=='all':return rows
 if isinstance(group,int):return [x for x in rows if x['length']==group]
 return [x for x in rows if x['split']==group]
for model in ROOTS:
 for dataset in ['main','independent']:
  groups=(['all']+sorted({x['split'] for x in lookup[model,'flat',11,dataset]})) if dataset=='main' else ['all',3,4,5,6,8]
  for condition in ['flat','macro','position','alias']:
   for group in groups:
    seeds=[]
    for seed in [11,22,33]:
     rs=select(lookup[model,condition,seed,dataset],dataset,group);assert rs
     counts={m:sum(x['metrics'][m] for x in rs) for m in metrics}
     seeds.append(dict(seed=seed,n=len(rs),counts=counts,rates={k:v/len(rs) for k,v in counts.items()}))
    summary.append(dict(model=model,dataset=dataset,condition=condition,group=group,seeds=seeds,mean={m:sum(x['rates'][m] for x in seeds)/3 for m in metrics}))
comparisons=[];rng=np.random.default_rng(2026092602)
for model in ROOTS:
 for dataset in ['main','independent']:
  groups=sorted({x['split'] for x in lookup[model,'flat',11,dataset]}) if dataset=='main' else ['all',3,4,5,6,8]
  for group in groups:
   for a,b in [('position','flat'),('alias','flat'),('position','macro'),('alias','macro'),('alias','position')]:
    seeds=[];programs=collections.defaultdict(lambda:[0,0])
    for seed in [11,22,33]:
     ar=select(lookup[model,a,seed,dataset],dataset,group);br=select(lookup[model,b,seed,dataset],dataset,group)
     assert [x['id'] for x in ar]==[x['id'] for x in br]
     ac=sum(x['metrics']['strict_trace'] for x in ar);bc=sum(x['metrics']['strict_trace'] for x in br)
     gain=loss=0
     for x,y in zip(ar,br):
      d=x['metrics']['strict_trace']-y['metrics']['strict_trace'];key=tuple(x['chain']);programs[key][0]+=d;programs[key][1]+=1;gain+=d==1;loss+=d==-1
     seeds.append(dict(seed=seed,n=len(ar),a_correct=ac,b_correct=bc,delta=(ac-bc)/len(ar),gain=gain,loss=loss))
    v=np.array(list(programs.values()),dtype=float);idx=rng.integers(0,len(v),(3000,len(v)));vv=v[idx].sum(axis=1);boot=vv[:,0]/vv[:,1]
    comparisons.append(dict(model=model,dataset=dataset,group=group,a=a,b=b,seeds=seeds,mean_delta=sum(s['delta'] for s in seeds)/3,conditional_program_bootstrap95=np.quantile(boot,[.025,.975]).tolist(),programs=len(v)))
write(R/'analysis/results.json',dict(summary=summary,comparisons=comparisons,notes='Original strict trajectory endpoint preserved; labels separately graded. Bootstrap resamples programs holding the three trained seeds fixed, not a seed-population guarantee. Existing datasets reused, no new blind test.'))
write(R/'analysis/completion-audit.json',dict(complete=True,formal_records=len(records),new_formal_records=24960,reused_records=24960,new_training_jobs=len(training),source_sha256=hashes,training=training,source_data_frozen=True,legacy_scoring_equivalent=True))
labels={'flat':'Original STEP','macro':'Original NAME','position':'Added position numbering','alias':'Added fixed aliases'}
lines=['# Complete label-control results','All new training runs use a fixed 512 steps. Four scales x three seeds x two added conditions = 24 runs; the two original conditions are reused read-only. Primary scoring retains the original requirements for operations, every numerical state, and the final Answer. Label sequences are reported separately, without adding label-identity requirements to the original primary metric.','', '## Earlier independent 480-example set: full-trajectory success','', '|Model|Tool count|Original STEP|Original NAME|Position numbering|Fixed aliases|','|---|---|---:|---:|---:|---:|']
for model in ROOTS:
 for group in ['all',3,4,5,6,8]:
  vals=[next(x for x in summary if (x['model'],x['dataset'],x['condition'],x['group'])==(model,'independent',c,group))['mean']['strict_trace'] for c in labels]
  lines.append('|'+model+'|'+str(group)+'|'+'|'.join(f'{v*100:.2f}%' for v in vals)+'|')
lines+=['','## All original test subsets and subtask metrics','','All emitted-segment operations correct compares operations with the required segment at that position, without assuming STEP carries an identity. Missing segments are reflected in label-sequence/full-trajectory metrics. This is not oracle ability on all required operations. Within-segment early stopping means that an emitted segment is a nonempty proper prefix of the required operations at that position; it describes behavior rather than attributing a cause.','','|Model|Set|Subset/length|Condition|Full trajectory|Final answer|Label sequence|All emitted-segment operations correct|Early answer after correct prefix|Short internal segment|','|---|---|---|---|---:|---:|---:|---:|---:|---:|']
for x in summary:
 m=x['mean'];lines.append('|'+ '|'.join([x['model'],x['dataset'],str(x['group']),labels[x['condition']]]+[f'{m[k]*100:.2f}%' for k in ['strict_trace','accuracy','label_sequence_correct','all_emitted_segments_correct','correct_prefix_early_answer','internal_short_any']])+'|')
lines+=['','## Paired comparisons: negative seeds retained','','|Model|Set|Subset/length|Added/control|Mean difference pp|Three seed differences pp|Program bootstrap 95% pp|','|---|---|---|---|---:|---|---|']
for x in comparisons:
 lo,hi=x['conditional_program_bootstrap95'];lines.append('|'+ '|'.join([x['model'],x['dataset'],str(x['group']),labels[x['a']]+' − '+labels[x['b']],f'{100*x["mean_delta"]:+.2f}',' / '.join(f'{100*s["delta"]:+.2f}' for s in x['seeds']),f'[{100*lo:+.2f}, {100*hi:+.2f}]'])+'|')
lines+=['','The 49,920 total samples include 24,960 new and 24,960 reused trajectories, not that many independent examples. Bootstrap intervals are not corrected for multiple comparisons and do not replace more training seeds. Completing the main matrix and all seeds does not establish a specific mechanism.','Run costs and complete training logs are in analysis/completion-audit.json and each run directory. Final scientific interpretation is written to CONCLUSIONS.md after human review.']
(R/'REPORT.md').write_text('\n'.join(lines)+'\n');print('Analysis complete',len(records),'rows,',len(comparisons),'paired comparisons',flush=True)

import subprocess,sys
subprocess.run([sys.executable,str(R/"src/delivery.py")],check=True)
plot_python=B.parents[2]/".analysis-venv/bin/python"
subprocess.run([str(plot_python),str(R/"src/plots.py")],check=True)

subprocess.run([sys.executable,str(R/"src/boundary_diagnostics.py")],check=True)

subprocess.run([sys.executable,str(R/"src/auxiliary.py")],check=True)
