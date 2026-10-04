import json
from sandbox import R,create
from queue_tasks import make,Queue,expected,grade
checks=[];jobs=[]
for n,seed in [(12,20264001),(24,20264101)]:
 for i in range(3):
  tag=f'queue-confirm-n{n}-s{seed+i}';m=make(n,seed+i,tag);root=R/'runtime/queue-confirm-preflight';work=create(root,R/'tasks'/tag/'initial');state=Queue(m,work)
  for t in m['tickets']:
   state.tool('next_ticket',{});p=work/t['output_path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(expected(t)));state.tool('submit_ticket',{'ticket_id':t['id'],'path':t['output_path']})
  g=grade(m,root,state);assert g['complete'];checks.append({'task':tag,'reference':g});jobs.append([tag,'plan'])
(R/'queues/queue-notes-main.json').write_text(json.dumps(jobs));(R/'analysis/queue-notes-preflight.json').write_text(json.dumps(checks,indent=2));print('PASS six independent sequential workflows',flush=True)
