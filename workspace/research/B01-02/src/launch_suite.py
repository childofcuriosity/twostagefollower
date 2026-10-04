"""Independent GPU jobs, not assistant subagents and not distributed training."""
import argparse,concurrent.futures,json,os,subprocess,time,queue
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT.parents[2]
ap=argparse.ArgumentParser();ap.add_argument('--steps',type=int,required=True);ap.add_argument('--gpus',default='0,1,2,3');ap.add_argument('--phase',choices=['core','intervention','baseline'],required=True);args=ap.parse_args()
gpus=queue.Queue()
for gpu in args.gpus.split(','):gpus.put(gpu)
if args.phase=='core':jobs=[(c,'original',s,[]) for s in [11,22,33] for c in ['flat','macro','natural','shuffled']]
elif args.phase=='intervention':jobs=[('macro',w,s,[]) for s in [11,22,33] for w in ['renamed','semantic']]
else:jobs=[('frozen','original',11,['--tag=-no-library']),('frozen','original',11,['--with-library','--tag=-with-library'])]
state=ROOT/'analysis'/f'{args.phase}-job-status.jsonl'
def run(job):
 c,w,s,extra=job;tag=next((x.split('=',1)[1] for x in extra if x.startswith('--tag=')),'');name=f'{c}-{w}-s{s}'+tag
 previous=ROOT/'runs'/name
 if (previous/'summary.json').exists():
  old=json.loads((previous/'summary.json').read_text())
  if old['args']['steps']!=args.steps:raise RuntimeError('Completed run has different steps; require explicit new experiment ID')
  return {'job':name,'returncode':0,'reused_completed_run':True}
 if previous.exists():
  archive=ROOT/'runs'/'failed';archive.mkdir(exist_ok=True)
  previous.rename(archive/(name+'-'+str(int(time.time()))))
 oldlog=ROOT/'runs'/f'{name}.log'
 if oldlog.exists():
  archive=ROOT/'runs'/'failed';archive.mkdir(exist_ok=True)
  oldlog.rename(archive/(name+'-'+str(int(time.time()))+'.log'))
 gpu=gpus.get()
 env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=gpu
 cmd=[str(PROJECT/'.training-venv/bin/python'),'-u',str(ROOT/'src/run.py'),'--condition',c,'--world',w,'--seed',str(s),'--steps',str(args.steps)]+extra
 started=time.time()
 try:
  with (ROOT/'runs'/f'{name}.log').open('w') as log:p=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT)
  item={'job':name,'gpu':gpu,'returncode':p.returncode,'started':started,'finished':time.time(),'wall_seconds':time.time()-started}
 finally:gpus.put(gpu)
 with state.open('a') as f:f.write(json.dumps(item)+'\n')
 print(json.dumps(item),flush=True);return item
with concurrent.futures.ThreadPoolExecutor(max_workers=gpus.qsize()) as ex:results=list(ex.map(run,jobs))
(ROOT/'analysis'/f'{args.phase}-completed.json').write_text(json.dumps(results,indent=2))
if any(r['returncode'] for r in results):raise SystemExit(1)
