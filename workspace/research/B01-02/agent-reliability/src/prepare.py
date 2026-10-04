import json,shutil,hashlib
from sandbox import R,create,execute
from tasks import make,reference,grade
from native import parse,examples,TOOLS
checks=[];jobs=[]
for family in ['files','data','code']:
 for i in range(2):
  tag=f'dev-{family}-n04-s{i}';meta=make(family,4,20261001+i,tag);jobs.append([tag,'plan'])
  root=R/'runtime/preflight';work=create(root,R/'tasks'/tag/'initial');reference(meta,work);g=grade(meta,root);assert g['complete'],g
  for spec in meta['specs']:
   p=work/spec['path'];old=p.read_bytes();p.unlink();missing=grade(meta,root);assert not missing['complete'];p.write_bytes(old)
  checks.append({'task':tag,'reference':g,'omission_checks':len(meta['specs'])})
assert len(parse('<tool_call>{"name":"list_files","arguments":{}}</tool_call>')[1])==1
for bad in ['<tool_call>{"name":"list_files","arguments":{}}','<tool_call>{"name":"write_file","arguments":{}}</tool_call>']:
 try:parse(bad)
 except ValueError:pass
 else:raise AssertionError(bad)
# Execute demonstration snippets inside a separate example workspace.
initial=R/'runtime/example-input';initial.mkdir();(initial/'notes.txt').write_text('alpha\nbeta\n');root=R/'runtime/preflight';create(root,initial)
for m in examples():
 for c in m.get('tool_calls',[]):
  f=c['function']
  if f['name']=='run_python':
   result=execute(root,f['arguments']['code']);assert result['returncode']==0,result
(R/'queues/dev.json').write_text(json.dumps(jobs,indent=2))
(R/'analysis/preflight.json').write_text(json.dumps({'task_checks':checks,'parser_checks':'pass','example_execution':'pass'},indent=2))
print('PASS: six reference tasks, 24 omission checks, native parser and executable example',flush=True)
