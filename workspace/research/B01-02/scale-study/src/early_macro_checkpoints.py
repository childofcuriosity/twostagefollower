from pathlib import Path
import subprocess,sys,os,json,time,socket,concurrent.futures
R=Path(__file__).resolve().parents[1]
def worker(seed,gpu):
 env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu);start=time.time()
 with (R/'runs'/f'checkpoints-qwen32b-macro-s{seed}.log').open('x') as f:
  p=subprocess.run([sys.executable,'-u',str(R/'src/checkpoints.py'),'--model','qwen32b','--condition','macro','--seed',str(seed)],env=env,stdout=f,stderr=subprocess.STDOUT)
 record=dict(condition='macro',seed=seed,returncode=p.returncode,wall_seconds=time.time()-start,hostname=socket.gethostname(),gpu=gpu,note='Includes any wait for checkpoint readiness; not pure evaluation compute time')
 dest=R/f'analysis/early-checkpoints-macro-s{seed}.json';tmp=dest.with_suffix('.tmp');tmp.write_text(json.dumps(record,indent=2));tmp.replace(dest);print(json.dumps(record),flush=True);return record
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:records=list(pool.map(lambda x:worker(*x),zip([11,22,33],[4,5,6])))
assert all(x['returncode']==0 for x in records)
