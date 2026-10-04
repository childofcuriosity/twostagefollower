"""One host orchestrator; each GPU has sequential train -> eval, never overwrite runs."""
import argparse,concurrent.futures,json,os,socket,subprocess,sys,time,traceback
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--config',required=True);a=ap.parse_args();p=Path(a.config);config=json.loads(p.read_text());tag=config['tag'];start=time.time()
 def lane(job):
  env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(job['gpu']);cmd=[sys.executable,'-u',str(R/'src/train.py'),'--model',job['model'],'--condition',job['condition'],'--seed',str(job['seed']),'--microbatch',str(job['microbatch'])]
  if job.get('probe'):cmd+=['--probe','--steps','2']
  runid=f"{job['model']}-{job['condition']}-s{job['seed']}";record=dict(job=job,host=socket.gethostname(),start_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),commands=[])
  commands=[cmd]
  if not job.get('probe'):commands.append([sys.executable,'-u',str(R/'src/evaluate.py'),'--model',job['model'],'--condition',job['condition'],'--seed',str(job['seed'])])
  for stage,cmd in enumerate(commands):
   logpath=R/'logs'/f'{tag}-{runid}-stage{stage}.log'
   with logpath.open('x') as log:
    child=subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT)
    record['commands'].append(dict(argv=cmd,pid=child.pid,log=str(logpath),started=time.time()))
    status=R/'analysis'/f'{tag}-{runid}-status.json';status.write_text(json.dumps(record,indent=2))
    code=child.wait();record['commands'][-1].update(returncode=code,ended=time.time());status.write_text(json.dumps(record,indent=2))
   if code:record['status']='failed';return record
  record['status']='complete';return record
 lanes={}
 for j in config['jobs']:lanes.setdefault(j['gpu'],[]).append(j)
 def run_lane(jobs):return [lane(j) for j in jobs]
 with concurrent.futures.ThreadPoolExecutor(max_workers=len(lanes)) as pool:records=[r for group in pool.map(run_lane,lanes.values()) for r in group]
 (R/'analysis'/f'{tag}-completed.json').write_text(json.dumps(dict(records=records,seconds=time.time()-start),indent=2))
 if not all(r['status']=='complete' for r in records):raise SystemExit(1)
if __name__=='__main__':main()
