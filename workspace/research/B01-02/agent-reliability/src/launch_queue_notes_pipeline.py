import json,os,subprocess,time
from pathlib import Path
R=Path(__file__).resolve().parents[1]
subprocess.run([os.sys.executable,str(R/'src/prepare_queue_notes.py')],check=True)
# GPU7 was released by the completed original todo worker.
assert (R/'analysis/queue-main-todo-completed.json').exists()
dev=json.loads((R/'queues/queue-dev.json').read_text());alljobs=[[t,c] for c in ['plan','identity'] for t,_ in dev]
(R/'queues/queue-notes-dev.json').write_text(json.dumps(alljobs));cfg=[{'gpu':7,'tag':'queue-notes-dev','queue':'queue-notes-dev.json','mode':'zero','script':'native_queue_notes.py'}]
p=R/'queues/queue-notes-dev-batch.json';p.write_text(json.dumps(cfg));subprocess.run([os.sys.executable,str(R/'src/launch_batch.py'),str(p)],check=True)
xs=[json.loads(p.read_text()) for p in (R/'runs/queue-notes-dev').glob('*/summary.json')];gate={'n':len(xs),'complete':sum(s['grade']['complete'] for s in xs)};(R/'analysis/queue-notes-gate.json').write_text(json.dumps(gate))
assert gate=={'n':4,'complete':4},'Repair explicit-note queue before main'
while not (R/'analysis/notes-main-batch-completed.json').exists():time.sleep(60)
assert all(x==0 for x in json.loads((R/'analysis/notes-main-batch-completed.json').read_text()).values())
main=json.loads((R/'queues/queue-notes-main.json').read_text());cfg=[]
for gpu,c in enumerate(['plan','reminder','identity','todo']):
 tag=f'queue-notes-main-{c}';(R/'queues'/f'{tag}.json').write_text(json.dumps([[t,c] for t,_ in main]));cfg.append({'gpu':gpu,'tag':tag,'queue':f'{tag}.json','mode':'zero','script':'native_queue_notes.py','wall_seconds':18000})
p=R/'queues/queue-notes-main-batch.json';p.write_text(json.dumps(cfg));subprocess.run([os.sys.executable,str(R/'src/launch_batch.py'),str(p)],check=True)
