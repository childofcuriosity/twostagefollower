import argparse,json,time,os,subprocess,sys,concurrent.futures,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--model',choices=['qwen32b','qwen7b'],required=True);ap.add_argument('--condition',choices=['flat','macro']);ap.add_argument('--seed',type=int);a=ap.parse_args()
if a.condition:
 import torch
 from transformers import AutoModelForCausalLM,AutoTokenizer
 from peft import PeftModel
 import train
 train.ROOT=ROOT/a.model;torch.set_num_threads(4)
 run=train.ROOT/f'runs/{a.condition}-original-s{a.seed}';out=run/'checkpoint-tests';out.mkdir(exist_ok=True)
 tok=AutoTokenizer.from_pretrained(train.ROOT/'model',local_files_only=True);tok.pad_token=tok.eos_token
 model=AutoModelForCausalLM.from_pretrained(train.ROOT/'model',torch_dtype=torch.bfloat16,attn_implementation='sdpa',local_files_only=True,low_cpu_mem_usage=True).cuda()
 model=PeftModel.from_pretrained(model,run/'checkpoints/step0000/adapter',adapter_name='step0000')
 world=json.loads((train.ROOT/'data/worlds.json').read_text())['original'];rows=train.read('test');summaries=[]
 for step in [0,16,64,128,256]:
  # A dev output is written only after this checkpoint has been fully saved.
  while not (run/f'step{step:04d}-dev.jsonl').exists():time.sleep(60)
  tag=f'step{step:04d}';meta=out/f'{tag}-summary.json'
  if meta.exists():summaries.append(json.loads(meta.read_text()));continue
  if step:model.load_adapter(run/f'checkpoints/{tag}/adapter',adapter_name=tag)
  model.set_adapter(tag);model.config.use_cache=True;start=time.time()
  result={'step':step,'without_library':train.evaluate(model,tok,rows,world,out/f'{tag}-predictions.jsonl')}
  if step==0:result['with_library']=train.evaluate(model,tok,rows,world,out/f'{tag}-with-library.jsonl',True)
  result['wall_seconds']=time.time()-start;meta.write_text(json.dumps(result,indent=2));summaries.append(result);print('CHECKPOINT',a.model,a.condition,a.seed,step,flush=True)
 (out/'completed.json').write_text(json.dumps(summaries,indent=2));sys.exit(0)
marker=ROOT/f'analysis/{a.model}-completed.json'
while not marker.exists():time.sleep(60)
records=json.loads(marker.read_text());assert len(records)==6 and all(r['returncode']==0 for r in records),'Training did not complete successfully'
gpus=[0,1,2] if a.model=='qwen32b' else [4,5,6]
def worker(seed,gpu):
 results=[]
 for condition in ['flat','macro']:
  if a.model=='qwen32b' and condition=='macro' and (ROOT/'analysis/early-macro-checkpoints-claim.json').exists():
   marker=ROOT/f'analysis/early-checkpoints-macro-s{seed}.json'
   while not marker.exists():time.sleep(60)
   record=json.loads(marker.read_text());assert record['returncode']==0,record
   done=ROOT/f'qwen32b/runs/macro-original-s{seed}/checkpoint-tests/completed.json'
   assert [x['step'] for x in json.loads(done.read_text())]==[0,16,64,128,256]
   results.append(record);continue
  claim=ROOT/'analysis/remote-checkpoints-claim.json'
  if a.model=='qwen32b' and condition=='flat' and claim.exists():
   assigned=json.loads(claim.read_text())['seeds']
   if seed in assigned:
    remote=ROOT/f'analysis/remote-checkpoints-flat-s{seed}.json'
    while not remote.exists():time.sleep(60)
    record=json.loads(remote.read_text());assert record['returncode']==0,record
    done=ROOT/f'qwen32b/runs/flat-original-s{seed}/checkpoint-tests/completed.json'
    assert [x['step'] for x in json.loads(done.read_text())]==[0,16,64,128,256]
    results.append(record);continue
  env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu);start=time.time()
  with (ROOT/'runs'/f'checkpoints-{a.model}-{condition}-s{seed}.log').open('x') as f:
   p=subprocess.run([sys.executable,'-u',__file__,'--model',a.model,'--condition',condition,'--seed',str(seed)],env=env,stdout=f,stderr=subprocess.STDOUT)
  results.append(dict(condition=condition,seed=seed,returncode=p.returncode,wall_seconds=time.time()-start))
  if p.returncode:break
 return results
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=sum(list(pool.map(lambda x:worker(*x),zip([11,22,33],gpus))),[])
(ROOT/f'analysis/{a.model}-checkpoint-tests-completed.json').write_text(json.dumps(results,indent=2));assert len(results)==6 and all(r['returncode']==0 for r in results)
print('All fixed checkpoint tests completed',a.model,flush=True)
