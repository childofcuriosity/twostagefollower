import subprocess,time,json,os,sys,concurrent.futures
from common import ROOT
jobs=[(c,s) for c in ['base','flat','macro','mismatch'] for s in [11,22,33]]
def worker(gpu):
 results=[]
 for c,s in jobs[gpu::4]:
  with (ROOT/'runs'/f'{c}-s{s}.log').open('w') as log:
   start=time.time();p=subprocess.run([sys.executable,str(ROOT/'src/propose.py'),'--condition',c,'--seed',str(s)],env={**os.environ,'CUDA_VISIBLE_DEVICES':str(gpu)},stdout=log,stderr=subprocess.STDOUT)
  r=dict(condition=c,seed=s,gpu=gpu,returncode=p.returncode,wall_seconds=time.time()-start);results.append(r);print(json.dumps(r),flush=True)
  if p.returncode:break
 return results
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=sum(list(pool.map(worker,range(4))),[])
(ROOT/'analysis/completed.json').write_text(json.dumps(results,indent=2))
assert len(results)==12 and all(r['returncode']==0 for r in results)
