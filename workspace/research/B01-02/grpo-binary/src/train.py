from common import *
from engine import *
import argparse,contextlib,datetime,os,traceback
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
p=argparse.ArgumentParser();p.add_argument('--condition',choices=CONDITIONS,required=True);p.add_argument('--seed',type=int,required=True);p.add_argument('--config',required=True);p.add_argument('--output-dir',dest='run',required=True);p.add_argument('--precheck',action='store_true');p.add_argument('--stop-after',type=int);p.add_argument('--resume');a=p.parse_args()
cfg=json.loads(Path(a.config).read_text());rank=int(os.environ['LOCAL_RANK']);world=int(os.environ['WORLD_SIZE']);assert world==cfg['world_size']==2
torch.cuda.set_device(rank);device=torch.device('cuda',rank);dist.init_process_group('nccl',timeout=datetime.timedelta(minutes=15))
run=Path(a.run).resolve();run.mkdir(parents=True,exist_ok=True);start=time.time()
if a.precheck:
 data=readrows(R/'data/precheck.jsonl');order=list(range(len(data)));random.Random(a.seed).shuffle(order);order=(order*25)[:1600]
else:
 assert a.seed in SEEDS;assert Path(a.config).name=='frozen.json'
 data=readrows(R/'data/train.jsonl');order=json.loads((R/f'data/order-s{a.seed}.json').read_text())['indices']
manifest=json.loads((R/'data/manifest.json').read_text());assert cfg['model_revision']==manifest['model_revision']
assert sha(OLD/f'prompts/{a.condition}.txt')==manifest['prompt_sha256'][a.condition]
assert sha(B/'scale-study/src/audit.py')==manifest['legacy_score_sha256']
model,tok=load(cfg,a.seed,device,adapter=a.resume)
opt=torch.optim.AdamW([v for v in model.parameters() if v.requires_grad],lr=cfg['learning_rate'],betas=tuple(cfg['adam_betas']),eps=cfg['adam_eps'],weight_decay=cfg['weight_decay'],fused=True)
initial_hash=adapter_hash(model)
wrapper=DDP(model,device_ids=[rank],output_device=rank,broadcast_buffers=False,find_unused_parameters=False)
step0=0
if a.resume:
 resume=Path(a.resume);state=torch.load(resume/'optimizer.pt',map_location=device,weights_only=False);opt.load_state_dict(state['optimizer']);step0=state['update']
 rng=torch.load(resume/f'rng-rank{rank}.pt',map_location='cpu',weights_only=False);torch.set_rng_state(rng['cpu']);torch.cuda.set_rng_state(rng['cuda'],device);random.setstate(rng['python'])
else:
 torch.manual_seed(a.seed+100000*rank);random.seed(a.seed+100000*rank)
if rank==0:
 write(run/'job.json',dict(condition=a.condition,seed=a.seed,precheck=a.precheck,config=cfg,config_sha256=sha(a.config),manifest_sha256=sha(R/'data/manifest.json'),initial_adapter_sha256=initial_hash,world=world,started=start,resume=a.resume,source={f.name:sha(f) for f in (R/'src').glob('*.py')}))

def save(update):
 directory=run/f'checkpoint-{update:03d}';directory.mkdir(exist_ok=True)
 if rank==0:
  model.save_pretrained(directory,safe_serialization=True)
  torch.save(dict(update=update,optimizer=opt.state_dict()),directory/'optimizer.pt')
 torch.save(dict(cpu=torch.get_rng_state(),cuda=torch.cuda.get_rng_state(device),python=random.getstate()),directory/f'rng-rank{rank}.pt')
 dist.barrier()
 if rank==0:
  write(directory/'checkpoint.json',dict(update=update,condition=a.condition,seed=a.seed,adapter_sha256=sha(directory/'adapter_model.safetensors'),initial_adapter_sha256=initial_hash,time=time.time(),config_sha256=sha(a.config),precheck=a.precheck))
 dist.barrier()

try:
 if not a.resume:save(0)
 updates=a.stop_after or cfg['updates'];G=cfg['candidates_per_question'];local_questions=cfg['questions_per_update']//world
 for update in range(step0+1,updates+1):
  tick=time.time();indices=order[(update-1)*16:update*16];indices=indices[rank*local_questions:(rank+1)*local_questions];rows=[data[i] for i in indices]
  rollout_path=run/f'candidates/update-{update:03d}-rank{rank}.jsonl';assert not rollout_path.exists(),'Never overwrite an earlier rollout; archive incomplete attempt before resume'
  candidates,sampling_seconds=generate(model,tok,rows,a.condition,cfg,True,G)
  adv,metrics=advantages([x['grading']['reward'] for x in candidates],G,cfg['advantage_epsilon'])
  for x,y in zip(candidates,adv.tolist()):x.update(update=update,rank=rank,advantage=y,seed=a.seed)
  saverows(rollout_path,candidates)
  assert len(candidates)==64
  lr=cfg['learning_rate']*min(update/cfg['warmup_updates'],1.0);opt.param_groups[0]['lr']=lr;opt.zero_grad(set_to_none=True)
  micro=cfg['microbatch'];train_start=time.time();loss_sum=0.;kl_sum=0.;policy_sum=0.;token_count=0
  for offset in range(0,len(candidates),micro):
   subset=candidates[offset:offset+micro];ids,attention,mask=pack(subset,tok.pad_token_id,device)
   assert int(mask.sum())==sum(len(x['output_ids']) for x in subset)
   # The reference is the frozen original policy: same base with adapters disabled.
   model.eval()
   with torch.no_grad(),model.disable_adapter():ref=logps(model,ids,attention)
   model.train()
   sync=wrapper.no_sync() if offset+micro<len(candidates) else contextlib.nullcontext()
   with sync:
    logp=logps(wrapper,ids,attention)
    loss,info=loss_terms(logp,ref,mask,adv[offset:offset+len(subset)].to(device),cfg)
    assert torch.isfinite(loss),dict(update=update,rank=rank,loss=float(loss))
    (loss*(len(subset)/len(candidates))).backward()
   weight=len(subset)/len(candidates);loss_sum+=float(loss.detach())*weight;kl_sum+=info['kl']*weight;policy_sum+=info['policy_loss']*weight;token_count+=info['token_count']
   del ids,attention,mask,ref,logp,loss
  grad=torch.nn.utils.clip_grad_norm_([v for v in model.parameters() if v.requires_grad],cfg['max_grad_norm']);assert torch.isfinite(grad),grad
  opt.step();torch.cuda.synchronize();train_seconds=time.time()-train_start
  unique=sum(len({x['raw'] for x in candidates[i:i+G]}) for i in range(0,len(candidates),G))
  record=dict(update=update,rank=rank,condition=a.condition,seed=a.seed,questions=indices,**metrics,unique_candidates=unique,candidates=len(candidates),output_tokens=token_count,lr=lr,loss=loss_sum,policy_loss=policy_sum,kl=kl_sum,grad_norm=float(grad),sampling_seconds=sampling_seconds,update_seconds=train_seconds,seconds=time.time()-tick,peak_memory_bytes=torch.cuda.max_memory_allocated(),truncated=sum(x['finish_reason']=='length' for x in candidates))
  with (run/f'metrics-rank{rank}.jsonl').open('a') as f:f.write(json.dumps(record)+'\n')
  print(json.dumps(record),flush=True)
  if a.precheck or update%cfg['checkpoint_every']==0:save(update)
 if rank==0:write(run/'complete.json',dict(updates=updates,started_from=step0,seconds=time.time()-start,condition=a.condition,seed=a.seed,precheck=a.precheck))
except BaseException:
 write(run/f'failure-rank{rank}-{int(time.time())}.json',dict(error=traceback.format_exc(),time=time.time()));raise
finally:
 dist.destroy_process_group()
