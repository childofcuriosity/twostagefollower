import json,os,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]
for name in ['queue-notes-main-batch','notes-replication-batch','compact-main-batch','controlled-v2-main-batch','controlled-v3-main-batch']:
 p=R/'analysis'/f'{name}-completed.json';assert p.exists() and all(v==0 for v in json.loads(p.read_text()).values()),name
workers=[]
for i in range(4):
 log=(R/'logs'/f'audit-shard-{i}.log').open('w');p=subprocess.Popen([os.sys.executable,str(R/'src/audit_native.py'),'--shard',str(i),'--shards','4'],stdout=log,stderr=subprocess.STDOUT);workers.append((p,log))
for p,log in workers:assert p.wait()==0,'Audit discrepancy; inspect shard logs';log.close()
records=[];hashes={}
for i in range(4):
 x=json.loads((R/'analysis'/f'audit-shard-{i}.json').read_text());records+=x['records'];assert not set(hashes)&set(x['raw_sha256']);hashes.update(x['raw_sha256'])
actual={str(p.parent.relative_to(R)) for p in (R/'runs').glob('*/*/summary.json')};assert {r['run'] for r in records}==actual and len(records)==len(actual)
(R/'analysis/native-audit.json').write_text(json.dumps({'records':records,'count':len(records),'raw_sha256':hashes},indent=2))
print('PASS all',len(records),'trajectories independently regraded and replayed')
