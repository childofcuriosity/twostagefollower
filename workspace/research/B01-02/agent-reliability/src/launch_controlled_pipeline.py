import json,os,subprocess
from pathlib import Path
from sandbox import R,create
from queue_tasks import make,Queue,expected,grade
from fixed_tools import tool,canonical_error
# Check fixed clock/random output in two independent workspaces and canonical errors.
meta=json.loads((R/'tasks/queue-dev-n04-s20262001/task.json').read_text());outputs=[];errors=[]
for name in ['fixed-check-a','fixed-check-b']:
 root=R/'runtime'/name;work=create(root,R/'tasks'/meta['id']/'initial');outputs.append(tool(work,root,'run_python',{'code':'from datetime import datetime,date\nimport time,random,os,uuid\nprint(datetime.now(),date.today(),time.time(),random.random(),os.urandom(8).hex(),uuid.uuid4())'}))
 try:tool(work,root,'read_file',{'path':'missing.json'})
 except Exception as e:errors.append(canonical_error(e,work))
assert outputs[0]==outputs[1] and outputs[0]['returncode']==0,outputs
assert errors[0]==errors[1] and '/workspace/' in errors[0]['error']
(R/'analysis/fixed-tools-preflight.json').write_text(json.dumps({'outputs':outputs,'canonical_errors':errors},indent=2))
checks=[];main=[]
for i in range(3):
 tag=f'queue-controlled-n24-s{20267001+i}';m=make(24,20267001+i,tag);root=R/'runtime/controlled-preflight';work=create(root,R/'tasks'/tag/'initial');state=Queue(m,work)
 for t in m['tickets']:
  state.tool('next_ticket',{});p=work/t['output_path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(expected(t)));state.tool('submit_ticket',{'ticket_id':t['id'],'path':t['output_path']})
 g=grade(m,root,state);assert g['complete'];checks.append({'task':tag,'reference':g});main.append([tag,'plan'])
(R/'analysis/controlled-preflight.json').write_text(json.dumps(checks,indent=2));dev=json.loads((R/'queues/queue-dev.json').read_text());cfg=[]
for gpu,policy in enumerate(['full','compact']):
 tag=f'controlled-dev-{policy}';(R/'queues'/f'{tag}.json').write_text(json.dumps([[t,'plan',policy] for t,_ in dev]));cfg.append({'gpu':gpu,'tag':tag,'queue':f'{tag}.json','mode':'zero','script':'native_queue_controlled.py','context_policy':policy})
p=R/'queues/controlled-dev-batch.json';p.write_text(json.dumps(cfg));subprocess.run([os.sys.executable,str(R/'src/launch_batch.py'),str(p)],check=True)
xs=[json.loads(p.read_text()) for d in (R/'runs').glob('controlled-dev-*') for p in d.glob('*/summary.json')];gate={'n':len(xs),'complete':sum(s['grade']['complete'] for s in xs)};(R/'analysis/controlled-gate.json').write_text(json.dumps(gate));assert gate=={'n':4,'complete':4},'Fixed-runtime calibration needs repair'
cfg=[]
for gpu,job in enumerate(main):
 tag=f'controlled-main-full-{gpu}';(R/'queues'/f'{tag}.json').write_text(json.dumps([job+['full']]));cfg.append({'gpu':gpu,'tag':tag,'queue':f'{tag}.json','mode':'zero','script':'native_queue_controlled.py','context_policy':'full'})
tag='controlled-main-compacted';(R/'queues'/f'{tag}.json').write_text(json.dumps([[t,c,policy] for t,c in main for policy in ['compact','trim']]))
cfg.append({'gpu':5,'tag':tag,'queue':f'{tag}.json','mode':'zero','script':'native_queue_controlled.py','context_policy':'compact','wall_seconds':18000})
p=R/'queues/controlled-main-batch.json';p.write_text(json.dumps(cfg));subprocess.run([os.sys.executable,str(R/'src/launch_batch.py'),str(p)],check=True)
