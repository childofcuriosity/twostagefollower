import json,os,subprocess,hashlib
from sandbox import R
assert (R/'analysis/fixed-tools-preflight.json').exists()
main=[]
for i in range(3):
 tag=f'queue-controlled-n24-s{20267001+i}';m=json.loads((R/'tasks'/tag/'task.json').read_text());assert m['seed']==20267001+i and m['n_requirements']==24;main.append([tag,'plan'])
(R/'analysis/controlled-v2-source-fingerprint.json').write_text(json.dumps({str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [R/'src/native_queue_controlled_v2.py',R/'src/fixed_tools.py']},indent=2))
dev=json.loads((R/'queues/queue-dev.json').read_text());cfg=[]
for gpu,policy in enumerate(['full','compact']):
 tag=f'controlled-v2-dev-{policy}';(R/'queues'/f'{tag}.json').write_text(json.dumps([[t,'plan',policy] for t,_ in dev]));cfg.append({'gpu':gpu,'tag':tag,'queue':f'{tag}.json','mode':'zero','script':'native_queue_controlled_v2.py','context_policy':policy})
p=R/'queues/controlled-v2-dev-batch.json';p.write_text(json.dumps(cfg));subprocess.run([os.sys.executable,str(R/'src/launch_batch.py'),str(p)],check=True)
xs=[json.loads(p.read_text()) for d in (R/'runs').glob('controlled-v2-dev-*') for p in d.glob('*/summary.json')];gate={'n':len(xs),'complete':sum(s['grade']['complete'] for s in xs)};(R/'analysis/controlled-v2-gate.json').write_text(json.dumps(gate));assert gate=={'n':4,'complete':4},'Schema-aware fixed-runtime calibration needs repair'
cfg=[]
for gpu,job in enumerate(main):
 tag=f'controlled-v2-main-full-{gpu}';(R/'queues'/f'{tag}.json').write_text(json.dumps([job+['full']]));cfg.append({'gpu':gpu,'tag':tag,'queue':f'{tag}.json','mode':'zero','script':'native_queue_controlled_v2.py','context_policy':'full'})
tag='controlled-v2-main-compacted';(R/'queues'/f'{tag}.json').write_text(json.dumps([[t,c,policy] for t,c in main for policy in ['compact','trim']]))
cfg.append({'gpu':5,'tag':tag,'queue':f'{tag}.json','mode':'zero','script':'native_queue_controlled_v2.py','context_policy':'compact','wall_seconds':18000})
p=R/'queues/controlled-v2-main-batch.json';p.write_text(json.dumps(cfg));subprocess.run([os.sys.executable,str(R/'src/launch_batch.py'),str(p)],check=True)
