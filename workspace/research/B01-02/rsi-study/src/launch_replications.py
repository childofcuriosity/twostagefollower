import concurrent.futures,subprocess,os,sys,time,json
from common import ROOT
jobs=[(m,c,s) for m in ['qwen3b','smol1.7b'] for c in ['flat','macro'] for s in [11,22,33]]+[(m,'frozen',11) for m in ['qwen3b','smol1.7b']]
def worker(slot):
 results=[]
 for m,c,s in jobs[slot::4]:
  ready=ROOT/'models'/m/'download-manifest.json'
  while not ready.exists():time.sleep(60)
  start=time.time()
  with (ROOT/'runs'/f'replicate-{m}-{c}-s{s}.log').open('w') as log:
   p=subprocess.run([sys.executable,str(ROOT/'src/replicate.py'),'--model',m,'--condition',c,'--seed',str(s)],env={**os.environ,'CUDA_VISIBLE_DEVICES':str(slot+4)},stdout=log,stderr=subprocess.STDOUT)
  r=dict(model=m,condition=c,seed=s,returncode=p.returncode,wall_seconds=time.time()-start);print(json.dumps(r),flush=True);results.append(r)
  if p.returncode:break
 return results
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=sum(list(pool.map(worker,range(4))),[])
(ROOT/'analysis/replications-completed.json').write_text(json.dumps(results,indent=2))
assert len(results)==len(jobs) and all(r['returncode']==0 for r in results)
