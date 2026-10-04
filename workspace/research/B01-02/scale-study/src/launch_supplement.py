import argparse,subprocess,sys,os,json,time,concurrent.futures
from pathlib import Path
R=Path(__file__).resolve().parents[1];ap=argparse.ArgumentParser();ap.add_argument('--lane',choices=['lr','instruct'],required=True);ap.add_argument('--remote-ready',action='store_true');a=ap.parse_args()
primary='qwen7b' if a.lane=='lr' else 'qwen32b';marker=R/f'analysis/{primary}-checkpoint-tests-completed.json'
if a.remote_ready:
 assert a.lane in ['lr','instruct']
 print('Independent remote supplement lane',a.lane,'no primary GPU dependency',flush=True)
else:
 print('Supplement lane',a.lane,'waiting for primary checkpoints',flush=True)
 while not marker.exists():time.sleep(60)
 records=json.loads(marker.read_text());assert len(records)==6 and all(r['returncode']==0 for r in records)
gpus=[0,1,2] if a.remote_ready else ([4,5,6] if a.lane=='lr' else [0,1,2])
groups=[('qwen3b',1e-4),('qwen32b',1e-4)] if a.lane=='lr' else [('qwen32b-instruct',3e-4)]
def call(model,condition,seed,gpu,lr,micro,probe=False):
 env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu);tag='-probe' if probe else '';log=R/'runs'/f'supplement-{model}-{condition}-s{seed}{tag}.log'
 cmd=[sys.executable,'-u',str(R/'src/train_supplement.py'),'--model',model,'--condition',condition,'--seed',str(seed),'--microbatch',str(micro),'--accum',str(32//micro),'--lr',str(lr)]
 if probe:cmd+=['--probe-only','--steps','2','--tag=-probe']
 start=time.time()
 with log.open('x') as f:p=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
 record=dict(model=model,condition=condition,seed=seed,lr=lr,microbatch=micro,probe=probe,returncode=p.returncode,wall_seconds=time.time()-start);print(json.dumps(record),flush=True);return record
allrecords=[]
for model,lr in groups:
 if model=='qwen3b' and (R/'analysis/remote-qwen3b-claim.json').exists():
  remote_marker=R/'analysis/supplement-qwen3b-completed.json'
  while not remote_marker.exists():time.sleep(60)
  records=json.loads(remote_marker.read_text());assert len(records)==6 and all(x['returncode']==0 for x in records)
  allrecords.extend(records);print('Adopted remote 3B results',flush=True);continue
 while not (R/f'models/{model}/download-manifest.json').exists():time.sleep(60)
 micro=16 if model=='qwen3b' else json.loads((R/'analysis/qwen32b-calibration.json').read_text())['microbatch'];assert micro
 if model.endswith('instruct'):
  rec=call(model,'flat',11,gpus[0],lr,micro,True);allrecords.append(rec);assert rec['returncode']==0,'Instruct calibration failed, preserve logs'
  rec=call(model,'frozen',11,gpus[0],lr,micro);allrecords.append(rec);assert rec['returncode']==0
 def worker(seed,gpu):
  result=[]
  for condition in ['flat','macro']:
   rec=call(model,condition,seed,gpu,lr,micro);result.append(rec)
   if rec['returncode']:break
  return result
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:records=sum(list(pool.map(lambda x:worker(*x),zip([11,22,33],gpus))),[])
 allrecords.extend(records);(R/f'analysis/supplement-{model}-completed.json').write_text(json.dumps(records,indent=2));assert len(records)==6 and all(r['returncode']==0 for r in records)
(R/f'analysis/supplement-{a.lane}-completed.json').write_text(json.dumps(allrecords,indent=2));print('Supplement lane done',a.lane,flush=True)
