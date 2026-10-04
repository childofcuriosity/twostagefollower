import json
from sandbox import R,create
from tasks import make,reference,grade
records=[];queues={'short':[],'long':[]}
for length,n,seed in [('short',4,20261101),('long',12,20261201)]:
 for family in ['files','data','code']:
  for i in range(4):
   tag=f'validation-{family}-n{n:02d}-s{i}';meta=make(family,n,seed+i,tag)
   root=R/'runtime/validation-preflight';work=create(root,R/'tasks'/tag/'initial');reference(meta,work);g=grade(meta,root);assert g['complete'],g
   records.append({'task':tag,'reference':g});queues[length].append([tag,'plan'])
for k,v in queues.items():(R/'queues'/f'validation-{k}.json').write_text(json.dumps(v,indent=2))
(R/'analysis/validation-preflight.json').write_text(json.dumps(records,indent=2))
print('PASS: 24 independent short/long reference tasks')
