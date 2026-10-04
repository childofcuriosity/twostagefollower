import concurrent.futures,subprocess,os,sys,time,json
from common import ROOT
while not (ROOT/'analysis/legacy-completed.json').exists():time.sleep(60)
def job(seed):
 start=time.time()
 with (ROOT/'runs'/f'timecourse-s{seed}.log').open('w') as log:p=subprocess.run([sys.executable,str(ROOT/'src/timecourse.py'),'--seed',str(seed)],env={**os.environ,'CUDA_VISIBLE_DEVICES':str([11,22,33].index(seed))},stdout=log,stderr=subprocess.STDOUT)
 result=dict(seed=seed,returncode=p.returncode,wall_seconds=time.time()-start);print(json.dumps(result),flush=True);return result
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(job,[11,22,33]))
(ROOT/'analysis/timecourse-completed.json').write_text(json.dumps(results,indent=2));assert all(r['returncode']==0 for r in results)
