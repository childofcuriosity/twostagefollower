from pathlib import Path
import json,sys,collections,statistics,time,hashlib,math
import numpy as np
from scipy.stats import t
from audit import check
R=Path(__file__).resolve().parents[1]
for lane in ['lr','instruct']:
 marker=R/f'analysis/supplement-{lane}-completed.json'
 while not marker.exists():time.sleep(60)
 assert all(x['returncode']==0 for x in json.loads(marker.read_text()))
primary=json.loads((R/'analysis/results.json').read_text());assert not primary['missing'] and primary['final_execution_records']==13440
registered=json.loads((R/'analysis/supplement-registration.json').read_text())
assert hashlib.sha256((R/'src/train_supplement.py').read_bytes()).hexdigest()==registered['source_sha256']
source_hashes={}
main=[json.loads(l) for l in (R/'analysis/final-case-audit.jsonl').read_text().splitlines()];rows=[];runs=[];hashes={}
for model in ['qwen3b','qwen32b','qwen32b-instruct']:
 for seed in [11,22,33]:
  counts=[]
  for condition in ['flat','macro']:
   run=R/f'supplement/{model}/runs/{condition}-original-s{seed}';meta=json.loads((run/'summary.json').read_text());assert meta['training']['counts']['examples']==16384;assert meta['args']['steps']==512
   assert meta['source_sha256']==registered['source_sha256']
   assert meta['args']['lr']==next(x['lr'] for x in registered['groups'] if x['model']==model)
   loss=[json.loads(l) for l in (run/'train.jsonl').read_text().splitlines()];assert len(loss)==512;counts.append(meta['training']['counts']);runs.append(dict(model=model,seed=seed,condition=condition,args=meta['args'],training=meta['training'],gpu=meta.get('gpu'),source_sha256=meta['source_sha256']))
   assert [x['step'] for x in loss]==list(range(1,513))
   assert all(x['examples']==32*x['step'] and all(math.isfinite(x[k]) for k in ['loss','lr','grad_norm','elapsed']) for x in loss)
   for context,file in [('no_definitions','predictions.jsonl'),('definitions','predictions-with-library.jsonl')]:
    p=run/file;source_hashes[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest();rs=[json.loads(l) for l in p.read_text().splitlines()];assert len(rs)==560
    for row in rs:rows.append(dict(model=model,seed=seed,condition=condition,context=context,**check(row)))
   for p in [run/'adapter/adapter_model.safetensors']+list((run/'checkpoints').glob('*/adapter/adapter_model.safetensors')):
    h=hashlib.sha256()
    with p.open('rb') as f:
     for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    hashes[str(p.relative_to(R))]=h.hexdigest()
   assert hashes[str((run/'adapter/adapter_model.safetensors').relative_to(R))]==hashes[str((run/'checkpoints/step0512/adapter/adapter_model.safetensors').relative_to(R))]
  assert counts[0]==counts[1],(model,seed,'different tokens')
assert len(hashes)==126
frozen=[]
for context,file in [('no_definitions','predictions.jsonl'),('definitions','predictions-with-library.jsonl')]:
 p=R/f'supplement/qwen32b-instruct/runs/frozen-original-s11/{file}';source_hashes[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest();rs=[json.loads(l) for l in p.read_text().splitlines()];assert len(rs)==560
 for row in rs:frozen.append(dict(model='qwen32b-instruct',seed=11,condition='frozen',context=context,**check(row)))
metrics=['accuracy','strict_trace','correct_prefix_early_answer','exact_two_tools_early_answer','two_output_segments','wrong_operation','numeric_step_error','budget_hit']
summary=[]
for model in ['qwen3b','qwen32b','qwen32b-instruct']:
 for condition in ['flat','macro','frozen']:
  for context in ['no_definitions','definitions']:
   for split in ['iid','ood','pressure']:
    rs=[r for r in rows+frozen if (r['model'],r['condition'],r['context'],r['split'])==(model,condition,context,split)]
    if rs:summary.append(dict(model=model,condition=condition,context=context,split=split,n=len(rs),means={m:statistics.mean(r[m] for r in rs) for m in metrics}))
paired={}
for model in ['qwen3b','qwen32b']:
 paired[model]={}
 for condition in ['flat','macro']:
  paired[model][condition]={}
  for metric in metrics:
   differences=[]
   for seed in [11,22,33]:
    high=[r for r in main if (r['model'],r['condition'],r['seed'],r['split'])==(model,condition,seed,'ood')]
    low=[r for r in rows if (r['model'],r['condition'],r['seed'],r['split'],r['context'])==(model,condition,seed,'ood','no_definitions')]
    assert len(high)==len(low)==384;differences.append(statistics.mean(r[metric] for r in low)-statistics.mean(r[metric] for r in high))
   mean=float(np.mean(differences));margin=float(t.ppf(.975,2)*np.std(differences,ddof=1)/np.sqrt(3));paired[model][condition][metric]=dict(direction='low lr minus original lr',seed_differences=differences,mean=mean,seed_t95=[mean-margin,mean+margin])
assert len(source_hashes)==38
result=dict(source_sha256=source_hashes,registered_training_source_unchanged=True,raw_records=len(rows)+len(frozen),summary=summary,low_lr_comparisons=paired,training=runs,checkpoint_sha256=hashes,notes='Instruct uses official chat template consistently in training/test and is reported separately; not pure parameter-scale comparison. Low LR both 3B and 32B same 512 steps; no test-selected early stop.')
(R/'analysis/supplement-results.json').write_text(json.dumps(result,indent=2));(R/'analysis/supplement-case-audit.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows+frozen))
lines=[]
for r in summary:
 if r['split']=='ood':
  v=r['means'];lines.append(f"| {r['model']} | {r['condition']} | {r['context']} | {100*v['accuracy']:.2f}% | {100*v['strict_trace']:.2f}% | {100*v['exact_two_tools_early_answer']:.2f}% |")
text='''# Lower learning rate and instruction-model supplement

Registered before final formal scores for the new models were visible: symmetric 1e-4 learning rates for 3B/32B versus the original 3e-4 recipe, and 32B-Instruct at 3e-4 with the official chat template. Each flat/macro group uses three seeds, 512 steps, and batch size 32. Learning rate and stopping steps were not tuned on test scores. Intermediate adapters are retained; this comparison uses fixed final evaluation.

| Model | Condition | Tool definitions supplied | Long-composition answer correct | Complete trajectory correct | Stops after two correct tools |
|---|---|---|---:|---:|---:|
'''+ '\n'.join(lines)+'''

The frozen baseline receives one deterministic evaluation, not three training seeds. Without definitions, the base model does not know the artificial color mapping; low scores do not establish low capability. Results with and without definitions are different conditions. Base and Instruct differ in templates and post-training, so differences cannot all be attributed to parameter scale or prior stability. The low-learning-rate 3B group uses a 5090 while the original 3B group uses a PRO6000, limiting a purely learning-rate causal interpretation. Both 32B learning-rate groups use PRO6000 GPUs.

See [supplementary statistics](analysis/supplement-results.json) for all seed differences, 95% t intervals, example-level checks, training counts, and 126 checkpoint hashes. This file is a summary; interpret it with the main report and CONCLUSIONS.md.
'''
(R/'SUPPLEMENT.md').write_text(text);(R/'analysis/SUPPLEMENT_READY.json').write_text(json.dumps({'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'records':len(rows)+len(frozen),'checkpoint_files':len(hashes)},indent=2));print('Supplement complete, pending manual interpretation',flush=True)
