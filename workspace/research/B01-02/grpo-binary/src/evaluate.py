from common import *
from engine import load,generate
import argparse,os,time,traceback
from peft import set_peft_model_state_dict
from safetensors.torch import load_file
p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--worker',required=True);p.add_argument('--once');a=p.parse_args()
cfg=json.loads(Path(a.config).read_text());model=tok=None
while True:
 jobpath=Path(a.once) if a.once else None
 if not jobpath:
  for candidate in sorted((R/'eval/queue').glob('*.json')):
   spec=json.loads(candidate.read_text());out=Path(spec['out'])
   if (out/'complete.json').exists():continue
   try:candidate.with_suffix('.claim').mkdir()
   except FileExistsError:continue
   jobpath=candidate;write(jobpath.with_suffix('.claim')/'worker.json',dict(worker=a.worker,pid=os.getpid(),time=time.time()));break
 if jobpath is None:
  if (R/'eval/stop').exists():break
  time.sleep(10);continue
 job=json.loads(jobpath.read_text());out=Path(job['out']);out.mkdir(parents=True,exist_ok=True)
 if (out/'complete.json').exists():
  if a.once:break
  continue
 try:
  begin=time.time()
  if model is None:model,tok=load(cfg,301,'cuda',train=False)
  checkpoint=job.get('checkpoint')
  if checkpoint:
   checkpoint=Path(checkpoint);assert (checkpoint/'checkpoint.json').exists()
   state=load_file(str(checkpoint/'adapter_model.safetensors'));result=set_peft_model_state_dict(model,state,adapter_name='default');assert not result.unexpected_keys,result
  rows=readrows(R/f'data/{job["split"]}.jsonl');rows=rows[job['shard']::job['shards']]
  if checkpoint:outputs,seconds=generate(model,tok,rows,job['condition'],cfg,False)
  else:
   with model.disable_adapter():outputs,seconds=generate(model,tok,rows,job['condition'],cfg,False)
  saverows(out/'predictions.jsonl',outputs)
  write(out/'complete.json',dict(**job,n=len(rows),correct=sum(x['grading']['strict'] for x in outputs),header_correct=sum(x['grading']['header_compliant'] for x in outputs),generated_tokens=sum(x['generated_tokens'] for x in outputs),generate_seconds=sum(x['allocated_generate_seconds'] for x in outputs),wall_seconds=time.time()-begin,predictions_sha256=sha(out/'predictions.jsonl'),worker=a.worker,finished=time.time()))
  print(json.dumps(dict(job=str(jobpath),n=len(rows),seconds=time.time()-begin)),flush=True)
 except BaseException:
  write(out/'failure.json',dict(traceback=traceback.format_exc(),time=time.time()));raise
 if a.once:break
print('EVALUATOR_DONE',flush=True)
