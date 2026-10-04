import argparse,subprocess,sys,os,json,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];ap=argparse.ArgumentParser();ap.add_argument('--lane',type=int,choices=[0,1],required=True);a=ap.parse_args()
models=['qwen1.5b','qwen32b'] if a.lane==0 else ['qwen3b','qwen7b'];gpu=3 if a.lane==0 else 7
results=[]
for model in models:
 env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu);start=time.time()
 with (R/'runs'/f'extended-{model}.log').open('x') as f:p=subprocess.run([sys.executable,'-u',str(R/'src/extended.py'),'--model',model],env=env,stdout=f,stderr=subprocess.STDOUT)
 results.append(dict(model=model,gpu=gpu,returncode=p.returncode,wall_seconds=time.time()-start));print(results[-1],flush=True)
 if p.returncode:break
(R/f'analysis/extended-lane{a.lane}-completed.json').write_text(json.dumps(results,indent=2));assert len(results)==2 and all(r['returncode']==0 for r in results)
