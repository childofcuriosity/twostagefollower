from common import *
import argparse,concurrent.futures,os,queue,subprocess,time

p=argparse.ArgumentParser();p.add_argument('--condition',choices=CONDITIONS,required=True);p.add_argument('--max-length',type=int,default=2,choices=range(2,9));a=p.parse_args()
q=queue.Queue()
for seed in SEEDS:q.put(seed)
def lane(gpu):
 out=[]
 while True:
  try:seed=q.get_nowait()
  except queue.Empty:break
  name=f'L{a.max_length}-{a.condition}-s{seed}';log=R/'logs'/f'{name}.log'
  env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu);start=time.time()
  with log.open('x') as f:proc=subprocess.run([sys.executable,'-u',str(R/'src/worker.py'),'--condition',a.condition,'--seed',str(seed),'--max-length',str(a.max_length)],env=env,stdout=f,stderr=subprocess.STDOUT)
  record=dict(condition=a.condition,seed=seed,gpu=gpu,exit_code=proc.returncode,seconds=time.time()-start,finished=time.time(),log=str(log.relative_to(R)))
  write(R/'analysis'/f'exit-{name}.json',record);print(json.dumps(record),flush=True);out.append(record)
  if proc.returncode:break
 return out
(R/'logs').mkdir(exist_ok=True)
start=time.time();results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
 for f in concurrent.futures.as_completed([pool.submit(lane,gpu) for gpu in range(8)]):results+=f.result()
write(R/'analysis'/f'dispatch-L{a.max_length}-{a.condition}.json',dict(results=results,seconds=time.time()-start))
if len(results)!=len(SEEDS) or any(x['exit_code'] for x in results):raise SystemExit(1)
