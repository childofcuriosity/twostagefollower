from common import *
import concurrent.futures,os,queue,subprocess,time,traceback

jobs=json.loads((R/'analysis/jobs.json').read_text())
assert len(jobs)==204
(R/'logs').mkdir(exist_ok=True)
pending=queue.Queue()
for model in ('qwen7b','qwen3b','qwen1.5b'):
 for i,job in enumerate(jobs):
  if job['model']==model:pending.put(i)

def lane(gpu):
 completed=[]
 while True:
  try:i=pending.get_nowait()
  except queue.Empty:break
  job=jobs[i];name=f"{job['model']}-{job['condition']}-s{job['seed']}"
  env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu)
  start=time.time();logpath=R/'logs'/f'{name}.log'
  write(R/'analysis'/f'running-{name}.json',dict(job=job,gpu=gpu,started=start))
  try:
   with logpath.open('x') as log:
    p=subprocess.run([sys.executable,'-u',str(R/'src/worker.py'),'--job',str(i)],env=env,stdout=log,stderr=subprocess.STDOUT)
   result=dict(job=job,gpu=gpu,returncode=p.returncode,seconds=time.time()-start,finished=time.time(),log=str(logpath.relative_to(R)))
  except BaseException as e:
   result=dict(job=job,gpu=gpu,returncode=-1,seconds=time.time()-start,finished=time.time(),error=repr(e),traceback=traceback.format_exc())
  write(R/'analysis'/f'exit-{name}.json',result)
  (R/'analysis'/f'running-{name}.json').unlink(missing_ok=True)
  print(json.dumps(result),flush=True)
  completed.append(result)
  if result['returncode']!=0:break
 return completed

start=time.time();results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
 futures=[pool.submit(lane,gpu) for gpu in range(8)]
 for f in concurrent.futures.as_completed(futures):results.extend(f.result())
write(R/'analysis/dispatch.json',dict(results=results,seconds=time.time()-start))
if len(results)!=len(jobs) or any(x['returncode'] for x in results):
 write(R/'analysis/pipeline-failed.json',dict(reason='Incomplete or failed jobs; outputs preserved',completed=len(results),expected=len(jobs),finished=time.time()))
 raise SystemExit(1)
write(R/'analysis/training-complete.json',dict(jobs=len(results),finished=time.time()))
p=subprocess.run([sys.executable,str(R/'src/analyze.py')])
if p.returncode:
 write(R/'analysis/pipeline-failed.json',dict(reason='Analysis failed',returncode=p.returncode,finished=time.time()))
 raise SystemExit(p.returncode)
write(R/'analysis/pipeline-complete.json',dict(finished=time.time(),jobs=len(results),note='Analysis and audit complete; interpretation in report.'))
