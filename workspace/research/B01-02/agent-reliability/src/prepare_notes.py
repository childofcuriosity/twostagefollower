import json
from sandbox import R,create
from tasks import make,reference,grade
checks=[];jobs=[]
for family in ['files','data','code']:
 for i in range(4):
  tag=f'notes-confirm-{family}-n12-s{i}';m=make(family,12,20263001+i,tag);root=R/'runtime/notes-preflight';work=create(root,R/'tasks'/tag/'initial');reference(m,work);g=grade(m,root);assert g['complete'];checks.append({'task':tag,'reference':g});jobs.append([tag,'plan'])
(R/'queues/notes-main.json').write_text(json.dumps(jobs,indent=2));(R/'analysis/notes-preflight.json').write_text(json.dumps(checks,indent=2))
print('PASS: twelve independent explicit-note tasks')
