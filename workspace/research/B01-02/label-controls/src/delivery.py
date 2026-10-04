"""Deterministic result digest; requires scientific review, never marks goal complete."""
from common import *
import collections,time,random
D=json.loads((R/'analysis/results.json').read_text());summary=D['summary'];comp=D['comparisons']
labels={'flat':'Original STEP','macro':'Original NAME','position':'Position numbering','alias':'Fixed aliases'}
def cell(model,c,group='all'):
 return next(x for x in summary if (x['model'],x['dataset'],x['condition'],x['group'])==(model,'independent',c,group))
lines=['# Position and identity controls: automated summary (pending final scientific review)',
'This study aims to separate progress information, stable tool identity, and name form. The two original conditions were not retrained; the two new conditions retain the original training and Answer protocols. Results below are computed at fixed step512 on the earlier independent 480-example set. See REPORT.md for all counterexamples and original tests.',
'','|Model|Original STEP|Original NAME|Position numbering|Fixed aliases|','|---|---:|---:|---:|---:|']
for model in ROOTS:lines.append('|'+model+'|'+'|'.join(f'{100*cell(model,c)["mean"]["strict_trace"]:.2f}%' for c in labels)+'|')
lines+=['','## Paired evidence at each scale','']
for model in ROOTS:
 lines+=['### '+model,'','|Comparison|Mean difference pp|Three training-seed differences pp|','|---|---:|---|']
 for x in comp:
  if (x['model'],x['dataset'],x['group'])!=(model,'independent','all'):continue
  lines.append('|'+labels[x['a']]+' − '+labels[x['b']]+'|'+f'{100*x["mean_delta"]:+.2f}'+'|'+' / '.join(f'{100*s["delta"]:+.2f}' for s in x['seeds'])+'|')
 lines+=['','Positive and negative signs indicate observed directions. Means must not hide negative seeds, and three seeds do not adequately cover training randomness.','']
lines+=['## Scope of interpretation','',
'- The two added conditions have equal supervised output-token counts: 271656 per pass, compared with 263858 for Original NAME. New labels add approximately 2.96%; no padding or configuration changes are used to hide this difference. Alias input prompts are also longer.',
'- Position labels step3 and later are label combinations unseen in training, although digit tokens themselves occur in numerical states. Failure alone cannot rule out the value of position information.',
'- Alias and Original NAME both use matching names in inputs and outputs, so this comparison does not directly test matched versus mismatched names. If aliases are weaker, distinguishability of word forms, a shared tool prefix, tokenization/pretrained representations, and learning difficulty are all plausible explanations. A causal attention mechanism is not established.',
'- One fixed mapping is used across all seeds/scales, without replication over multiple mappings. The earlier test set has been used before and is not a fresh blind test.',
'- The original strict primary metric checks required operations and answers without requiring correct label identities. Label sequences and label-aware full-success rates are reported separately to preserve the original scoring standard.',
'- The task supplies the sequence; it does not directly test autonomous planning or mid-task stopping in real agents. Application transfer remains untested.',
'','All 49920 main/independent trajectories (24960 new, 24960 reused) are independently scored. See analysis/completion-audit.json for data and source-freeze checks. All generation failures remain in denominators. The system goal slot still refers to the older paused task; this study marks GOAL.json complete only after final human review and delivery.']
(R/'RESULT_DIGEST.md').write_text('\n'.join(lines)+'\n')
# Fixed random gains AND losses for all new-vs-old comparisons, selected after complete coverage.
rows=[json.loads(l) for l in (R/'analysis/graded.jsonl').read_text().splitlines()];lookup={(x['model'],x['condition'],x['seed'],x['dataset'],str(x['id'])):x for x in rows}
rng=random.Random(2026092603);selected=[];raw_cache={}
for model in ROOTS:
 for c in ['position','alias']:
  for baseline in (['flat','macro','position'] if c=='alias' else ['flat','macro']):
   for kind in ['gain','loss']:
    pool=[]
    for x in rows:
     if (x['model'],x['condition'],x['dataset'])!=(model,c,'independent'):continue
     y=lookup[model,baseline,x['seed'],x['dataset'],str(x['id'])];diff=x['metrics']['strict_trace']-y['metrics']['strict_trace']
     if diff==(1 if kind=='gain' else -1):pool.append((x,y))
    cases=rng.sample(pool,min(3,len(pool)))
    for x,y in cases:
     sources=[]
     for z in [x,y]:
      src=z['source']
      if src not in raw_cache:raw_cache[src]={str(t['id']):t for t in map(json.loads,(B/src).read_text().splitlines())}
      sources.append(dict(source=src,grade=z['metrics'],raw=raw_cache[src][str(z['id'])]))
     selected.append(dict(model=model,new=c,baseline=baseline,change=kind,population=len(pool),seed=x['seed'],id=x['id'],pair=sources))
write(R/'analysis/paired-cases.json',dict(selection='Fixed seed 2026092603, up to three from every gain AND loss stratum; illustrative, not denominator for success rates.',cases=selected))
write(R/'analysis/delivery-assembled.json',dict(time=time.time(),note='Digest and random paired cases assembled; agent must review before completion.'))
print('Digest and paired cases assembled:',len(selected),flush=True)

allocation=json.loads((R/'analysis/dispatch.json').read_text())['results']
assert len(allocation)==24 and all(x['returncode']==0 for x in allocation)
cost=[]
for model in ROOTS:
 rs=[x for x in allocation if x['job']['model']==model]
 cost.append(dict(model=model,jobs=len(rs),allocated_gpu_hours=sum(x['seconds'] for x in rs)/3600))
write(R/'analysis/resource-accounting.json',dict(per_model=cost,total_allocated_gpu_hours=sum(x['allocated_gpu_hours'] for x in cost),note='Sum of whole single-GPU process wall times, including loading, training, in-training evaluation and final evaluations; not kernel-active hours or pure optimization hours. Original baseline training sunk cost excluded.'))
lines=['# Reproduction and resource accounting','', 'This study uses only the existing project training/analysis environments and local PRO6000 GPUs. Per-run config.json, driver_snapshot.py, train.jsonl, model adapters, and outputs are retained in runs. analysis/preflight.json and baseline-freeze.json record hashes of data, original source, and earlier outputs; analysis/launch.json records the generation-wrapper version. Initial adapters for large models are checked file by file against the original same-seed adapters.','', 'Routine monitoring is hourly, with process-completion events handled automatically rather than minute-by-minute GPU polling. Any failure logs are retained without overwriting and rerunning. Apart from calls to target-construction functions, training algorithms retain the original source; see TRAINER_DIFF.md for the exact diff.','', '|Model|New jobs|Total single-GPU process wall hours|','|---|---:|---:|']
for x in cost:lines.append(f'|{x["model"]}|{x["jobs"]}|{x["allocated_gpu_hours"]:.2f}|')
lines+=['',f'Total: {sum(x["allocated_gpu_hours"] for x in cost):.2f} GPU-hours. This includes model loading, training, development-set/formal inference; it is neither active GPU-kernel time nor pure training time, and excludes historical training costs for the original baselines.',
'', 'After completion, rerun offline scoring/statistics from the project root if needed. This refreshes derived reports without retraining or overwriting raw outputs:', '', '```bash','source training-env.sh','python workspace/research/B01-02/label-controls/src/analyze.py','```','',
'New training uses worker.py --job INDEX, with configurations from analysis/jobs.json and scheduling records in analysis/dispatch.json. The worker refuses to overwrite existing runs. To reproduce training, first create a separate experiment directory at the same level and preserve original records; do not directly delete existing runs. Full base models and previous controls depend on original project paths, so this directory is not a standalone software package.']
(R/'REPRODUCTION_AND_COST.md').write_text('\n'.join(lines)+'\n')
