import concurrent.futures,json,subprocess,os,queue,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT.parents[2];python=PROJECT/'.training-venv/bin/python'
while not (ROOT/'analysis/PIPELINE_COMPLETE.json').exists():time.sleep(60)
gpus=queue.Queue()
for x in ['0','1','2','3']:gpus.put(x)
jobs=[('alignment',c,s) for s in [11,22,33] for c in ['stable','call']]+[('routing',c,s) for s in [11,22,33] for c in ['flat','macro']]+[('routing','frozen',11)]
def run(job):
 kind,c,seed=job;gpu=gpus.get();env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=gpu
 out=ROOT/'analysis'/'posthoc-logs';out.mkdir(exist_ok=True)
 if kind=='alignment':cmd=[str(python),'-u',str(ROOT/'src/run_alignment.py'),'--alignment',c,'--condition','macro','--seed',str(seed),'--steps','512']
 else:cmd=[str(python),'-u',str(ROOT/'src/route_probe.py'),'--condition',c,'--seed',str(seed)]
 start=time.time()
 try:
  with (out/f'{kind}-{c}-s{seed}.log').open('w') as f:p=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
  row={'kind':kind,'condition':c,'seed':seed,'gpu':gpu,'returncode':p.returncode,'wall_seconds':time.time()-start}
 finally:gpus.put(gpu)
 print(json.dumps(row),flush=True);return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:rows=list(ex.map(run,jobs))
(ROOT/'analysis/posthoc-completed.json').write_text(json.dumps(rows,indent=2))
if any(r['returncode'] for r in rows):raise SystemExit(1)
subprocess.run([str(python),str(ROOT/'src/analyze.py')],check=True)
subprocess.run([str(python),str(ROOT/'src/verify_artifacts.py')],check=True)
