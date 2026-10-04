from common import *
import subprocess,os,time,concurrent.futures,queue
jobs=json.loads((R/'analysis/jobs.json').read_text())
# Six large runs immediately; two GPUs consume all smaller jobs, avoiding queue starvation.
big=queue.Queue();small=queue.Queue()
for i,j in enumerate(jobs):(big if j['model']=='qwen32b' else small).put(i)
def work(gpu,q):
 results=[]
 while True:
  try:i=q.get_nowait()
  except queue.Empty:break
  j=jobs[i];name=f'{j["model"]}-{j["condition"]}-s{j["seed"]}';env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu);start=time.time()
  with (R/'logs'/f'{name}.log').open('x') as log:p=subprocess.run([sys.executable,'-u',str(R/'src/worker.py'),'--job',str(i)],env=env,stdout=log,stderr=subprocess.STDOUT)
  rec=dict(job=j,gpu=gpu,returncode=p.returncode,seconds=time.time()-start,finished=time.time());write(R/'analysis'/f'exit-{name}.json',rec);print(json.dumps(rec),flush=True);results.append(rec)
  if p.returncode:break
 return results
start=time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
 futures=[pool.submit(work,g,big if g<6 else small) for g in range(8)]
 results=[]
 for f in concurrent.futures.as_completed(futures):results.extend(f.result())
write(R/'analysis/dispatch.json',dict(results=results,seconds=time.time()-start))
if len(results)!=24 or any(x['returncode'] for x in results):
 write(R/'analysis/pipeline-failed.json',dict(reason='Incomplete/failed jobs; raw runs retained',finished=time.time()));raise SystemExit(1)
write(R/'analysis/training-and-inference-complete.json',dict(jobs=24,finished=time.time()))
# Analysis is installed before this event; no healthy-job polling.
p=subprocess.run([sys.executable,str(R/'src/analyze.py')])
if p.returncode:
 write(R/'analysis/pipeline-failed.json',dict(reason='Analysis failure',finished=time.time()));raise SystemExit(p.returncode)
write(R/'analysis/pipeline-complete.json',dict(finished=time.time(),note='All computation/audit complete; scientific review required before goal complete.'))
