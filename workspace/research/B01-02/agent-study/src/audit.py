"""Post-run evidence audit. Never supplies scores to a running agent."""
from pathlib import Path
import collections,hashlib,json,re,statistics,time
from sandbox import R,create
from tasks import grade

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
reg=json.loads((R/'analysis/registration-v2.json').read_text());manifest=json.loads((R/'analysis/task-manifest.json').read_text())
# Verify the treatment/execution code and every task fixture against pre-main registration.
for name in ['agent.py','sandbox.py','tasks.py','jail.c']:
 assert sha(R/'src'/name)==reg['source_sha256'][name],name
for name,h in reg['task_sha256'].items():assert sha(R/name)==h,name
expected={(task,c) for task in manifest['main_ids'] for c in ['plan','reminder','identity','todo']}
paths=list((R/'runs').glob('main-*/*/summary.json'));lookup={}
for p in paths:
 s=json.loads(p.read_text());key=(s['task'],s['condition']);assert key not in lookup;lookup[key]=(p,s)
assert set(lookup)==expected,(len(lookup),sorted(expected-set(lookup)))
root=R/'runtime/final-audit';records=[];hashes={};failed=[];status=[]
for key,(p,s) in sorted(lookup.items()):
 meta=json.loads((R/'tasks'/s['task']/'task.json').read_text());events=[json.loads(x) for x in (p.parent/'trajectory.jsonl').read_text().splitlines()]
 messages=json.loads((p.parent/'messages.json').read_text())
 assert messages[1]['content']==meta['user']
 assert [x['content'] for x in messages if x['role']=='assistant']==[x['raw'] for x in events]
 assert [x['turn'] for x in events]==list(range(len(events)))
 assert sum(x['generated_tokens'] for x in events)==s['generated_tokens'] and sum(x['input_tokens'] for x in events)==s['input_tokens']
 assert s['source_sha256']==reg['source_sha256']['agent.py']
 assert s['model_revision']==reg['revision']
 if s['stop_reason']=='agent_finish':assert events[-1]['action']['tool']=='finish' and events[-1]['action']['args']==s['finish']
 for event in events:
  assert event['generation_stop'] in ['eos','length_limit']
  action=event.get('action',{});txt=action.get('status','');ids=re.findall(r'\bT(\d{1,2})\b',txt)
  status.append(dict(task=s['task'],condition=s['condition'],turn=event['turn'],tool=action.get('tool'),status=txt,explicit_valid_task_ids=sorted(set(int(x) for x in ids if 1<=int(x)<=meta['n_requirements'])),invalid_task_ids=sorted(set(int(x) for x in ids if not 1<=int(x)<=meta['n_requirements'])),has_tool_error='error' in event.get('tool_result',{}) or event.get('tool_result',{}).get('returncode',0)!=0))
 # Re-evaluate untouched archived state, not the runtime directory already used by the original grader.
 create(root,p.parent/'final-workspace');g=grade(meta,root)
 assert [(x['passed']) for x in g['checks']]==[x['passed'] for x in s['grade']['checks']],(key,g,s['grade'])
 assert g['complete']==s['grade']['complete'] and g['protected_inputs_unchanged']==s['grade']['protected_inputs_unchanged']
 failure_details=[]
 for spec,check in zip(meta['specs'],g['checks']):
  if check['passed']:continue
  q=p.parent/'final-workspace'/spec['path'];initial=R/'tasks'/s['task']/'initial'/spec['path']
  if not q.exists():kind='required_output_missing'
  elif initial.exists() and sha(q)==sha(initial):kind='required_file_unchanged'
  else:kind='output_written_but_incorrect'
  failure_details.append(dict(requirement=check['id'],path=spec['path'],kind=kind,grader_detail=check['detail']))
 row=dict(task=s['task'],condition=s['condition'],category=s['category'],stop_reason=s['stop_reason'],grade=g,failure_details=failure_details,source=str(p.parent.relative_to(R)))
 records.append(row)
 if not g['complete']:failed.append(row|{'finish':s['finish']})
 for q in [p,p.parent/'trajectory.jsonl',p.parent/'messages.json']+list((p.parent/'final-workspace').rglob('*')):
  if q.is_file():hashes[str(q.relative_to(R))]=sha(q)
 print('AUDITED',s['task'],s['condition'],g['complete'],flush=True)
processes=json.loads((R/'analysis/main-processes.json').read_text())
assert len(processes)==4 and all(x['returncode']==0 for x in processes)
calibrations=[json.loads((R/'analysis'/f'{name}-process.json').read_text()) for name in ['calibration','calibration-v2']]
gpu_seconds=sum(x['wall_seconds'] for x in processes+calibrations)
assert gpu_seconds<8*3600,gpu_seconds
for p in (R/'analysis').glob('main-*-completed.json'):
 x=json.loads(p.read_text());assert x['jobs_requested']==24 and x['jobs_completed']==24
(R/'analysis/all-failures.json').write_text(json.dumps(failed,indent=2))
(R/'analysis/status-audit.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in status))
(R/'analysis/verification.json').write_text(json.dumps(dict(records_checked=96,failed_trajectories=len(failed),all_archived_workspaces_regraded=True,registered_execution_and_tasks_unchanged=True,gpu_reserved_seconds=gpu_seconds,gpu_reserved_hours=gpu_seconds/3600,budget_gpu_hours=8,original_failed_calibration_included=True,raw_sha256=hashes,cases=records,notes='Does not establish real-world generality; task generator has3 families. Claimed blocking is not automatically judged reasonable. Status lexical flags are descriptive, not causal proof.'),indent=2))
print('Verification complete',len(records),'failures',len(failed),'GPU hours',gpu_seconds/3600,flush=True)
