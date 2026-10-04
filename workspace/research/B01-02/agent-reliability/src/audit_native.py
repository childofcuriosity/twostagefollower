"""Independent archive regrade and deterministic tool replay; no inference feedback."""
from pathlib import Path
import argparse,hashlib,json,re
from sandbox import R,create
from agent import tool
from tasks import grade
from queue_tasks import Queue,grade as queue_grade
from native import parse,examples,SYSTEM,CONDITIONS
from native_notes import CONDITIONS as NOTE_CONDITIONS
from native_queue_notes import SYSTEM as QUEUE_NOTE_SYSTEM
from native_queue_controlled import SYSTEM as CONTROLLED_SYSTEM
from native_queue_controlled_v2 import SYSTEM as CONTROLLED_V2_SYSTEM
from fixed_tools import tool as fixed_tool,canonical_error

def digest(work):return {str(p.relative_to(work)):hashlib.sha256(p.read_bytes()).hexdigest() for p in work.rglob('*') if p.is_file()}
def samegrade(a,b):return a['complete']==b['complete'] and a['protected_inputs_unchanged']==b['protected_inputs_unchanged'] and [x['passed'] for x in a['checks']]==[x['passed'] for x in b['checks']]
ap=argparse.ArgumentParser();ap.add_argument('--shard',type=int,default=0);ap.add_argument('--shards',type=int,default=1);args=ap.parse_args()
output_name='native-audit.json' if args.shards==1 else f'audit-shard-{args.shard}.json'
previous=json.loads((R/'analysis/native-audit.json').read_text()) if (R/'analysis/native-audit.json').exists() else {'records':[],'raw_sha256':{}}
records=[];hashes={};prior={x['run']:x for x in previous['records']};root=R/'runtime'/f'archive-audit-{args.shard}';replayroot=R/'runtime'/f'native-replay-{args.shard}'
for p in sorted((R/'runs').glob('*/*/summary.json'))[args.shard::args.shards]:
 s=json.loads(p.read_text());meta=json.loads((R/'tasks'/s['task']/'task.json').read_text());events=[json.loads(line) for line in (p.parent/'trajectory.jsonl').read_text().splitlines()];messages=json.loads((p.parent/'messages.json').read_text());isqueue=s['family']=='queue'
 iscontrolledv3=p.parent.parent.name.startswith('controlled-v3-');iscontrolledv2=p.parent.parent.name.startswith('controlled-v2-');iscontrolled=p.parent.parent.name.startswith('controlled-');iscompact=p.parent.parent.name.startswith('compact-') or iscontrolled;isnotes='notes' in p.parent.parent.name or iscompact
 script='native_queue_controlled_v3.py' if iscontrolledv3 else ('native_queue_controlled_v2.py' if iscontrolledv2 else ('native_queue_controlled.py' if iscontrolled else ('native_queue_compact.py' if iscompact else ('native_queue_notes.py' if isqueue and isnotes else ('native_queue.py' if isqueue else ('native_notes.py' if isnotes else 'native.py'))))))
 source=R/'src'/script;assert s['source_sha256']==hashlib.sha256(source.read_bytes()).hexdigest(),p
 runkey=str(p.parent.relative_to(R));audit_files=[p,p.parent/'messages.json',p.parent/'trajectory.jsonl']+([p.parent/'queue-state.json'] if isqueue else [])+([p.parent/'compactions.json'] if iscompact else [])+[q for q in (p.parent/'final-workspace').rglob('*') if q.is_file()];known={k:v for k,v in previous['raw_sha256'].items() if k.startswith(runkey+'/')}
 if runkey in prior and set(known)=={str(q.relative_to(R)) for q in audit_files} and known and all((R/k).exists() and hashlib.sha256((R/k).read_bytes()).hexdigest()==h for k,h in known.items()):
  records.append(prior[runkey]);hashes.update(known);continue
 assert sum(e['generated_tokens'] for e in events)==s['generated_tokens'];assert sum(e['input_tokens'] for e in events)==s['input_tokens'];assert [e['turn'] for e in events]==list(range(len(events)))
 offset=1+(len(examples()) if s['mode']=='fewshot' else 0)
 assert messages[0]['content']==(CONTROLLED_V2_SYSTEM if (iscontrolledv2 or iscontrolledv3) else (CONTROLLED_SYSTEM if iscontrolled else (QUEUE_NOTE_SYSTEM if isqueue and isnotes else SYSTEM)))+'\n'+(NOTE_CONDITIONS if isnotes else CONDITIONS)[s['condition']];assert messages[offset]=={'role':'user','content':meta['user']}
 assistants=[m for m in messages[offset+1:] if m['role']=='assistant'];assert iscompact or len(assistants)==len(events)
 for m,e in ([] if iscompact else zip(assistants,events)):
  if 'protocol_error' in e:assert m['content']==e['raw']
  else:assert m['content']==e['content'] and m.get('tool_calls',[])==e['tool_calls']
 archived=p.parent/'final-workspace';work=create(root,archived)
 if isqueue:
  saved=json.loads((p.parent/'queue-state.json').read_text());state=Queue(meta,work);state.opened=saved['opened'];state.receipts=saved['receipts'];g=queue_grade(meta,root,state)
 else:g=grade(meta,root)
 assert samegrade(g,s['grade']),(p,g,s['grade'])
 work=create(replayroot,R/'tasks'/s['task']/'initial');state=Queue(meta,work) if isqueue else None;progress=[];mismatches=[];value_mismatches=[];first=None;history=[];statuses=[]
 compactions={c['before_turn']:c for c in json.loads((p.parent/'compactions.json').read_text())} if iscompact else {}
 reconstructed=messages[:2]
 for e in events:
  if iscompact:
   if e['turn'] in compactions:
    comp=compactions[e['turn']];ids=[r['ticket_id'] for r in state.receipts];assert comp['retained_ids']==ids and comp['delivered']==len(ids)
    expected_ledger='Workspace handoff summary from observed tool receipts: '+str(len(ids))+'/'+str(meta['n_requirements'])+' tickets delivered: '+', '.join(ids)+'. Receipt is not a correctness check. The original request remains active. Continue with next_ticket until all requested tickets are delivered, then verify completion. Previous files remain in the workspace; use tools if you need to inspect them.'
    assert comp['ledger']==expected_ledger
    last=max(i for i,m in enumerate(reconstructed) if m['role']=='assistant');tail=reconstructed[last:];assert comp['discarded_messages']==len(reconstructed)-2-len(tail)
    reconstructed=reconstructed[:2]+([{'role':'user','content':comp['ledger']}] if comp.get('ledger_injected',True) else [])+tail
   assert e['prompt_messages']==reconstructed,('prompt reconstruction mismatch',p,e['turn'])
   if 'protocol_error' in e:reconstructed.extend([{'role':'assistant','content':e['raw']},{'role':'user','content':'Protocol error; no malformed calls executed. '+json.dumps(e['protocol_error'])}])
   else:
    m={'role':'assistant','content':e.get('history_content',e['content'])}
    if e['tool_calls']:m['tool_calls']=e['tool_calls']
    reconstructed.append(m)
    for result in e.get('tool_results',[]):reconstructed.append({'role':'tool','name':result['tool'],'content':json.dumps(result['result'])})
  statuses.append({'turn':e['turn'],'content':e.get('content',''),'task_ids':sorted(set(re.findall(r'\bT\d{2}\b',e.get('content','')))),'calls':len(e.get('tool_calls',[])), 'tool_notes':[c['function']['arguments'].get('note') for c in e.get('tool_calls',[])]})
  for c,old in zip(e.get('tool_calls',[]),e.get('tool_results',[])):
   f=c['function'];name=f['name'];args={k:v for k,v in f['arguments'].items() if k!='note'} if isnotes else f['arguments'];before_complete=first is not None
   try:result=state.tool(name,args) if name in ['next_ticket','submit_ticket'] else (fixed_tool if iscontrolled else tool)(work,replayroot,name,args)
   except Exception as ex:result=canonical_error(ex,work) if iscontrolled else {'error':type(ex).__name__+': '+str(ex)[:1000]}
   if ('error' in result)!=('error' in old['result']) or result.get('returncode',0)!=old['result'].get('returncode',0):mismatches.append({'turn':e['turn'],'tool':name})
   if result!=old['result']:value_mismatches.append({'turn':e['turn'],'tool':name,'old':old['result'],'replayed':result})
   history.append({'turn':e['turn'],'tool':name,'after_first_complete':before_complete})
   if name in ['write_file','run_python','submit_ticket']:
    before=digest(work);now=queue_grade(meta,replayroot,state) if isqueue else grade(meta,replayroot);assert digest(work)==before,'grader mutated workspace'
    progress.append({'turn':e['turn'],'tool':name,'complete':now['complete'],'correct':now['completed_requirements']})
    if now['complete'] and first is None:first=e['turn']
 if iscompact and len(events) in compactions:
  comp=compactions[len(events)];ids=[r['ticket_id'] for r in state.receipts];assert comp['retained_ids']==ids and comp['delivered']==len(ids)
  expected_ledger='Workspace handoff summary from observed tool receipts: '+str(len(ids))+'/'+str(meta['n_requirements'])+' tickets delivered: '+', '.join(ids)+'. Receipt is not a correctness check. The original request remains active. Continue with next_ticket until all requested tickets are delivered, then verify completion. Previous files remain in the workspace; use tools if you need to inspect them.'
  assert comp['ledger']==expected_ledger
  last=max(i for i,m in enumerate(reconstructed) if m['role']=='assistant');tail=reconstructed[last:];assert comp['discarded_messages']==len(reconstructed)-2-len(tail)
  reconstructed=reconstructed[:2]+([{'role':'user','content':comp['ledger']}] if comp.get('ledger_injected',True) else [])+tail
 if iscompact:assert reconstructed==messages
 assert digest(work)==digest(archived),('replay differs',p)
 assert not mismatches,(p,mismatches)
 if iscontrolled:assert not value_mismatches,('Controlled tool-result mismatch',p,value_mismatches)
 if isqueue:assert state.receipts==saved['receipts'] and state.opened==saved['opened']
 failure=[]
 specs=meta['tickets'] if isqueue else meta['specs']
 for spec,check in zip(specs,g['checks']):
  if check['passed']:continue
  rel=spec['output_path'] if isqueue else spec['path'];q=archived/rel;initial=R/'tasks'/s['task']/'initial'/rel
  kind='missing' if not q.exists() else ('unchanged' if initial.exists() and q.read_bytes()==initial.read_bytes() else 'written_incorrect')
  failure.append({'id':check['id'],'path':rel,'kind':kind,'detail':check['detail']})
 records.append({'run':str(p.parent.relative_to(R)),'task':s['task'],'condition':s['condition'],'mode':s['mode'],'category':s['category'],'regraded':True,'replay_matches':True,'tool_result_value_mismatches':value_mismatches,'first_complete_turn':first,'progress':progress,'post_completion_actions':[x for x in history if x['after_first_complete']],'status_observations':statuses,'failures':failure})
 for q in audit_files:
  if q.is_file():hashes[str(q.relative_to(R))]=hashlib.sha256(q.read_bytes()).hexdigest()
 print('AUDITED',p.parent.parent.name,s['task'],s['category'],flush=True)
(R/'analysis'/output_name).write_text(json.dumps({'records':records,'count':len(records),'raw_sha256':hashes},indent=2))
print('PASS',len(records),'archive regrades and exact filesystem replays',flush=True)
