from common import *
import argparse,os,subprocess,sys,time
p=argparse.ArgumentParser();p.add_argument('--phase',required=True);p.add_argument('--lengths',nargs='+',type=int,required=True);p.add_argument('--conditions',nargs='+',default=list(CONDITIONS));p.add_argument('--batch',type=int,default=16);a=p.parse_args()
# Split one-length formal comparison across all 8 GPUs without repeated inference.
shards=2 if a.phase=='formal' and len(a.lengths)==1 else 1
pending=[(L,c,s) for L in sorted(a.lengths,reverse=True) for c in a.conditions for s in range(shards)]
active={};results=[];start=time.time();last_check=start
ledger=R/f'analysis/dispatch-{a.phase}-{"-".join(map(str,a.lengths))}.json'
while pending or active:
 for gpu in range(8):
  if gpu in active or not pending:continue
  L,c,s=pending.pop(0);name=f'{a.phase}-L{L}-{c}-shard{s}'
  logpath=R/f'logs/{name}-{int(time.time())}.log';log=logpath.open('w')
  cmd=[sys.executable,str(R/'src/worker.py'),'--phase',a.phase,'--lengths',str(L),'--conditions',c,'--batch',str(a.batch),'--shard',str(s),'--shards',str(shards)]
  env=dict(os.environ,CUDA_VISIBLE_DEVICES=str(gpu));proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,env=env)
  active[gpu]=(proc,log,dict(gpu=gpu,length=L,condition=c,shard=s,shards=shards,pid=proc.pid,start=time.time(),log=str(logpath)))
  print('START',name,'GPU',gpu,'PID',proc.pid,flush=True)
 for gpu,(proc,log,meta) in list(active.items()):
  rc=proc.poll()
  if rc is None:continue
  log.close();meta.update(returncode=rc,seconds=time.time()-meta['start']);results.append(meta);del active[gpu]
  write(ledger,dict(results=results,active=[x[2] for x in active.values()],pending=pending))
  print('EXIT',meta,flush=True)
 if time.time()-last_check>=3600:
  usage=subprocess.run(['nvidia-smi','--query-gpu=index,memory.used,utilization.gpu','--format=csv'],capture_output=True,text=True)
  with (R/'logs/hourly-checks.jsonl').open('a') as f:f.write(json.dumps(dict(time=time.time(),phase=a.phase,active=[x[2] for x in active.values()],gpu=usage.stdout))+'\n')
  print('HOURLY_CHECK',usage.stdout,flush=True);last_check=time.time()
 if active:time.sleep(10)
write(ledger,dict(results=results,seconds=time.time()-start,allocated_gpu_seconds=sum(x['seconds'] for x in results)))
if any(x['returncode'] for x in results):raise SystemExit('FAILED jobs retained; diagnose logs')
if shards>1:
 for L in a.lengths:
  order={x['id']:i for i,x in enumerate(readrows(R/f'data/{a.phase}-L{L}.jsonl'))}
  for c in a.conditions:
   out=R/f'runs/{a.phase}-L{L}-{c}';rows=[];metas=[]
   for s in range(shards):
    sub=out/f'shard-{s}-of-{shards}';rows+=readrows(sub/'predictions.jsonl');metas.append(json.loads((sub/'complete.json').read_text()))
   rows.sort(key=lambda x:order[x['id']]);assert len(rows)==len(order)==len({x['id'] for x in rows})
   saverows(out/'predictions.jsonl',rows);write(out/'complete.json',dict(n=len(rows),shards=metas,prediction_sha256=sha(out/'predictions.jsonl'),generate_seconds_all_records=sum(x['allocated_generate_seconds'] for x in rows)))
subprocess.run([sys.executable,str(R/'src/score.py'),'--phase',a.phase,'--lengths',*map(str,a.lengths),'--conditions',*a.conditions],check=True)
print('DISPATCH_COMPLETE',flush=True)
