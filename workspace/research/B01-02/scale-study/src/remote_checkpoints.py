from pathlib import Path
import subprocess,sys,os,json,time,socket,argparse
R=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--seeds',required=True);args=a.parse_args()
for seed in map(int,args.seeds.split(',')):
 run=R/f'qwen32b/runs/flat-original-s{seed}'
 for step in [0,16,64,128,256]:assert (run/f'step{step:04d}-dev.jsonl').exists()
 env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']='3';start=time.time()
 with (R/'runs'/f'checkpoints-qwen32b-flat-s{seed}.log').open('x') as f:
  p=subprocess.run([sys.executable,'-u',str(R/'src/checkpoints.py'),'--model','qwen32b','--condition','flat','--seed',str(seed)],env=env,stdout=f,stderr=subprocess.STDOUT)
 record=dict(condition='flat',seed=seed,returncode=p.returncode,wall_seconds=time.time()-start,hostname=socket.gethostname(),gpu=3)
 dest=R/f'analysis/remote-checkpoints-flat-s{seed}.json';tmp=dest.with_suffix('.tmp');tmp.write_text(json.dumps(record,indent=2));tmp.replace(dest);print(json.dumps(record),flush=True)
 assert p.returncode==0,'Remote checkpoint job failed, preserve logs'
