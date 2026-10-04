"""Audit complete multi-action rollouts, regrade archived states, replay atomic actions."""
from pathlib import Path
import collections,hashlib,json,re,time
from sandbox import R,create
from tasks import grade
from agent import tool,parse

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(work):return {str(p.relative_to(work)):sha(p) for p in work.rglob('*') if p.is_file()}
reg=json.loads((R/'analysis/registration.json').read_text());manifest=json.loads((R/'analysis/task-manifest.json').read_text())
for name in ['agent.py','sandbox.py','tasks.py','jail.c']:assert sha(R/'src'/name)==reg['source_sha256'][name],name
for name,h in reg['task_sha256'].items():assert sha(R/name)==h,name
lookup={}
for p in (R/'runs').glob('main-*/*/summary.json'):
 s=json.loads(p.read_text());key=(s['task'],s['condition']);assert key not in lookup;lookup[key]=(p,s)
assert set(lookup)=={(t,c) for t in manifest['main_ids'] for c in ['plan','reminder','identity','todo']}
root=R/'runtime/replay';auditroot=R/'runtime/archive-audit';rows=[];hashes={};statuses=[]
for key,(p,s) in sorted(lookup.items()):
 meta=json.loads((R/'tasks'/s['task']/'task.json').read_text());events=[json.loads(x) for x in (p.parent/'trajectory.jsonl').read_text().splitlines()];messages=json.loads((p.parent/'messages.json').read_text())
 assert messages[1]['content']==meta['user']
 assert [x['content'] for x in messages if x['role']=='assistant']==[x['raw'] for x in events]
 assert [x['turn'] for x in events]==list(range(len(events)))
 assert sum(x['generated_tokens'] for x in events)==s['generated_tokens'] and sum(x['input_tokens'] for x in events)==s['input_tokens']
 assert s['source_sha256']==reg['source_sha256']['agent.py'] and s['model_revision']==reg['model_revision']
 create(auditroot,p.parent/'final-workspace');g=grade(meta,auditroot)
 assert [x['passed'] for x in g['checks']]==[x['passed'] for x in s['grade']['checks']] and g['complete']==s['grade']['complete']
 work=create(root,R/'tasks'/s['task']/'initial');first=None;history=[];progress=[];sideeffects=[];mismatches=[];protocol_errors=0;parsed_batches=0;finish=None
 for event in events:
  try:decoded=parse(event['raw'])
  except (ValueError,AssertionError,KeyError,TypeError):
   protocol_errors+=1;assert 'error' in event['tool_result'];continue
  assert decoded==event['action'];actions=decoded['args']['actions'] if decoded['tool']=='batch' else [decoded]
  parsed_batches+=decoded['tool']=='batch';results=[]
  for index,action in enumerate(actions):
   txt=action['status'];ids=re.findall(r'\bT(\d{1,2})\b',txt)
   statuses.append(dict(task=s['task'],condition=s['condition'],turn=event['turn'],index=index,tool=action['tool'],status=txt,explicit_task_ids=sorted(set(int(x) for x in ids if 1<=int(x)<=meta['n_requirements']))))
   if action['tool']=='finish':
    finish=action['args'];break
   try:result=tool(work,root,action['tool'],action['args'])
   except Exception as ex:result={'error':type(ex).__name__+': '+str(ex)[:1000]}
   results.append(dict(tool=action['tool'],result=result));history.append(dict(turn=event['turn'],index=index,tool=action['tool'],args=action['args'],after_completion=first is not None))
   if action['tool'] in ['write_file','run_python']:
    before=digest(work);state=grade(meta,root)
    if digest(work)!=before:sideeffects.append((event['turn'],index))
    progress.append(dict(turn=event['turn'],index=index,complete=state['complete'],completed_requirements=state['completed_requirements']))
    if first is None and state['complete']:first=[event['turn'],index]
  observed=event.get('tool_result',{}).get('batch_results',[])
  if len(results)!=len(observed):mismatches.append(event['turn'])
  else:
   for a,b in zip(results,observed):
    if a['tool']!=b['tool'] or ('error' in a['result'])!=('error' in b['result']) or a['result'].get('returncode',0)!=b['result'].get('returncode',0):mismatches.append(event['turn'])
 if s['stop_reason']=='agent_finish':assert finish==s['finish']
 final_matches=digest(work)==digest(p.parent/'final-workspace');assert final_matches and not sideeffects and not mismatches,(key,final_matches,sideeffects,mismatches)
 failures=[]
 for spec,check in zip(meta['specs'],g['checks']):
  if check['passed']:continue
  q=p.parent/'final-workspace'/spec['path'];original=R/'tasks'/s['task']/'initial'/spec['path']
  kind='required_output_missing' if not q.exists() else ('required_file_unchanged' if original.exists() and sha(q)==sha(original) else 'output_written_but_incorrect')
  failures.append(dict(requirement=check['id'],path=spec['path'],kind=kind,detail=check['detail']))
 rows.append(dict(task=s['task'],condition=s['condition'],category=s['category'],stop_reason=s['stop_reason'],finish=s['finish'],grade=g,failure_details=failures,protocol_error_turns=protocol_errors,accepted_batch_turns=parsed_batches,actual_tool_calls=len(history),first_complete_action=first,post_completion_actions=[x for x in history if x['after_completion']],progress=progress,final_workspace_matches=final_matches,source=str(p.parent.relative_to(R))))
 for q in [p,p.parent/'trajectory.jsonl',p.parent/'messages.json']+list((p.parent/'final-workspace').rglob('*')):
  if q.is_file():hashes[str(q.relative_to(R))]=sha(q)
 print('AUDIT',s['task'],s['condition'],g['complete'],flush=True)
main=json.loads((R/'analysis/main-processes.json').read_text());assert len(main)==4 and all(x['returncode']==0 for x in main)
cal=json.loads((R/'analysis/calibration-process.json').read_text());hours=(sum(x['wall_seconds'] for x in main)+cal['wall_seconds'])/3600
combined=hours+reg['original_gpu_hours'];assert combined<8
(R/'analysis/status-audit.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in statuses))
(R/'analysis/verification.json').write_text(json.dumps(dict(records_checked=96,registered_execution_and_tasks_unchanged=True,all_archived_states_regraded=True,all_action_replays_match=True,compatibility_gpu_hours=hours,combined_gpu_hours=combined,budget_gpu_hours=8,raw_sha256=hashes,cases=rows),indent=2))
print('Verified all96 compatibility trajectories; combined GPU hours',combined,flush=True)
