"""CPU-only replay of recorded actions to locate completion; no model rerun or oracle feedback."""
from pathlib import Path
import hashlib,json
from sandbox import R,create
from tasks import grade
from agent import tool

def digest(work):return {str(p.relative_to(work)):hashlib.sha256(p.read_bytes()).hexdigest() for p in work.rglob('*') if p.is_file()}
root=R/'runtime/replay-audit';records=[];batch_diagnostics=[]
def decode_batch(raw):
 decoder=json.JSONDecoder();remaining=raw.strip();objects=[]
 while remaining:
  obj,end=decoder.raw_decode(remaining);assert isinstance(obj,dict) and isinstance(obj.get('args'),dict) and obj.get('tool') in ['list_files','read_file','write_file','run_python','finish']
  objects.append(obj);remaining=remaining[end:].lstrip()
 assert len(objects)>1
 return objects
for p in sorted((R/'runs').glob('main-*/*/summary.json')):
 s=json.loads(p.read_text());meta=json.loads((R/'tasks'/s['task']/'task.json').read_text());work=create(root,R/'tasks'/s['task']/'initial')
 events=[json.loads(x) for x in (p.parent/'trajectory.jsonl').read_text().splitlines()];first=None;progress=[];side_effects=[];mismatches=[];action_history=[]
 for event in events:
  action=event.get('action')
  if not action:
   try:batch=decode_batch(event['raw'])
   except (ValueError,AssertionError):continue
   alternative=R/'runtime/batch-diagnostic';other=create(alternative,work);results=[]
   for proposed in batch:
    if proposed['tool']=='finish':break
    try:results.append(tool(other,alternative,proposed['tool'],proposed['args']))
    except Exception as ex:results.append({'error':type(ex).__name__+': '+str(ex)[:200]})
   batch_diagnostics.append(dict(task=s['task'],condition=s['condition'],turn=event['turn'],proposed_calls=len(batch),tool_results=results,grade_after_executing_batch=grade(meta,alternative),scope='Offline execution of already-generated fully valid JSON objects rejected by single-object parser. Not an observed agent completion rate or a rollout with changed feedback.'))
   continue
  if action['tool']=='finish':continue
  try:result=tool(work,root,action['tool'],action['args'])
  except Exception as ex:result={'error':type(ex).__name__+': '+str(ex)[:1000]}
  old=event.get('tool_result',{})
  # Error strings may contain different absolute audit paths; compare error class/return status.
  if ('error' in result)!=('error' in old) or result.get('returncode',0)!=old.get('returncode',0):mismatches.append(event['turn'])
  action_history.append(dict(turn=event['turn'],tool=action['tool'],args=action['args'],after_first_completion=first is not None))
  if action['tool'] not in ['write_file','run_python']:continue
  before=digest(work);g=grade(meta,root);after=digest(work)
  if before!=after:side_effects.append(event['turn'])
  progress.append(dict(turn=event['turn'],complete=g['complete'],completed_requirements=g['completed_requirements'],total_requirements=g['total_requirements']))
  if g['complete'] and first is None:first=event['turn']
 final_matches=digest(work)==digest(p.parent/'final-workspace')
 records.append(dict(task=s['task'],condition=s['condition'],first_complete_turn=first,progress=progress,post_completion_actions=[x for x in action_history if x['after_first_completion']],replay_error_status_mismatches=mismatches,grader_side_effect_turns=side_effects,final_workspace_matches=final_matches,notes='Post-completion actions can be legitimate verification, not automatically idle looping. Completion inferred by independent tests; actions replayed without model/oracle feedback.'))
 print('REPLAY',s['task'],s['condition'],'first',first,'match',final_matches,flush=True)
(R/'analysis/batch-protocol-diagnostics.json').write_text(json.dumps(batch_diagnostics,indent=2))
(R/'analysis/replay.json').write_text(json.dumps(records,indent=2));assert len(records)==96
assert all(x['final_workspace_matches'] and not x['grader_side_effect_turns'] and not x['replay_error_status_mismatches'] for x in records),'Replay discrepancies require manual investigation'
print('All96 replayed; final states and tool error statuses match',flush=True)
