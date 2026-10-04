import json,os,subprocess,sys,time,concurrent.futures,hashlib,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--model',choices=['qwen32b','qwen7b'],required=True);a=ap.parse_args()
gpus=[0,1,2] if a.model=='qwen32b' else [4,5,6]
def call(condition,seed,gpu,micro,tag='',probe=False):
 env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu)
 cmd=[sys.executable,'-u',str(ROOT/'src/train.py'),'--model',a.model,'--condition',condition,'--seed',str(seed),'--microbatch',str(micro),'--accum',str(32//micro)]
 if tag:cmd+=['--tag='+tag]
 if probe:cmd+=['--probe-only','--steps','2']
 log=ROOT/'runs'/f'{a.model}-{condition}-s{seed}{tag}.log';start=time.time()
 with log.open('x') as f:p=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
 r=dict(condition=condition,seed=seed,gpu=gpu,microbatch=micro,tag=tag,probe=probe,returncode=p.returncode,wall_seconds=time.time()-start,log=str(log.relative_to(ROOT)))
 print(json.dumps(r),flush=True);return r
print('STAGE1 waiting for verified download',a.model,flush=True)
while not (ROOT/f'models/{a.model}/download-manifest.json').exists():time.sleep(60)
print('STAGE2 calibration',a.model,flush=True)
probes=[];chosen=None
for micro in [16,8,4,2,1]:
 r=call('flat',11,gpus[0],micro,f'-probe-m{micro}',True);probes.append(r)
 if r['returncode']==0:
  meta=json.loads((ROOT/f'{a.model}/runs/flat-original-s11-probe-m{micro}/summary.json').read_text())
  if meta['training']['peak_memory_bytes']<90*1024**3:chosen=micro;break
  print('Calibration succeeded but exceeds 90GiB reserve; retry smaller',flush=True)
 else:
  log=(ROOT/r['log']).read_text()
  if 'out of memory' not in log.lower():raise RuntimeError('Non-OOM calibration failure; preserve log and stop')
(ROOT/f'analysis/{a.model}-calibration.json').write_text(json.dumps(dict(probes=probes,microbatch=chosen),indent=2))
if chosen is None:raise RuntimeError('No single-GPU calibration fits; training not launched')
print('STAGE3 starting registered flat/macro paired jobs',a.model,'micro',chosen,flush=True)
def worker(seed,gpu):
 rs=[]
 for condition in ['flat','macro']:
  r=call(condition,seed,gpu,chosen);rs.append(r)
  if r['returncode']!=0:break
 return rs
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=sum(list(pool.map(lambda x:worker(*x),zip([11,22,33],gpus))),[])
(ROOT/f'analysis/{a.model}-completed.json').write_text(json.dumps(results,indent=2))
if len(results)!=6 or any(r['returncode'] for r in results):raise RuntimeError('Incomplete/failed jobs; not a success marker')
print('STAGE3 completed',a.model,flush=True)
