import json,re,sys,collections,statistics,hashlib,csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PARENT=ROOT.parent;sys.path.insert(0,str(PARENT/'src'));import dsl
world=json.loads((PARENT/'data/worlds.json').read_text())['original'];lib=world['library']
locations={'qwen1.5b':PARENT,'qwen3b':PARENT/'rsi-study/replications/qwen3b','qwen7b':ROOT/'qwen7b','qwen32b':ROOT/'qwen32b'}
from audit import check
metrics=['accuracy','strict_trace','correct_prefix_early_answer','exact_two_tools_early_answer','two_output_segments','budget_hit','wrong_operation','numeric_step_error','format_extra_lines','missing_or_multiple_answer']
rows=[];sources={};training=[];missing=[]
for model,root in locations.items():
 for seed in [11,22,33]:
  for condition in ['flat','macro']:
   run=root/f'runs/{condition}-original-s{seed}';p=run/'predictions.jsonl'
   if not p.exists() or not (run/'summary.json').exists():missing.append(f'{model}/{condition}/s{seed}');continue
   rs=[json.loads(l) for l in p.read_text().splitlines()];assert len(rs)==560
   sources[str(p.resolve())]=hashlib.sha256(p.read_bytes()).hexdigest()
   for r in rs:rows.append(dict(model=model,seed=seed,condition=condition,**check(r)))
   meta=json.loads((run/'summary.json').read_text());assert meta['args']['steps']==512 and meta['training']['counts']['examples']==16384
   training.append(dict(model=model,seed=seed,condition=condition,training=meta['training'],microbatch=meta['args']['microbatch'],accum=meta['args']['accum']))
summary=[]
for model in locations:
 for condition in ['flat','macro']:
  for split in ['iid','ood','pressure']:
   rs=[r for r in rows if (r['model'],r['condition'],r['split'])==(model,condition,split)]
   if not rs:continue
   summary.append(dict(model=model,condition=condition,split=split,n=len(rs),unique_test_ids=len({r['id'] for r in rs}),means={k:statistics.mean(r[k] for r in rs) for k in metrics},seeds={str(seed):{k:statistics.mean(r[k] for r in rs if r['seed']==seed) for k in metrics} for seed in sorted({r['seed'] for r in rs})}))
curves=[];checked=0
for model in ['qwen7b','qwen32b']:
 for seed in [11,22,33]:
  for condition in ['flat','macro']:
   run=locations[model]/f'runs/{condition}-original-s{seed}'
   for p in sorted((run/'checkpoint-tests').glob('*-predictions.jsonl')):
    step=int(p.name[4:8]);rs=[check(json.loads(l)) for l in p.read_text().splitlines()];assert len(rs)==560;checked+=len(rs)
    for split in ['iid','ood','pressure']:
     sub=[r for r in rs if r['split']==split];curves.append(dict(model=model,condition=condition,seed=seed,step=step,split=split,**{k:statistics.mean(r[k] for r in sub) for k in metrics}))
   for p in list((run/'checkpoint-tests').glob('*-with-library.jsonl'))+list(run.glob('predictions-with-library.jsonl')):
    rs=[check(json.loads(l)) for l in p.read_text().splitlines()];assert len(rs)==560;checked+=len(rs)
stop_counts=[]
for model in locations:
 for condition in ['flat','macro']:
  for split in ['iid','ood','pressure']:
   rs=[r for r in rows if (r['model'],r['condition'],r['split'])==(model,condition,split)]
   if rs:stop_counts.append(dict(model=model,condition=condition,split=split,counts=dict(collections.Counter(r['stop_evidence'] for r in rs))))
result=dict(stop_evidence_counts=stop_counts,missing=missing,final_execution_records=len(rows),additional_execution_records_checked=checked,summary=summary,training=training,curves=curves,source_sha256=sources,notes='all test cases included, not conditioned on macro correctness; prefix-early-answer is a conservative directly verifiable subset, not every possible premature stop')
(ROOT/'analysis/results.json').write_text(json.dumps(result,indent=2))
(ROOT/'analysis/final-case-audit.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
with (ROOT/'analysis/summary.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=['model','condition','split','n']+metrics);w.writeheader()
 for r in summary:w.writerow({k:r[k] for k in ['model','condition','split','n']}|r['means'])
print('Analyzed',len(rows),'final records;',checked,'checkpoint/definition records; missing',missing,flush=True)
