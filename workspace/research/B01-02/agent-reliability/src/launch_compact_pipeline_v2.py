import json,os,subprocess,time
from pathlib import Path
from sandbox import R,create
from queue_tasks import make,Queue,expected,grade
checks=[];jobs=[]
for i in range(3):
 tag=f'queue-compact-confirm-n24-s{20266001+i}';m=json.loads((R/'tasks'/tag/'task.json').read_text()) if (R/'tasks'/tag/'task.json').exists() else make(24,20266001+i,tag);assert m['seed']==20266001+i and m['n_requirements']==24;root=R/'runtime/compact-preflight';work=create(root,R/'tasks'/tag/'initial');state=Queue(m,work)
 for t in m['tickets']:
  state.tool('next_ticket',{});p=work/t['output_path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(expected(t)));state.tool('submit_ticket',{'ticket_id':t['id'],'path':t['output_path']})
 g=grade(m,root,state);assert g['complete'];checks.append({'task':tag,'reference':g});jobs.append([tag,'plan'])
old=[j for j in json.loads((R/'queues/queue-notes-main.json').read_text()) if 'n24-' in j[0]];assert len(old)==3
(R/'analysis/compact-preflight.json').write_text(json.dumps(checks,indent=2));(R/'queues/compact-main.json').write_text(json.dumps(old+jobs))
for tag in ['notes-replication-plan','notes-replication-identity','notes-replication-todo','queue-notes-main-todo']:
 while not (R/'analysis'/f'{tag}-completed.json').exists():time.sleep(60)
dev=json.loads((R/'queues/queue-dev.json').read_text());(R/'queues/compact-dev.json').write_text(json.dumps([[t,c] for c in ['plan','identity'] for t,_ in dev]))
p=R/'queues/compact-dev-batch.json';p.write_text(json.dumps([{'gpu':4,'tag':'compact-dev','queue':'compact-dev.json','mode':'zero','script':'native_queue_compact.py'}]));subprocess.run([os.sys.executable,str(R/'src/launch_batch.py'),str(p)],check=True)
xs=[json.loads(p.read_text()) for p in (R/'runs/compact-dev').glob('*/summary.json')];gate={'n':len(xs),'complete':sum(s['grade']['complete'] for s in xs)};(R/'analysis/compact-gate.json').write_text(json.dumps(gate))
assert gate=={'n':4,'complete':4},'Compaction calibration needs repair'
cfg=[]
for gpu,c in zip([4,3,6,7],['plan','reminder','identity','todo']):
 tag=f'compact-main-{c}';(R/'queues'/f'{tag}.json').write_text(json.dumps([[t,c] for t,_ in old+jobs]));cfg.append({'gpu':gpu,'tag':tag,'queue':f'{tag}.json','mode':'zero','script':'native_queue_compact.py','wall_seconds':18000})
p=R/'queues/compact-main-batch.json';p.write_text(json.dumps(cfg));subprocess.run([os.sys.executable,str(R/'src/launch_batch.py'),str(p)],check=True)
