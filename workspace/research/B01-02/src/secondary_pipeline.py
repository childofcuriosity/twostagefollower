import concurrent.futures,json,os,queue,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT.parents[2];python=PROJECT/'.training-venv/bin/python'
while not (ROOT/'analysis/posthoc-completed.json').exists():time.sleep(60)
if any(r['returncode'] for r in json.loads((ROOT/'analysis/posthoc-completed.json').read_text())):raise SystemExit('Posthoc failures must be inspected')
gpus=queue.Queue()
for i in ['0','1','2','3']:gpus.put(i)
def run(job):
 cond,seed=job;gpu=gpus.get();env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=gpu;start=time.time()
 try:
  with (ROOT/f'secondary/runs/{cond}-s{seed}.log').open('w') as f:p=subprocess.run([str(python),'-u',str(ROOT/'src/run_secondary.py'),'--condition',cond,'--seed',str(seed),'--steps','512'],env=env,stdout=f,stderr=subprocess.STDOUT)
  row={'condition':cond,'seed':seed,'gpu':gpu,'returncode':p.returncode,'wall_seconds':time.time()-start}
 finally:gpus.put(gpu)
 print(json.dumps(row),flush=True);return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:rows=list(ex.map(run,[(c,s) for s in [11,22,33] for c in ['flat','macro']]))
(ROOT/'secondary/analysis/completed.json').write_text(json.dumps(rows,indent=2))
if any(r['returncode'] for r in rows):raise SystemExit(1)
