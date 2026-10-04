import json
from sandbox import R,create
from tasks import make,reference,grade
jobs=[];checks=[]
for family in ['files','data','code']:
 for i in range(12):
  tag=f'notes-replication-{family}-n12-s{i:02d}';m=make(family,12,20265001+i,tag);root=R/'runtime/notes-replication-preflight';work=create(root,R/'tasks'/tag/'initial');reference(m,work);g=grade(m,root);assert g['complete'];checks.append({'task':tag,'reference':g});jobs.append([tag,'plan'])
(R/'analysis/notes-replication-preflight.json').write_text(json.dumps(checks,indent=2));cfg=[]
for gpu,c in enumerate(['plan','reminder','identity','todo'],4):
 tag=f'notes-replication-{c}';(R/'queues'/f'{tag}.json').write_text(json.dumps([[t,c] for t,_ in jobs]));cfg.append({'gpu':gpu,'tag':tag,'queue':f'{tag}.json','mode':'zero','script':'native_notes.py','wall_seconds':18000})
(R/'queues/notes-replication-batch.json').write_text(json.dumps(cfg,indent=2));print('PASS 36 fixed independent replication tasks',flush=True)
