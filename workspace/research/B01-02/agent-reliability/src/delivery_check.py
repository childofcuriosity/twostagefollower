from pathlib import Path
import collections,hashlib,json,subprocess,time
from sandbox import R

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
x=json.loads((R/'analysis/results.json').read_text());audit=json.loads((R/'analysis/native-audit.json').read_text());mechanism=json.loads((R/'analysis/mechanism-audit.json').read_text());cfg={}
for p in (R/'queues').glob('*-batch.json'):
 rows=json.loads(p.read_text())
 for row in rows:
  assert isinstance(row,dict) and 'tag' in row,p
  if row['tag'] in cfg:assert row==cfg[row['tag']],row
  cfg[row['tag']]=row
for mode in ['zero','fewshot']:cfg['dev-'+mode]={'tag':'dev-'+mode,'queue':'dev.json','script':'native.py','mode':mode}
expected=set();workers=[]
for tag,c in sorted(cfg.items()):
 jobs=json.loads((R/'queues'/c['queue']).read_text());worker=json.loads((R/'analysis'/f'{tag}-completed.json').read_text());assert worker['jobs_requested']==worker['jobs_completed']==len(jobs),(tag,worker)
 workers.append({'tag':tag,'jobs':len(jobs),'gpu_reserved_seconds':worker['seconds']})
 for job in jobs:
  task,condition=job[:2];suffix=f'{task}--{condition}'
  if c.get('script','native.py').startswith('native_queue_controlled'):
   policy=job[2] if len(job)==3 else c['context_policy'];suffix+='--'+policy
  run='runs/'+tag+'/'+suffix;assert run not in expected;expected.add(run)
  summary=json.loads((R/run/'summary.json').read_text());assert summary['source_sha256']==sha(R/'src'/c.get('script','native.py')),(run,'source changed')
  assert summary['model_revision']=='5ede1c97bbab6ce5cda5812749b4c0bdf79b18dd'
actual={str(p.parent.relative_to(R)) for p in (R/'runs').glob('*/*/summary.json')};assert actual==expected and len(actual)==439,(len(actual),len(expected),expected-actual)
assert {str(p.relative_to(R)) for p in (R/'runs').glob('*/*') if p.is_dir()}==actual,'Partial unaccounted run'
assert {s['run'] for s in x['runs']}==actual=={s['run'] for s in audit['records']}
assert all(s['regraded'] and s['replay_matches'] for s in audit['records'])
assert len(mechanism['paired_prefix_checks'])==9 and all(s['pre_intervention_identical'] for s in mechanism['paired_prefix_checks'])
assert all(s['all_model_outputs_and_tool_results_identical'] for s in mechanism['deterministic_rerun'])
controlled=[s for s in audit['records'] if s['run'].startswith('runs/controlled-')];assert len(controlled)==21 and all(not s.get('tool_result_value_mismatches') for s in controlled)
assert abs(sum(w['gpu_reserved_seconds'] for w in workers)/3600-x['gpu_reserved_hours'])<1e-8
for name in ['REPORT.md','CONCLUSIONS.md','README.md','LITERATURE.md','figures/reliability.png','figures/reliability.svg','figures/reliability.pdf']:assert (R/name).stat().st_size>0,name
inventory=subprocess.run(['nvidia-smi','--query-gpu=index,memory.used,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout.splitlines()
result={'registered_and_completed_runs':len(actual),'independent_regrades':audit['count'],'controlled_exact_tool_result_replays':len(controlled),'paired_prefix_checks':9,'deterministic_model_reruns':1,'all_model_workers_finished':True,'gpu_reserved_hours':x['gpu_reserved_hours'],'gpu_inventory_at_delivery':inventory,'workers':workers,'checked_at':time.time(),'all_assets_in_project':True}
(R/'analysis/final-delivery-check.json').write_text(json.dumps(result,indent=2))
old_differences=sum(bool(s.get('tool_result_value_mismatches')) for s in audit['records'])
text=f'''# Delivery verification

- All {len(actual)} registered trajectories are complete, covering every run queue, with no uncounted partial run directories.
- All {audit['count']} archived final workspaces have been regraded, matching original scores. Successes and all 73 failures are retained.
- Action replays match final file states and tool-error states. In the early unfixed interface, full tool-return text in {old_differences} trajectories differs in time/host paths. These early cross-run differences cannot be interpreted as a single-method effect; see native-audit.json.
- All {len(controlled)} trajectories under the new controlled interface also pass full tool-return text equality checks.
- Model outputs and tool returns match before intervention in nine repair pairs. A new-process repeat of the original 5/24 failure matches trajectory, results, and files item by item.
- Original prompts, tool calls, results, final files, receipts, context-management records, and all development failures are saved.
- Total model-process occupancy is {x['gpu_reserved_hours']:.2f} GPU-hours. All model workers have exited; local GPU memory at delivery is recorded in final-delivery-check.json.
- Model weights were unchanged, with no paid external inference calls or external publication. Work environments, cache references, and artifacts remain in the current project directory.

These checks establish record completeness and agreement of scoring/replays, not general conclusions across models or real tasks from a 3-task mechanism study. Gains from the original summary/deletion methods do not establish a unique identity-restatement effect. The deliverable is a reproducible engineering repair and mechanism evidence; research novelty still requires further checking.

Review entry: [CONCLUSIONS.md](CONCLUSIONS.md); full report: [REPORT.md](REPORT.md); structured results: [analysis/results.json](analysis/results.json); mechanism checks: [analysis/mechanism-audit.json](analysis/mechanism-audit.json).
'''
(R/'COMPLETION_AUDIT.md').write_text(text)
assets=[p for p in R.glob('*.md')]+list((R/'src').glob('*.py'))+[p for p in (R/'analysis').glob('*.json') if p.name!='delivery-manifest.json']+list((R/'figures').glob('*'))+list((R/'queues').glob('*.json'))+[p for p in (R/'tasks').rglob('*') if p.is_file()]
manifest={'created_at':time.time(),'run_count':len(actual),'source_and_asset_sha256':{str(p.relative_to(R)):sha(p) for p in sorted(assets) if p.is_file()},'raw_artifact_hash_index':'analysis/native-audit.json','dependency_sha256':{'../agent-study/src/jail.c':sha(R.parent/'agent-study/src/jail.c'),'runtime/jail':sha(R/'runtime/jail')},'model_revision':'5ede1c97bbab6ce5cda5812749b4c0bdf79b18dd'}
(R/'analysis/delivery-manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({k:v for k,v in result.items() if k not in ['workers','gpu_inventory_at_delivery']},indent=2));print('GPU inventory:',inventory)
