import concurrent.futures,subprocess,os,sys,time,json
from common import ROOT
jobs=[(d,s) for d in ['digits','strings'] for s in [11,22,33]]
while not (ROOT/'analysis/gradients-completed.json').exists():time.sleep(60)
def worker(slot):
 results=[]
 for d,s in jobs[slot::4]:
  start=time.time()
  with (ROOT/'runs'/f'branch-{d}-legacy-s{s}.log').open('w') as log:p=subprocess.run([sys.executable,str(ROOT/'src/legacy_branch.py'),'--domain',d,'--seed',str(s)],env={**os.environ,'CUDA_VISIBLE_DEVICES':str(slot)},stdout=log,stderr=subprocess.STDOUT)
  r=dict(domain=d,seed=s,returncode=p.returncode,wall_seconds=time.time()-start);results.append(r);print(json.dumps(r),flush=True)
  if p.returncode:break
 return results
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=sum(list(pool.map(worker,range(4))),[])
(ROOT/'analysis/legacy-completed.json').write_text(json.dumps(results,indent=2));assert len(results)==len(jobs) and all(r['returncode']==0 for r in results)
