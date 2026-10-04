import concurrent.futures,subprocess,os,sys,time,json
from common import ROOT
jobs=[(d,source,s) for d in ['digits','strings'] for source in ['updated','base'] for s in [11,22,33]]
while not (ROOT/'analysis/robust-completed.json').exists():time.sleep(60)
def worker(slot):
 results=[]
 for d,source,s in jobs[slot::4]:
  while not (ROOT/'runs'/f'loop-{d}-shared-s{s}'/'round1/summary.json').exists():time.sleep(60)
  start=time.time()
  with (ROOT/'runs'/f'branch-{d}-{source}-s{s}.log').open('w') as log:p=subprocess.run([sys.executable,str(ROOT/'src/branch.py'),'--domain',d,'--source',source,'--seed',str(s)],env={**os.environ,'CUDA_VISIBLE_DEVICES':str(slot)},stdout=log,stderr=subprocess.STDOUT)
  r=dict(domain=d,source=source,seed=s,returncode=p.returncode,wall_seconds=time.time()-start);print(json.dumps(r),flush=True);results.append(r)
  if p.returncode:break
 return results
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=sum(list(pool.map(worker,range(4))),[])
(ROOT/'analysis/branches-completed.json').write_text(json.dumps(results,indent=2));assert len(results)==len(jobs) and all(r['returncode']==0 for r in results)
