import concurrent.futures,subprocess,os,sys,time,json
from common import ROOT
jobs=[(m,c,s) for m in ['qwen1.5b','qwen3b','smol1.7b'] for c in ['base','flat','macro'] for s in [11,22,33]]
while not (ROOT/'analysis/coverage-completed.json').exists():time.sleep(60)
def worker(slot):
 results=[]
 for m,c,s in jobs[slot::4]:
  start=time.time()
  with (ROOT/'runs'/f'length-{m}-{c}-s{s}.log').open('w') as log:p=subprocess.run([sys.executable,str(ROOT/'src/length_control.py'),'--model',m,'--condition',c,'--seed',str(s)],env={**os.environ,'CUDA_VISIBLE_DEVICES':str(slot)},stdout=log,stderr=subprocess.STDOUT)
  r=dict(model=m,condition=c,seed=s,returncode=p.returncode,wall_seconds=time.time()-start);results.append(r);print(json.dumps(r),flush=True)
  if p.returncode:break
 return results
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=sum(list(pool.map(worker,range(4))),[])
(ROOT/'analysis/length-completed.json').write_text(json.dumps(results,indent=2));assert len(results)==len(jobs) and all(r['returncode']==0 for r in results)
