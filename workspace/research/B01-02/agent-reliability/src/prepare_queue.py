import json,os
from sandbox import R,create
from queue_tasks import make,Queue,expected,grade
records=[];dev=[];main=[]
for n,seeds,split in [(4,[20262001,20262002],'dev'),(12,[20262101,20262102,20262103],'main'),(24,[20262201,20262202,20262203],'main')]:
 for seed in seeds:
  tag=f'queue-{split}-n{n:02d}-s{seed}';meta=make(n,seed,tag);root=R/'runtime/queue-preflight';work=create(root,R/'tasks'/tag/'initial');state=Queue(meta,work)
  for ticket in meta['tickets']:
   obs=state.tool('next_ticket',{});assert obs['id']==ticket['id'] and 'records' not in obs
   p=work/ticket['output_path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(expected(ticket)))
   receipt=state.tool('submit_ticket',{'ticket_id':ticket['id'],'path':ticket['output_path']});assert not receipt['correctness_checked']
  assert state.tool('next_ticket',{})['queue_empty'];g=grade(meta,root,state);assert g['complete'],g
  # A wrong submitted result is accepted by workflow, but rejected independently.
  saved=state.receipts[0]['content'];state.receipts[0]['content']='{}';assert not grade(meta,root,state)['complete'];state.receipts[0]['content']=saved
  saved=state.receipts.pop();assert not grade(meta,root,state)['complete'];state.receipts.append(saved)
  records.append({'task':tag,'reference':g,'wrong_delivery_and_omission':'rejected by grader'})
  (dev if split=='dev' else main).append([tag,'plan'])
for name,q in [('queue-dev',dev),('queue-main',main)]:(R/'queues'/f'{name}.json').write_text(json.dumps(q,indent=2))
(R/'analysis/queue-preflight.json').write_text(json.dumps(records,indent=2));print('PASS: 8 sequential workflow references, wrong-delivery and missing-receipt rejection')
