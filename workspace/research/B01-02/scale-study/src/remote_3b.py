from pathlib import Path
import subprocess,sys,os,time,json,socket,concurrent.futures
R=Path(__file__).resolve().parents[1]
def call(condition,seed,gpu,probe=False):
 env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu)
 tag='-remote-probe' if probe else ''
 cmd=[sys.executable,'-u',str(R/'src/train_supplement.py'),'--model','qwen3b','--condition',condition,'--seed',str(seed),'--microbatch','16','--accum','2','--lr','0.0001']
 if probe:cmd+=['--probe-only','--steps','2','--tag='+tag]
 log=R/'runs'/f'supplement-qwen3b-{condition}-s{seed}{tag}.log';start=time.time()
 with log.open('x') as f:p=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
 rec=dict(model='qwen3b',condition=condition,seed=seed,gpu=gpu,lr=1e-4,microbatch=16,probe=probe,hostname=socket.gethostname(),returncode=p.returncode,wall_seconds=time.time()-start)
 print(json.dumps(rec),flush=True);return rec
probe=call('flat',11,0,True)
(R/'analysis/qwen3b-remote-calibration.json').write_text(json.dumps(probe,indent=2))
assert probe['returncode']==0,'Remote calibration failed; preserve logs'
jobs=[(c,s,g) for g,(c,s) in enumerate((c,s) for s in [11,22,33] for c in ['flat','macro'])]
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:records=list(pool.map(lambda x:call(*x),jobs))
assert len(records)==6 and all(x['returncode']==0 for x in records),'Remote jobs failed; preserve all logs'
p=R/'analysis/supplement-qwen3b-completed.json';tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(records,indent=2));tmp.replace(p)
print('Remote 3B six-job control complete',flush=True)
