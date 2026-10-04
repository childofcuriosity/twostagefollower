import concurrent.futures,subprocess,os,sys,time,json
from common import ROOT
jobs=[('digits',c,s) for c in ['shared','frozen','replay','joint','shuffled'] for s in [11,22,33]]+[('strings',c,s) for c in ['shared','frozen','joint'] for s in [11,22,33]]
while not (ROOT/'analysis/replications-completed.json').exists():time.sleep(60)
# Separate GPU slots from the concurrently running prompt robustness jobs.
def worker(slot):
 results=[]
 for domain,c,s in jobs[slot::4]:
  start=time.time()
  with (ROOT/'runs'/f'loop-{domain}-{c}-s{s}.log').open('w') as log:p=subprocess.run([sys.executable,str(ROOT/'src/loop.py'),'--domain',domain,'--condition',c,'--seed',str(s)],env={**os.environ,'CUDA_VISIBLE_DEVICES':str(slot+4)},stdout=log,stderr=subprocess.STDOUT)
  r=dict(domain=domain,condition=c,seed=s,returncode=p.returncode,wall_seconds=time.time()-start);print(json.dumps(r),flush=True);results.append(r)
  if p.returncode:break
 return results
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=sum(list(pool.map(worker,range(4))),[])
(ROOT/'analysis/loops-completed.json').write_text(json.dumps(results,indent=2));assert len(results)==len(jobs) and all(r['returncode']==0 for r in results)
