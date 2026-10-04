from common import *
from engine import load,generate
import argparse,time,traceback,gc
from peft import set_peft_model_state_dict
from safetensors.torch import load_file
p=argparse.ArgumentParser();p.add_argument('--worker',required=True);a=p.parse_args();cache={}
while True:
 jobpath=None
 # Atomic claims: each evaluation shard has exactly one writer.
 for candidate in sorted((ROOT/'eval/queue').glob('*.json')):
  spec=json.loads(candidate.read_text());out=Path(spec['out'])
  if (out/'complete.json').exists():continue
  try:candidate.with_suffix('.claim').mkdir()
  except FileExistsError:continue
  jobpath=candidate;write(jobpath.with_suffix('.claim')/'worker.json',dict(worker=a.worker,pid=os.getpid(),time=time.time()));break
 if jobpath is None:
  if (ROOT/'eval/stop').exists():break
  time.sleep(10);continue
 job=json.loads(jobpath.read_text());out=Path(job['out']);out.mkdir(parents=True,exist_ok=True)
 try:
  begin=time.time();taskroot=Path(job['task_root']);cfg=json.loads((taskroot/'config/frozen.json').read_text());modelkey=cfg['model_path']
  if modelkey not in cache:cache[modelkey]=load(cfg,301,'cuda',train=False)
  model,tok=cache[modelkey];checkpoint=job.get('checkpoint')
  if checkpoint:
   checkpoint=Path(checkpoint);assert (checkpoint/'checkpoint.json').exists()
   state=load_file(str(checkpoint/'adapter_model.safetensors'));res=set_peft_model_state_dict(model,state,adapter_name='default');assert not res.unexpected_keys;del state
  rows=readrows(taskroot/f'data/{job["split"]}.jsonl')[job['shard']::job['shards']]
  if checkpoint:outputs,seconds=generate(model,tok,rows,job['condition'],cfg,False)
  else:
   with model.disable_adapter():outputs,seconds=generate(model,tok,rows,job['condition'],cfg,False)
  saverows(out/'predictions.jsonl',outputs)
  write(out/'complete.json',dict(**job,n=len(rows),correct=sum(x['grading']['strict'] for x in outputs),header_correct=sum(x['grading']['header_compliant'] for x in outputs),generated_tokens=sum(x['generated_tokens'] for x in outputs),generate_seconds=sum(x['allocated_generate_seconds'] for x in outputs),wall_seconds=time.time()-begin,predictions_sha256=sha(out/'predictions.jsonl'),config_sha256=sha(taskroot/'config/frozen.json'),worker=a.worker,finished=time.time()))
  print(json.dumps(dict(job=str(jobpath),n=len(rows),seconds=time.time()-begin)),flush=True)
 except BaseException:
  write(out/'failure.json',dict(traceback=traceback.format_exc(),time=time.time()));raise
print('EVALUATOR_DONE',flush=True)
