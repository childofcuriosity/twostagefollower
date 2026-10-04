"""Analyze all preregistered endpoints and curves; no model calls or selection."""
import collections,json,math,statistics,sys
from pathlib import Path
STUDY=Path(__file__).resolve().parents[1];sys.path.insert(0,str(STUDY/'src'))
from common import CONDITIONS,SEEDS,readrows,write,score,sha,R,ROOT
assert all((R/f'runs/v1-{c}-s{seed}/complete.json').exists() for c in CONDITIONS for seed in SEEDS),'Task training still incomplete'
assert len(list((ROOT/'eval/outputs').glob(R.name+'-*/complete.json')))==280,'Task scheduled evaluations still incomplete'

def evaluation(c,seed,step,split):
 outputs=[];metadata=[]
 for shard in range(4):
  folder=ROOT/f'eval/outputs/{R.name}-{c}-s{seed}-step{step:03d}-{split}-part{shard}'
  meta=json.loads((folder/'complete.json').read_text());rr=readrows(folder/'predictions.jsonl')
  assert len(rr)==meta['n'] and meta['predictions_sha256']==sha(folder/'predictions.jsonl')
  outputs+=rr;metadata.append(meta)
 expected=readrows(R/f'data/{split}.jsonl');byid={x['id']:x for x in outputs}
 assert len(byid)==len(outputs)==len(expected)
 outputs=[byid[x['id']] for x in expected]
 for row,truth in zip(outputs,expected):
  assert row['chain']==truth['chain'] and row['x']==truth['x']
  grading=score(row,row['raw'],c,row['generated_tokens'],row['finish_reason']);assert grading==row['grading']
 rates=dict(n=len(outputs),correct=sum(x['grading']['strict'] for x in outputs),success_rate=sum(x['grading']['strict'] for x in outputs)/len(outputs),header_rate=sum(x['grading']['header_compliant'] for x in outputs)/len(outputs),output_tokens=sum(x['generated_tokens'] for x in outputs),input_tokens=sum(x['input_tokens'] for x in outputs),generate_seconds=sum(x['allocated_generate_seconds'] for x in outputs),wall_seconds_sum=sum(x['wall_seconds'] for x in metadata),errors={k:sum(x['grading'][k] for x in outputs) for k in ['numeric_error','operation_mismatch','early_end','extra_output','extra_ops','missing_ops']},endings=dict(collections.Counter(x['finish_reason'] for x in outputs)),ids=[x['id'] for x in outputs],strict=[x['grading']['strict'] for x in outputs])
 return rates
base={c:{split:evaluation(c,'base',0,split) for split in ['validation','test']} for c in CONDITIONS}
curves=[];endpoints=[];training=[];total_candidates=0;actual_evals=1536;verified_checkpoints=0
for seed in SEEDS:
 pair_init=[]
 for c in CONDITIONS:
  folder=R/f'runs/v1-{c}-s{seed}';complete=json.loads((folder/'complete.json').read_text());assert complete['updates']==100
  job=json.loads((folder/'job.json').read_text());pair_init.append(job['initial_adapter_sha256'])
  assert job['config_sha256']==sha(R/'config/frozen.json')
  freeze=json.loads((R/'config/freeze-manifest.json').read_text())
  for executable in ['common.py','engine.py','train.py']:
   assert job['source'][executable]==freeze['source'][executable]
  for checkpoint_step in range(0,101,10):
   cp=folder/f'checkpoint-{checkpoint_step:03d}';cm=json.loads((cp/'checkpoint.json').read_text())
   assert cm['update']==checkpoint_step and cm['adapter_sha256']==sha(cp/'adapter_model.safetensors')
   assert cm['config_sha256']==sha(R/'config/frozen.json')
   assert all((cp/name).exists() for name in ['optimizer.pt','rng-rank0.pt','rng-rank1.pt'])
   verified_checkpoints+=1
  ranklogs=[readrows(folder/f'metrics-rank{rank}.jsonl') for rank in range(2)]
  assert all([x['update'] for x in logs]==list(range(1,101)) for logs in ranklogs)
  initial=base[c]['validation'];curve=[dict(step=0,rate=initial['success_rate'],correct=initial['correct'],output_tokens=initial['output_tokens'],generate_seconds=initial['generate_seconds'],training_gpu_seconds=0.,training_output_tokens=0,source='shared original-model step0')]
  expected_order=json.loads((R/f'data/order-s{seed}.json').read_text())['indices'];expected_train=readrows(R/'data/train.jsonl')
  for update in range(1,101):
   candidates=[]
   for rank in range(2):
    pp=folder/f'candidates/update-{update:03d}-rank{rank}.jsonl';rows=readrows(pp);assert len(rows)==64
    ids=[x['id'] for x in rows[::8]]
    desired=[expected_train[i]['id'] for i in expected_order[(update-1)*16+rank*8:(update-1)*16+(rank+1)*8]];assert ids==desired
    for group in range(8):
     group_rows=rows[group*8:(group+1)*8];assert len({x['id'] for x in group_rows})==1
     rewards=[x['grading']['reward'] for x in group_rows];mean=statistics.mean(rewards);sd=statistics.stdev(rewards)
     for x in group_rows:
      check=score(x,x['raw'],c,x['generated_tokens'],x['finish_reason']);assert check==x['grading']
      assert abs(x['advantage']-(x['grading']['reward']-mean)/(sd+1e-4))<1e-5
    candidates+=rows
   assert len(candidates)==128;total_candidates+=128
  for step in range(10,101,10):
   v=evaluation(c,seed,step,'validation');actual_evals+=256
   tt=[x for logs in ranklogs for x in logs if x['update']<=step]
   curve.append(dict(step=step,rate=v['success_rate'],correct=v['correct'],output_tokens=v['output_tokens'],generate_seconds=v['generate_seconds'],training_gpu_seconds=sum(x['seconds'] for x in tt),training_output_tokens=sum(x['output_tokens'] for x in tt),errors=v['errors'],header_rate=v['header_rate'],endings=v['endings']))
  test=evaluation(c,seed,100,'test');actual_evals+=512
  endpoints.append(dict(condition=c,seed=seed,step0=base[c]['test']['success_rate'],step100=test['success_rate'],improvement=test['success_rate']-base[c]['test']['success_rate'],details=test))
  thresholds={str(t):next((dict(step=x['step'],training_gpu_seconds=x['training_gpu_seconds'],training_output_tokens=x['training_output_tokens']) for x in curve if x['rate']>=t),None) for t in [.6,.7,.8,.9]}
  auc=sum((a['rate']+b['rate'])/2*(b['step']-a['step']) for a,b in zip(curve,curve[1:]))/100
  curves.append(dict(condition=c,seed=seed,points=curve,thresholds=thresholds,mean_validation_curve_area=auc))
  allmetrics=[x for logs in ranklogs for x in logs]
  training.append(dict(condition=c,seed=seed,candidates=sum(x['candidates'] for x in allmetrics),output_tokens=sum(x['output_tokens'] for x in allmetrics),sampling_seconds=sum(x['sampling_seconds'] for x in allmetrics),update_seconds=sum(x['update_seconds'] for x in allmetrics),update_wall_seconds_sum=sum(x['seconds'] for x in allmetrics),run_wall_seconds=complete['seconds'],allocated_gpu_seconds=2*complete['seconds'],mean_training_reward=statistics.mean(x['mean_reward'] for x in allmetrics),mixed_group_fraction=sum(x['mixed_groups'] for x in allmetrics)/sum(x['groups'] for x in allmetrics),all_zero_groups=sum(x['all_zero_groups'] for x in allmetrics),all_one_groups=sum(x['all_one_groups'] for x in allmetrics),duplicate_fraction=1-sum(x['unique_candidates'] for x in allmetrics)/sum(x['candidates'] for x in allmetrics),max_kl=max(x['kl'] for x in allmetrics),max_grad_norm=max(x['grad_norm'] for x in allmetrics),truncated=sum(x['truncated'] for x in allmetrics)))
 assert len(set(pair_init))==1,(seed,'unpaired initialization')
assert total_candidates==76800 and actual_evals==19968 and verified_checkpoints==66
by={(x['condition'],x['seed']):x for x in endpoints};pairs=[]
for seed in SEEDS:
 s=by['STEP',seed];n=by['NAME',seed]
 delta=n['step100']-s['step100'];paired_item=[a-b for a,b in zip(n['details']['strict'],s['details']['strict'])]
 assert math.isclose(delta,statistics.mean(paired_item),abs_tol=1e-12)
 pairs.append(dict(seed=seed,NAME_minus_STEP=delta,difference_of_improvements=n['improvement']-s['improvement'],NAME_only=sum(x==1 for x in paired_item),STEP_only=sum(x==-1 for x in paired_item)))
summary={c:dict(step0=base[c]['test']['success_rate'],step100_mean=statistics.mean(x['step100'] for x in endpoints if x['condition']==c),step100_sample_sd=statistics.stdev(x['step100'] for x in endpoints if x['condition']==c),improvement_mean=statistics.mean(x['improvement'] for x in endpoints if x['condition']==c)) for c in CONDITIONS}
summary['paired']=dict(mean=statistics.mean(x['NAME_minus_STEP'] for x in pairs),sample_sd=statistics.stdev(x['NAME_minus_STEP'] for x in pairs),positive_seeds=sum(x['NAME_minus_STEP']>0 for x in pairs),difference_of_improvements_mean=statistics.mean(x['difference_of_improvements'] for x in pairs))
write(R/'analysis/results.json',dict(base=base,endpoints=endpoints,paired=pairs,summary=summary,curves=curves,training=training,fixed_checkpoints_verified=verified_checkpoints,formal_candidates_verified=total_candidates,independent_eval_outputs_verified=actual_evals))
print(json.dumps(summary,indent=2))
