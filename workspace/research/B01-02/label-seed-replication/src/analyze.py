from common import *
from importlib.util import spec_from_file_location,module_from_spec
import collections,math,statistics

pre=json.loads((R/'analysis/preflight.json').read_text())
assert sha(R/'REGISTRATION.md')==pre['registration_sha256']
for p,h in pre['source_hashes'].items():assert sha(B/p)==h,(p,'source changed')
for p,h in pre['baseline_hashes'].items():assert sha(B/p)==h,(p,'baseline changed')
spec=spec_from_file_location('label_grading',L/'src/grading.py')
sys.path.insert(0,str(L/'src'))
grading=module_from_spec(spec);spec.loader.exec_module(grading)

def paths(model,condition,seed):
 root=ROOTS[model]
 if seed in (11,22,33):
  if condition in ('flat','macro'):
   return root/f'runs/{condition}-original-s{seed}/predictions.jsonl',S/f'extended/{model}/{condition}-s{seed}.jsonl'
  run=L/f'runs/{model}-{condition}-s{seed}'
  return run/f'runs/{condition}-original-s{seed}/predictions.jsonl',run/'independent.jsonl'
 run=R/f'runs/{model}-{condition}-s{seed}'
 assert (run/'complete.json').exists(),run
 assert (run/'driver_snapshot.py').read_text()==driver(model)
 return run/f'runs/{condition}-original-s{seed}/predictions.jsonl',run/'independent.jsonl'

allseeds=[11,22,33]+SEEDS
ref_main=[json.loads(x) for x in (B/'data/test.jsonl').read_text().splitlines()]
ref_ind=[json.loads(x) for x in (S/'data/extended-test.jsonl').read_text().splitlines()]
assert len(ref_main)==560 and len(ref_ind)==480
results={};sources={};training=[]
for model in ROOTS:
 for condition in CONDITIONS:
  for seed in allseeds:
   main,ind=paths(model,condition,seed)
   vals={}
   for dataset,path,ref in [('main',main,ref_main),('independent',ind,ref_ind)]:
    rows=[json.loads(x) for x in path.read_text().splitlines()]
    assert [(x['id'],x['x'],x['chain']) for x in rows]==[(x['id'],x['x'],x['chain']) for x in ref]
    scores=[grading.grade(x,condition) for x in rows]
    vals[dataset]=dict(all=sum(x['strict_trace'] for x in scores)/len(scores),ood=sum(x['strict_trace'] for x,y in zip(scores,rows) if y['split']=='ood')/384 if dataset=='main' else None,
                       by_length={str(length):sum(x['strict_trace'] for x,y in zip(scores,rows) if len(y['chain'])==length)/96 for length in (3,4,5,6,8)} if dataset=='independent' else {})
    sources[str(path.relative_to(B))]=sha(path)
   if seed in SEEDS:
    run=R/f'runs/{model}-{condition}-s{seed}'
    legacy=run/f'runs/{condition}-original-s{seed}'
    log=[json.loads(x) for x in (legacy/'train.jsonl').read_text().splitlines()]
    assert len(log)==512 and log[-1]['examples']==16384
    assert all(math.isfinite(x['loss']) and math.isfinite(x['grad_norm']) for x in log)
    cfg=json.loads((legacy/'config.json').read_text());summary=json.loads((legacy/'summary.json').read_text())
    assert cfg['args']['seed']==seed and cfg['args']['condition']==condition and cfg['args']['steps']==512
    assert cfg['args']['microbatch']==16 and cfg['args']['accum']==2
    assert summary['training']['counts']['examples']==16384
    expected_tokens=next(x['target_tokens'] for x in pre['checks'] if x['model']==model and x['condition']==condition)*4
    assert log[-1]['target_tokens']==expected_tokens
    training.append(dict(model=model,condition=condition,seed=seed,first_loss=log[0]['loss'],last_loss=log[-1]['loss'],seconds=json.loads((run/'complete.json').read_text())['seconds']))
   results[model,condition,seed]=vals

# For the first new 7B seed, all four conditions must start from identical LoRA weights.
initial=[]
for condition in CONDITIONS:
 p=R/f'runs/qwen7b-{condition}-s100/runs/{condition}-original-s100/checkpoints/step0000/adapter/adapter_model.safetensors'
 initial.append(sha(p))
assert len(set(initial))==1,('initial adapter mismatch',initial)

def avg_sd(a):return statistics.mean(a),statistics.stdev(a)
def fmt(a):
 m,s=avg_sd(a)
 return f'{m*100:.2f} ± {s*100:.2f}'

records=[]
for model in ROOTS:
 row={'model':model,'conditions':{},'comparisons':{}}
 for condition in CONDITIONS:
  a=[results[model,condition,seed]['independent']['all'] for seed in allseeds]
  row['conditions'][condition]=dict(seeds=dict(zip(map(str,allseeds),a)),mean=statistics.mean(a),sample_sd=statistics.stdev(a),min=min(a),max=max(a),original_ood_mean=statistics.mean(results[model,condition,seed]['main']['ood'] for seed in allseeds))
 for a,b in [('position','flat'),('alias','position'),('macro','alias'),('macro','flat'),('alias','macro')]:
  ds=[results[model,a,seed]['independent']['all']-results[model,b,seed]['independent']['all'] for seed in allseeds]
  mean,sd=avg_sd(ds);half=2.093024054*sd/math.sqrt(len(ds))
  row['comparisons'][a+'-'+b]=dict(seed_differences=dict(zip(map(str,allseeds),ds)),mean=mean,sample_sd=sd,t95=[mean-half,mean+half],positive=sum(x>0 for x in ds),negative=sum(x<0 for x in ds),ties=sum(x==0 for x in ds))
 records.append(row)
write(R/'analysis/results.json',dict(seeds=allseeds,models=records,source_sha256=sources,training=training,initial_7b_s100_sha256=initial[0],note='20 fixed training seeds. t intervals cover training-seed mean conditionally on reused task set and one alias mapping; descriptive, no multiplicity correction.'))

labels={'flat':'Uniform step','position':'Position numbering','alias':'Fixed aliases','macro':'Original tool names'}
lines=['# Label experiments: replication with 20 training seeds','',
 'The original training data, earlier independent 480-example set, and one alias mapping are fixed. The original 3 seeds are reused, with 17 new seeds 100–116. Results reflect only training randomness under fixed data and mapping. Values are mean ± sample SD, in percent.',
 '', '|Model|Uniform step|Position numbering|Fixed aliases|Original tool names|','|---|---:|---:|---:|---:|']
for row in records:
 lines.append('|'+row['model']+'|'+'|'.join(fmt([results[row['model'],condition,seed]['independent']['all'] for seed in allseeds])+'%' for condition in CONDITIONS)+'|')
lines+=['','## Same-seed paired differences: earlier independent 480-example set','', 'Differences, sample SDs, and 95% t intervals are in percentage points. Intervals cover training-seed variation only, conditional on this set of test programs.','',
 '|Model|Comparison|Mean±SD|95% interval|Positive/negative/tied seeds|','|---|---|---:|---:|---:|']
for row in records:
 for a,b in [('position','flat'),('alias','position'),('macro','alias'),('macro','flat'),('alias','macro')]:
  x=row['comparisons'][a+'-'+b]
  lines.append(f"|{row['model']}|{labels[a]} − {labels[b]}|{x['mean']*100:+.2f} ± {x['sample_sd']*100:.2f}|[{x['t95'][0]*100:+.2f}, {x['t95'][1]*100:+.2f}]|{x['positive']}/{x['negative']}/{x['ties']}|")
lines+=['','## Original OOD test: 384 examples','', '|Model|Uniform step|Position numbering|Fixed aliases|Original tool names|','|---|---:|---:|---:|---:|']
for row in records:
 model=row['model'];lines.append('|'+model+'|'+'|'.join(fmt([results[model,c,s]['main']['ood'] for s in allseeds])+'%' for c in CONDITIONS)+'|')
lines+=['','## Interpretation limits','',
 '- All 20 seeds use the same 4096 training examples, 480 test examples, and fixed alias mapping. SD does not measure uncertainty for new tasks, new data, or different mappings.',
 '- Position numbering and tool identity do not form a strictly increasing information hierarchy; original names and fixed aliases both identify tools. The two new target formats contain approximately 2.96% more tokens than original names, and alias inputs are longer.',
 '- Training contains only 1–2 calls; headings step3 and later for long tasks never appear as headings in training.',
 '- Multiple comparisons are uncorrected, and the earlier independent set has been analyzed repeatedly. Positive/negative seed counts and intervals are not evidence about real agents or RSI.',
 '- See analysis/results.json for every training seed, training loss, output-file hash, and itemized result. All failures are retained in raw outputs.']
(R/'REPORT.md').write_text('\n'.join(lines)+'\n')
write(R/'analysis/completion-audit.json',dict(complete=True,new_training_jobs=len(training),total_model_condition_seed=len(results),main_and_independent_score_records=len(results)*(560+480),new_score_records=len(training)*(560+480),baseline_hashes_unchanged=True,initial_7b_s100_identical=True))
print('analyzed',len(results),'model/condition/seed units',flush=True)
