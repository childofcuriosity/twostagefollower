from common import *
from remote import execute
import os,shutil,subprocess,time,traceback
import torch
ROOTCMD=f'cd {PROJECT} && '

def start_job(name,server,command):
 p=R/f'infrastructure/{name}.json'
 if p.with_suffix('.json.launched.json').exists():return p
 write(p,dict(log=str(R/f'logs/{name}.log'),command=command))
 cmd=ROOTCMD+f'python {R}/src/launch.py --job {p}'
 if server=='local':res=subprocess.run(['bash','-lc',cmd],capture_output=True,text=True)
 else:res=execute(server,cmd)
 assert res.returncode==0,(name,res.stderr)
 print('LAUNCHED',name,res.stdout,flush=True);return p

def train_command(c,seed,run,gpus,port,pre=False,resume=None,stop=None):
 config=R/'config'/('precheck-v2.json' if pre else 'frozen.json')
 command=f'source training-env.sh && source {R}/infrastructure/nccl-env.sh && CUDA_VISIBLE_DEVICES={gpus} torchrun --master_addr=127.0.0.1 --master_port={port} --nnodes=1 --nproc_per_node=2 {R}/src/train.py --condition {c} --seed {seed} --config {config} --output-dir {run}'
 if pre:command+=' --precheck'
 if resume:command+=f' --resume {resume}'
 if stop:command+=f' --stop-after {stop}'
 return command

def check_failure(jobpaths):
 for p in jobpaths:
  f=p.with_suffix(p.suffix+'.exit.json')
  if f.exists():
   x=json.loads(f.read_text());assert x['returncode']==0,(str(p),x)

def queue_eval(c,seed,step,split,checkpoint):
 # Four mutually exclusive shards keep all evaluator GPUs useful; no duplicated answers.
 for shard in range(4):
  label=f'{c}-s{seed}-step{step:03d}-{split}-part{shard}'
  p=R/f'eval/queue/{label}.json'
  if not p.exists():write(p,dict(condition=c,seed=seed,step=step,split=split,checkpoint=str(checkpoint) if checkpoint else None,shard=shard,shards=4,out=str(R/'eval/outputs'/label)))

def run():
 jobs=[R/f'infrastructure/precheck-{s}-v2.json' for s in ['remote70','remote65']]
 restore_started=set()
 while True:
  check_failure(jobs)
  for c,server in [('STEP','remote70'),('NAME','remote65')]:
   cp=R/f'precheck/v2-{c}/checkpoint-002'
   if (cp/'checkpoint.json').exists() and c not in restore_started:
    job=start_job(f'precheck-v2-resume-{c}',server,train_command(c,930001,R/f'precheck/v2-{c}-resume','2,3',29742,True,cp,4));jobs.append(job);restore_started.add(c)
  if all((R/f'precheck/v2-{c}{suffix}/complete.json').exists() for c in CONDITIONS for suffix in ['', '-resume']):break
  time.sleep(15)
 # Both conditions must pass implementation/recovery checks; do not select by their relative reward.
 diagnostics={}
 for c in CONDITIONS:
  run=R/f'precheck/v2-{c}';resume=R/f'precheck/v2-{c}-resume'
  logs=[x for rank in range(2) for x in readrows(run/f'metrics-rank{rank}.jsonl')]
  assert len(logs)==8 and all(x['grad_norm']>0 and x['kl']>=-1e-6 for x in logs)
  assert sum(x['mixed_groups'] for x in logs)>0,'Diagnose reward discrimination before freezing'
  for step in [3,4]:
   for rank in range(2):
    aa=readrows(run/f'candidates/update-{step:03d}-rank{rank}.jsonl');bb=readrows(resume/f'candidates/update-{step:03d}-rank{rank}.jsonl')
    assert [(x['id'],x['output_ids'],x['grading']['reward']) for x in aa]==[(x['id'],x['output_ids'],x['grading']['reward']) for x in bb],(c,step,rank,'resume mismatch')
  from safetensors.torch import load_file
  aa=load_file(str(run/'checkpoint-004/adapter_model.safetensors'));bb=load_file(str(resume/'checkpoint-004/adapter_model.safetensors'))
  drift=max(float((aa[k]-bb[k]).abs().max()) for k in aa);assert drift<=1e-6,(c,drift)
  diagnostics[c]=dict(updates=4,reward_mean=sum(x['mean_reward'] for x in logs)/len(logs),mixed_groups=sum(x['mixed_groups'] for x in logs),groups=sum(x['groups'] for x in logs),unique_candidates=sum(x['unique_candidates'] for x in logs),candidates=sum(x['candidates'] for x in logs),max_kl=max(x['kl'] for x in logs),max_grad=max(x['grad_norm'] for x in logs),max_memory=max(x['peak_memory_bytes'] for x in logs),resume_candidates_identical=True,resume_adapter_max_abs_difference=drift)
 assert json.loads((R/'precheck/v2-STEP/job.json').read_text())['initial_adapter_sha256']==json.loads((R/'precheck/v2-NAME/job.json').read_text())['initial_adapter_sha256']
 assert json.loads((R/'analysis/implementation-tests.json').read_text())['passed']
 write(R/'analysis/precheck-complete.json',dict(passed=True,diagnostics=diagnostics,selection_rule='same first candidate passes correctness, recovery and finite optimization checks; not selected by NAME-minus-STEP'))
 cfg=json.loads((R/'config/precheck-v2.json').read_text());cfg['protocol']='formal-v1'
 manifest=json.loads((R/'data/manifest.json').read_text())
 for split,v in manifest['datasets'].items():assert sha(R/f'data/{split}.jsonl')==v['sha256']
 if (R/'config/freeze-manifest.json').exists():
  frozen=json.loads((R/'config/freeze-manifest.json').read_text())
  assert json.loads((R/'config/frozen.json').read_text())==cfg
  assert frozen['config_sha256']==sha(R/'config/frozen.json')
  for name in ['common.py','engine.py','train.py','evaluate.py']:
   assert sha(R/'src'/name)==frozen['source'][name],('frozen executable changed',name)
 else:
  write(R/'config/frozen.json',cfg)
  snap=R/'snapshots/formal-v1';snap.mkdir(parents=True,exist_ok=True)
  for p in (R/'src').glob('*.py'):shutil.copy2(p,snap/p.name)
  write(R/'config/freeze-manifest.json',dict(created=time.time(),config_sha256=sha(R/'config/frozen.json'),data_manifest_sha256=sha(R/'data/manifest.json'),source={p.name:sha(p) for p in snap.glob('*.py')},precheck_sha256=sha(R/'analysis/precheck-complete.json')))
 print('CONFIG_FROZEN',json.dumps(diagnostics),flush=True)
 # Step0 is original policy, computed once per condition, reused explicitly for three seeds.
 for c in CONDITIONS:
  for split in ['validation','test']:queue_eval(c,'base',0,split,None)
 jobs=[]
 for worker,gpu in enumerate(range(4,8)):
  jobs.append(start_job(f'evaluator-{worker}','local',f'source training-env.sh && CUDA_VISIBLE_DEVICES={gpu} python {R}/src/evaluate.py --config {R}/config/frozen.json --worker local-gpu{gpu}'))
 training=[]
 for seed,server in [(301,'remote70'),(302,'remote65'),(303,'local')]:
  for ci,c in enumerate(CONDITIONS):
   run=R/f'runs/v1-{c}-s{seed}';p=start_job(f'formal-{c}-s{seed}',server,train_command(c,seed,run,'0,1' if ci==0 else '2,3',29751+ci));jobs.append(p);training.append((c,seed,server,run,p))
 last_check=time.time()
 while True:
  check_failure(jobs)
  for c,seed,server,run,p in training:
   for step in range(10,101,10):
    cp=run/f'checkpoint-{step:03d}'
    if (cp/'checkpoint.json').exists():
     queue_eval(c,seed,step,'validation',cp)
     if step==100:queue_eval(c,seed,step,'test',cp)
  all_train=all((run/'complete.json').exists() for _,_,_,run,_ in training)
  queued=list((R/'eval/queue').glob('*.json'))
  all_eval=all((Path(json.loads(p.read_text())['out'])/'complete.json').exists() for p in queued)
  if all_train and all_eval:
   assert len(queued)==16+6*11*4,len(queued)
   (R/'eval/stop').write_text('All scheduled evaluations completed.\n');break
  if time.time()-last_check>=3600:
   state=dict(time=time.time(),completed_runs=sum((run/'complete.json').exists() for _,_,_,run,_ in training),queued_eval=len(queued),completed_eval=sum((Path(json.loads(p.read_text())['out'])/'complete.json').exists() for p in queued),servers={})
   command='nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv; ps -eo pid,etime,args | grep -E "[t]rain.py|[e]valuate.py"'
   for server in ['local','remote70','remote65']:
    result=subprocess.run(['bash','-lc',command],capture_output=True,text=True) if server=='local' else execute(server,command)
    state['servers'][server]=dict(returncode=result.returncode,output=result.stdout)
   with (R/'logs/hourly-checks.jsonl').open('a') as f:f.write(json.dumps(state)+'\n')
   print('HOURLY',json.dumps(state),flush=True);last_check=time.time()
  time.sleep(15)
 write(R/'analysis/computation-complete.json',dict(finished=time.time(),runs=6,updates_each=100,eval_shards=len(queued),analysis_pending=True))
 print('COMPUTATION_COMPLETE',flush=True)
if __name__=='__main__':
 try:run()
 except BaseException:
  write(R/f'analysis/supervisor-failure-{int(time.time())}.json',dict(traceback=traceback.format_exc(),time=time.time()));raise
