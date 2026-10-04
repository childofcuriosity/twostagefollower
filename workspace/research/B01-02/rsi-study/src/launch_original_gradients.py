import subprocess,os,sys,time,json
from common import ROOT
results=[]
for seed in [11,22,33]:
 start=time.time()
 with (ROOT/'runs'/f'gradient-original-s{seed}.log').open('w') as log:p=subprocess.run([sys.executable,str(ROOT/'src/gradient_original.py'),'--seed',str(seed)],env={**os.environ,'CUDA_VISIBLE_DEVICES':'7'},stdout=log,stderr=subprocess.STDOUT)
 elapsed=time.time()-start;waiting=json.loads((ROOT/f'runs/gradient-original-s{seed}/results.json').read_text())['checkpoint_wait_seconds'] if p.returncode==0 else 0
 result=dict(seed=seed,returncode=p.returncode,wall_seconds=elapsed-waiting,checkpoint_wait_seconds=waiting);results.append(result);print(json.dumps(result),flush=True)
 if p.returncode:break
(ROOT/'analysis/original-gradients-completed.json').write_text(json.dumps(results,indent=2));assert len(results)==3 and all(r['returncode']==0 for r in results)
