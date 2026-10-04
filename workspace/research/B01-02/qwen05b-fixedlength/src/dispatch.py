from common import *
import argparse,concurrent.futures,os,queue,subprocess,time

p=argparse.ArgumentParser();p.add_argument('--length',type=int,required=True);p.add_argument('--phase',choices=('explore','formal'),required=True);p.add_argument('--conditions',nargs='+',choices=CONDITIONS);p.add_argument('--gpus',type=int,default=8);a=p.parse_args()
conditions=a.conditions or (('flat','macro') if a.phase=='explore' else CONDITIONS)
seeds=EXPLORE_SEEDS if a.phase=='explore' else FORMAL_SEEDS
jobs=queue.Queue()
for c in conditions:
 for seed in seeds:jobs.put((c,seed))
(R/'logs').mkdir(exist_ok=True)
def lane(gpu):
 out=[]
 while True:
  try:c,seed=jobs.get_nowait()
  except queue.Empty:break
  name=f'{a.phase}-L{a.length}-{c}-s{seed}';log=R/'logs'/f'{name}.log'
  env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu);start=time.time()
  with log.open('x') as f:
   proc=subprocess.run([sys.executable,'-u',str(R/'src/worker.py'),'--length',str(a.length),'--phase',a.phase,'--condition',c,'--seed',str(seed)],env=env,stdout=f,stderr=subprocess.STDOUT)
  rec=dict(length=a.length,phase=a.phase,condition=c,seed=seed,gpu=gpu,exit_code=proc.returncode,seconds=time.time()-start,log=str(log.relative_to(R)),finished=time.time())
  write(R/'analysis'/f'exit-{name}.json',rec);print(json.dumps(rec),flush=True);out.append(rec)
  if proc.returncode:break
 return out
results=[];start=time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=a.gpus) as pool:
 for f in concurrent.futures.as_completed([pool.submit(lane,gpu) for gpu in range(a.gpus)]):results+=f.result()
write(R/'analysis'/f'dispatch-{a.phase}-L{a.length}-{"-".join(conditions)}.json',dict(results=results,seconds=time.time()-start))
if len(results)!=len(seeds)*len(conditions) or any(x['exit_code'] for x in results):raise SystemExit(1)
