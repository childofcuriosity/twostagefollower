from common import *
import argparse,importlib.util,math,re,statistics,time,collections

p=argparse.ArgumentParser();p.add_argument('--length',type=int,required=True);p.add_argument('--phase',choices=('explore','formal'),required=True);p.add_argument('--conditions',nargs='+',choices=CONDITIONS);a=p.parse_args()
conditions=a.conditions or (('flat','macro') if a.phase=='explore' else CONDITIONS)
seeds=EXPLORE_SEEDS if a.phase=='explore' else FORMAL_SEEDS
data_root=R/f'data/L{a.length}'
if a.phase=='formal':data_root=data_root/'formal'
manifest=json.loads((data_root/('formal-manifest.json' if a.phase=='formal' else 'explore-manifest.json')).read_text())
test=[json.loads(x) for x in (data_root/'test.jsonl').read_text().splitlines()]
assert len(test)==512 and all(len(x['chain'])==a.length for x in test)
legacy_path=B/'scale-study/src/audit.py'
spec=importlib.util.spec_from_file_location('frozen_legacy_audit',legacy_path)
legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
header=re.compile(r'(?m)^[A-Za-z][A-Za-z0-9]*:$')
results={};graded=[]
for condition in conditions:
 runs=[]
 for seed in seeds:
  run=R/f'runs/{a.phase}-L{a.length}-{condition}-s{seed}'
  if not (run/'complete.json').exists():
   retries=sorted((R/'runs').glob(f'{a.phase}-L{a.length}-{condition}-s{seed}-retry*'))
   completed=[x for x in retries if (x/'complete.json').exists()]
   assert len(completed)==1,(run,retries)
   run=completed[0]
  assert (run/'complete.json').exists(),run
  pred_path=run/'runs'/f'{condition}-original-s{seed}'/'predictions.jsonl'
  rows=[json.loads(x) for x in pred_path.read_text().splitlines()]
  assert len(rows)==512 and [x['id'] for x in rows]==[x['id'] for x in test]
  counts=collections.Counter();token_count=0;strict=[]
  for row in rows:
   normalized=dict(row);normalized['raw']=header.sub('step:',row['raw']);normalized['max_new_tokens']=manifest['generation_cap']
   g=legacy.check(normalized)
   if condition in ('flat','macro'):
    assert legacy.check(row)['strict_trace']==g['strict_trace']
   strict.append(g['strict_trace'])
   traces=re.findall(r'^(rev|rot|inc|neg|swap|ends) [0-9] [0-9] [0-9] [0-9]$',normalized['raw'],re.M)
   required=len(dsl.expand(row['chain'],WORLD['library']))
   emitted=len(traces)
   emitted_tools=len(re.findall(r'^[A-Za-z][A-Za-z0-9]*:$',row['raw'],re.M))
   required_tools=len(row['chain'])
   counts['under_tools']+=emitted_tools<required_tools
   counts['over_tools']+=emitted_tools>required_tools
   counts['under_ops']+=emitted<required
   counts['over_ops']+=emitted>required
   counts['wrong_expansion']+=bool(g['wrong_operation'])
   counts['numeric_error']+=bool(g['numeric_step_error'])
   counts['generation_limit']+=row['generated_tokens']>=manifest['generation_cap']
   counts['correct']+=g['strict_trace'];token_count+=row['generated_tokens']
   graded.append(dict(phase=a.phase,length=a.length,condition=condition,seed=seed,id=row['id'],
                      strict_trace=g['strict_trace'],under_tools=emitted_tools<required_tools,over_tools=emitted_tools>required_tools,
                      emitted_tools=emitted_tools,required_tools=required_tools,under_ops=emitted<required,over_ops=emitted>required,
                      wrong_expansion=bool(g['wrong_operation']),numeric_error=bool(g['numeric_step_error']),
                      generation_limit=row['generated_tokens']>=manifest['generation_cap'],generated_tokens=row['generated_tokens'],
                      old_score=g))
  summary=json.loads((run/'runs'/f'{condition}-original-s{seed}'/'summary.json').read_text())
  runs.append(dict(seed=seed,correct=counts['correct'],n=512,rate=counts['correct']/512,
                   counts=dict(counts),mean_generated_tokens=token_count/512,
                   gpu_hours=summary['gpu_hours'],predictions_sha256=sha(pred_path)))
 rates=[x['rate'] for x in runs]
 results[condition]=dict(mean=statistics.mean(rates),sample_sd=statistics.stdev(rates),runs=runs)
paired={}
if 'flat' in results:
 base={x['seed']:x['rate'] for x in results['flat']['runs']}
 for c in conditions:
  if c=='flat':continue
  diffs=[x['rate']-base[x['seed']] for x in results[c]['runs']]
  paired[c]=dict(mean=statistics.mean(diffs),sample_sd=statistics.stdev(diffs),
                 positive_seeds=sum(x>0 for x in diffs),negative_seeds=sum(x<0 for x in diffs),
                 per_seed=dict(zip(seeds,diffs)))
path=R/'analysis'/f'scores-{a.phase}-L{a.length}.json'
write(path,dict(length=a.length,phase=a.phase,manifest_sha256=sha(data_root/('formal-manifest.json' if a.phase=='formal' else 'explore-manifest.json')),
                old_audit_sha256=sha(legacy_path),results=results,paired_vs_flat=paired,
                scored_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())))
with (R/'analysis'/f'graded-{a.phase}-L{a.length}.jsonl').open('w') as f:
 for row in graded:f.write(json.dumps(row)+'\n')
print(json.dumps(dict(length=a.length,phase=a.phase,means={c:results[c]['mean'] for c in conditions},paired={c:paired[c]['mean'] for c in paired})))
