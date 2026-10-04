from common import *
from remote import execute
import subprocess,time,traceback,shutil,math
import torch
from safetensors.torch import load_file
TASKS=['14b-L7','14b-L6','14b-L5','7b-L5','7b-L4','7b-L3']
PRE_SLOTS=[('local','0,1'),('local','2,3'),('local','4,5'),('local','6,7'),('remote70','0,1'),('remote70','2,3'),('remote65','0,1'),('remote65','2,3')]
SLOTS=[('local','0,1'),('local','2,3'),('remote70','0,1'),('remote70','2,3'),('remote65','0,1'),('remote65','2,3')]

def start_job(name,server,command):
 p=ROOT/f'infrastructure/{name}.json'
 if p.with_suffix('.json.launched.json').exists():return p
 write(p,dict(log=str(ROOT/f'logs/{name}.log'),command=command,server=server))
 cmd=f'cd {PROJECT} && python {ROOT}/src/launch.py --job {p}'
 res=subprocess.run(['bash','-lc',cmd],capture_output=True,text=True) if server=='local' else execute(server,cmd)
 assert res.returncode==0,(name,res.stderr)
 print('LAUNCHED',name,res.stdout,flush=True);return p

def exited(p):
 f=p.with_suffix('.json.exit.json')
 if not f.exists():return False
 x=json.loads(f.read_text());assert x['returncode']==0,(str(p),x)
 return True

def train_command(task,c,seed,gpus,port,pre=False,resume=False):
 root=ROOT/task;run=root/(f'precheck/v1-{c}'+('-resume' if resume else '') if pre else f'runs/v1-{c}-s{seed}')
 cfg=root/'config'/('precheck-v1.json' if pre else 'frozen.json')
 cmd=f'GRPO_TASK_ROOT={root} CUDA_VISIBLE_DEVICES={gpus} torchrun --master_addr=127.0.0.1 --master_port={port} --nnodes=1 --nproc_per_node=2 {ROOT}/src/train.py --condition {c} --seed {seed} --config {cfg} --output-dir {run}'
 if pre:cmd+=' --precheck --stop-after 4'
 if resume:cmd+=f' --resume {root}/precheck/v1-{c}/checkpoint-002'
 return cmd

def shell(command):return f'source training-env.sh && source {ROOT}/infrastructure/nccl-env.sh && '+command

def hourly(stage,state):
 records={}
 command='nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv'
 for server in ['local','remote70','remote65']:
  p=subprocess.run(['bash','-lc',command],capture_output=True,text=True) if server=='local' else execute(server,command)
  records[server]=dict(returncode=p.returncode,output=p.stdout)
 record=dict(time=time.time(),stage=stage,state=state,servers=records)
 with (ROOT/'logs/hourly-checks.jsonl').open('a') as f:f.write(json.dumps(record)+'\n')
 print('HOURLY',json.dumps(record),flush=True)

def precheck():
 statepath=ROOT/'infrastructure/precheck-state.json'
 if statepath.exists():
  state=json.loads(statepath.read_text());pending=state['pending'];active={int(i):(t,c,Path(p)) for i,(t,c,p) in state['active'].items()};finished=state['finished']
 else:pending=[(t,c) for t in TASKS for c in CONDITIONS];active={};finished=[]
 last=time.time()
 while pending or active:
  for i,(server,gpus) in enumerate(PRE_SLOTS):
   if i in active or not pending:continue
   task,c=pending.pop(0);root=ROOT/task
   command=''
   if c=='STEP':command=f'GRPO_TASK_ROOT={root} python {ROOT}/src/validate.py && '
   command+=train_command(task,c,930001,gpus,29810+i,pre=True)+' && '+train_command(task,c,930001,gpus,29810+i,pre=True,resume=True)
   p=start_job(f'precheck-{task}-{c}',server,shell(command));active[i]=(task,c,p)
  for i,(task,c,p) in list(active.items()):
   if exited(p):finished.append((task,c));del active[i];print('PRECHECK_DONE',task,c,flush=True)
  if time.time()-last>=3600:hourly('precheck',dict(finished=finished,active=[(t,c) for t,c,_ in active.values()]));last=time.time()
  write(statepath,dict(pending=pending,active={i:[t,c,str(p)] for i,(t,c,p) in active.items()},finished=finished))
  if pending or active:time.sleep(15)
 diagnostics={}
 for task in TASKS:
  root=ROOT/task;diagnostics[task]={};initial=[]
  assert json.loads((root/'analysis/implementation-tests.json').read_text())['passed']
  for c in CONDITIONS:
   run=root/f'precheck/v1-{c}';resume=root/f'precheck/v1-{c}-resume'
   initial.append(json.loads((run/'job.json').read_text())['initial_adapter_sha256'])
   logs=[x for rank in range(2) for x in readrows(run/f'metrics-rank{rank}.jsonl')]
   assert len(logs)==8 and all(math.isfinite(x['grad_norm']) and x['grad_norm']>=0 and math.isfinite(x['kl']) and x['kl']>=-1e-6 for x in logs)
   for step in [3,4]:
    for rank in range(2):
     aa=readrows(run/f'candidates/update-{step:03d}-rank{rank}.jsonl');bb=readrows(resume/f'candidates/update-{step:03d}-rank{rank}.jsonl')
     assert [(x['id'],x['output_ids'],x['grading']['reward']) for x in aa]==[(x['id'],x['output_ids'],x['grading']['reward']) for x in bb],(task,c,step,rank,'resume candidates')
   aa=load_file(str(run/'checkpoint-004/adapter_model.safetensors'));bb=load_file(str(resume/'checkpoint-004/adapter_model.safetensors'));drift=max(float((aa[k]-bb[k]).abs().max()) for k in aa);assert drift<=1e-6,(task,c,drift);del aa,bb
   aa=torch.load(run/'checkpoint-004/optimizer.pt',map_location='cpu',weights_only=False);bb=torch.load(resume/'checkpoint-004/optimizer.pt',map_location='cpu',weights_only=False)
   assert aa['update']==bb['update']==4
   assert aa['optimizer']['param_groups']==bb['optimizer']['param_groups']
   for key,state in aa['optimizer']['state'].items():
    assert float(state['step'])==4
    for k,v in state.items():assert torch.equal(v,bb['optimizer']['state'][key][k]),(task,c,'optimizer recovery',key,k)
   del aa,bb
   diagnostics[task][c]=dict(reward_mean=sum(x['mean_reward'] for x in logs)/8,mixed_groups=sum(x['mixed_groups'] for x in logs),groups=sum(x['groups'] for x in logs),candidates=sum(x['candidates'] for x in logs),unique_candidates=sum(x['unique_candidates'] for x in logs),zero_gradient_updates=sum(x['grad_norm']==0 for x in logs)/2,max_kl=max(x['kl'] for x in logs),peak_memory=max(x['peak_memory_bytes'] for x in logs),resume_candidates_identical=True,resume_adapter_max_difference=drift,optimizer_resume_identical=True)
  assert len(set(initial))==1,(task,'paired initialization')
  write(root/'analysis/precheck-complete.json',dict(passed=True,diagnostics=diagnostics[task],note='Zero-gradient/all-zero reward groups retained; not a stopping rule or configuration-selection signal.'))
 write(ROOT/'analysis/precheck-complete.json',dict(passed=True,diagnostics=diagnostics))
 return diagnostics

def freeze():
 source={p.name:sha(p) for p in (ROOT/'src').glob('*.py')}
 if (ROOT/'config/freeze-manifest.json').exists():
  old=json.loads((ROOT/'config/freeze-manifest.json').read_text());assert old['source']==source
  return
 for task in TASKS:
  root=ROOT/task;cfg=json.loads((root/'config/precheck-v1.json').read_text());cfg['protocol']='formal-v1';write(root/'config/frozen.json',cfg)
  write(root/'config/freeze-manifest.json',dict(created=time.time(),config_sha256=sha(root/'config/frozen.json'),data_manifest_sha256=sha(root/'data/manifest.json'),source=source,precheck_sha256=sha(root/'analysis/precheck-complete.json')))
 snap=ROOT/'snapshots/formal-v1';snap.mkdir(exist_ok=True)
 for p in (ROOT/'src').glob('*.py'):shutil.copy2(p,snap/p.name)
 write(ROOT/'config/freeze-manifest.json',dict(created=time.time(),source=source,tasks=TASKS,paired_queue=[dict(task=t,seed=s) for t in TASKS for s in SEEDS]))
 print('ALL_CONFIGS_FROZEN',flush=True)

def queue_eval(task,c,seed,step,split,checkpoint):
 for shard in range(4):
  label=f'{task}-{c}-s{seed}-step{step:03d}-{split}-part{shard}';p=ROOT/f'eval/queue/{label}.json'
  if not p.exists():write(p,dict(task=task,task_root=str(ROOT/task),condition=c,seed=seed,step=step,split=split,checkpoint=str(checkpoint) if checkpoint else None,shard=shard,shards=4,out=str(ROOT/'eval/outputs'/label)))

def formal():
 evaluators=[start_job(f'evaluator-{i}','local',f'source training-env.sh && CUDA_VISIBLE_DEVICES={gpu} python {ROOT}/src/evaluate_pool.py --worker local-gpu{gpu}') for i,gpu in enumerate(range(4,8))]
 for task in TASKS:
  for c in CONDITIONS:
   for split in ['validation','test']:queue_eval(task,c,'base',0,split,None)
 statepath=ROOT/'infrastructure/formal-state.json'
 if statepath.exists():
  state=json.loads(statepath.read_text());pending=state['pending'];active={int(i):(t,s,Path(p)) for i,(t,s,p) in state['active'].items()};finished=state['finished'];started=state['started']
 else:pending=[(task,seed) for task in TASKS for seed in SEEDS];active={};finished=[];started=[]
 last=time.time()
 # A pair stays on the same host and physical two-GPU slot; STEP then NAME.
 while True:
  for p in evaluators:exited(p)
  for i,(server,gpus) in enumerate(SLOTS):
   if i in active or not pending:continue
   task,seed=pending.pop(0)
   cmds=[train_command(task,c,seed,gpus,29910+i) for c in CONDITIONS]
   p=start_job(f'formal-pair-{task}-s{seed}',server,shell(' && '.join(cmds)));active[i]=(task,seed,p);started.append((task,seed));print('PAIR_SLOT',task,seed,i,server,gpus,flush=True)
  for i,(task,seed,p) in list(active.items()):
   if exited(p):finished.append((task,seed));del active[i];print('PAIR_FINISHED',task,seed,flush=True)
  for task,seed in started:
   for c in CONDITIONS:
    run=ROOT/task/f'runs/v1-{c}-s{seed}'
    for step in range(10,101,10):
     cp=run/f'checkpoint-{step:03d}'
     if (cp/'checkpoint.json').exists():
      queue_eval(task,c,seed,step,'validation',cp)
      if step==100:queue_eval(task,c,seed,step,'test',cp)
  write(statepath,dict(pending=pending,active={i:[t,s,str(p)] for i,(t,s,p) in active.items()},finished=finished,started=started))
  queued=list((ROOT/'eval/queue').glob('*.json'));done=sum((Path(json.loads(p.read_text())['out'])/'complete.json').exists() for p in queued)
  if not pending and not active and done==len(queued):
   assert len(finished)==18 and len(queued)==1680,(len(finished),len(queued));(ROOT/'eval/stop').write_text('All scheduled jobs completed.\n');break
  if time.time()-last>=3600:
   progress={}
   for task,seed in started:
    for c in CONDITIONS:
     p=ROOT/task/f'runs/v1-{c}-s{seed}/metrics-rank0.jsonl'
     if p.exists():progress[f'{task}-{c}-s{seed}']=readrows(p)[-1]['update']
   hourly('formal',dict(completed_pairs=finished,active_pairs=[(t,s) for t,s,_ in active.values()],updates=progress,queued_eval=len(queued),completed_eval=done));last=time.time()
  time.sleep(15)
 while not all(exited(p) for p in evaluators):time.sleep(5)
 write(ROOT/'analysis/computation-complete.json',dict(finished=time.time(),runs=36,updates_each=100,checkpoints_expected=396,formal_candidates_expected=460800,independent_eval_expected=119808,eval_shards=1680,analysis_pending=True))
 print('COMPUTATION_COMPLETE',flush=True)

if __name__=='__main__':
 try:
  assert (ROOT/'datasets/manifest.json').exists()
  if not (ROOT/'analysis/precheck-complete.json').exists():precheck()
  freeze();formal()
 except BaseException:
  write(ROOT/f'analysis/supervisor-failure-{int(time.time())}.json',dict(traceback=traceback.format_exc(),time=time.time()));raise
