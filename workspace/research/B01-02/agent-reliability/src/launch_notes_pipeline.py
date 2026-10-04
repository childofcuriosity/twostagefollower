import json,os,subprocess,time
from pathlib import Path
R=Path(__file__).resolve().parents[1]
# Wait on completed phase, not repeated GPU/log polling.
while not (R/'analysis/long-batch-completed.json').exists():time.sleep(60)
assert all(x==0 for x in json.loads((R/'analysis/long-batch-completed.json').read_text()).values())
subprocess.run([os.sys.executable,str(R/'src/prepare_notes.py')],check=True)
dev=json.loads((R/'queues/dev.json').read_text());cfg=[]
for gpu,c in enumerate(['plan','identity']):
 tag=f'notes-dev-{c}';(R/'queues'/f'{tag}.json').write_text(json.dumps([[t,c] for t,_ in dev]));cfg.append({'gpu':gpu,'tag':tag,'queue':f'{tag}.json','mode':'zero','script':'native_notes.py'})
p=R/'queues/notes-dev-batch.json';p.write_text(json.dumps(cfg));subprocess.run([os.sys.executable,str(R/'src/launch_batch.py'),str(p)],check=True)
scores={}
for c in ['plan','identity']:
 summaries=[json.loads(p.read_text()) for p in (R/'runs'/f'notes-dev-{c}').glob('*/summary.json')];scores[c]={'n':len(summaries),'complete':sum(s['grade']['complete'] for s in summaries),'protocol_errors':sum(s['stop_reason']=='protocol_failure' for s in summaries)}
(R/'analysis/notes-gate.json').write_text(json.dumps(scores,indent=2))
if not all(s['n']==6 and s['complete']>=5 and s['protocol_errors']==0 for s in scores.values()):raise RuntimeError('Explicit-note calibration needs repair; main not launched')
main=json.loads((R/'queues/notes-main.json').read_text());cfg=[]
for gpu,c in enumerate(['plan','reminder','identity','todo']):
 tag=f'notes-main-{c}';(R/'queues'/f'{tag}.json').write_text(json.dumps([[t,c] for t,_ in main]));cfg.append({'gpu':gpu,'tag':tag,'queue':f'{tag}.json','mode':'zero','script':'native_notes.py'})
p=R/'queues/notes-main-batch.json';p.write_text(json.dumps(cfg));subprocess.run([os.sys.executable,str(R/'src/launch_batch.py'),str(p)],check=True)
