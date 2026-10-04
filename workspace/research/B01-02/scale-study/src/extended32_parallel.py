from pathlib import Path
import json,time,subprocess,os,sys,queue,concurrent.futures
R=Path(__file__).resolve().parents[1];marker=R/'analysis/qwen32b-completed.json'
while not marker.exists():time.sleep(60)
records=json.loads(marker.read_text());assert len(records)==6 and all(x['returncode']==0 for x in records)
tags=['frozen-with-library']+[f'{c}-s{s}' for s in [11,22,33] for c in ['flat','macro']];pending=queue.Queue()
for tag in tags:pending.put(tag)
def worker(gpu):
 results=[]
 while True:
  try:tag=pending.get_nowait()
  except queue.Empty:return results
  env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu);start=time.time()
  with (R/'runs'/f'extended-qwen32b-{tag}.log').open('x') as f:
   p=subprocess.run([sys.executable,'-u',str(R/'src/extended32_worker.py'),'--tag',tag],env=env,stdout=f,stderr=subprocess.STDOUT)
  rec=dict(tag=tag,gpu=gpu,returncode=p.returncode,wall_seconds=time.time()-start);results.append(rec);print(json.dumps(rec),flush=True)
  if p.returncode:return results
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:records=sum(list(pool.map(worker,[0,1,2,3,7])),[])
(R/'analysis/parallel-extended32-completed.json').write_text(json.dumps(records,indent=2));assert len(records)==7 and all(x['returncode']==0 for x in records)
metas=[json.loads((R/f'extended/qwen32b/{tag}-summary.json').read_text()) for tag in tags]
assert all(x['records']==480 for x in metas)
p=R/'extended/qwen32b/completed.json';tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(metas,indent=2));tmp.replace(p);print('All independent32B passes complete',flush=True)
