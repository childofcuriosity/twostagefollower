import concurrent.futures,subprocess,os,sys,time,json,copy
from common import *
r=ROOT/'coverage';r.mkdir(exist_ok=True);(r/'data').mkdir(exist_ok=True);(r/'runs').mkdir(exist_ok=True)
if not (r/'model').exists():(r/'model').symlink_to(os.path.relpath(PARENT/'model',r),target_is_directory=True)
world=json.loads((PARENT/'data/worlds.json').read_text())['original'];world['library'][8]=['ends','inc','inc']
(r/'data/worlds.json').write_text(json.dumps({'original':world},indent=2))
train=[json.loads(l) for l in (PARENT/'data/train.jsonl').read_text().splitlines()];ss={sig(dsl.expand(row['chain'],world['library'])) for row in train};audit={}
for name in ['train','dev','test']:
 rows=[json.loads(l) for l in (PARENT/f'data/{name}.jsonl').read_text().splitlines()]
 selected=rows if name=='train' else [row for row in rows if row['split']=='iid' or sig(dsl.expand(row['chain'],world['library'])) not in ss]
 (r/f'data/{name}.jsonl').write_text(''.join(json.dumps(row)+'\n' for row in selected));audit[name]={'original':len(rows),'retained':len(selected)}
(r/'data/audit.json').write_text(json.dumps(audit,indent=2))
# Run after diagnostic GPU jobs, without interfering with the registered queues.
# Prerequisite branch scheduler paused while idle; use free GPU0-2 now.
def job(seed):
 start=time.time()
 with (ROOT/'runs'/f'coverage-s{seed}.log').open('w') as log:p=subprocess.run([sys.executable,str(ROOT/'src/coverage.py'),'--seed',str(seed)],env={**os.environ,'CUDA_VISIBLE_DEVICES':str([11,22,33].index(seed))},stdout=log,stderr=subprocess.STDOUT)
 result=dict(seed=seed,returncode=p.returncode,wall_seconds=time.time()-start);print(json.dumps(result),flush=True);return result
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(job,[11,22,33]))
(ROOT/'analysis/coverage-completed.json').write_text(json.dumps(results,indent=2));assert all(r['returncode']==0 for r in results)
