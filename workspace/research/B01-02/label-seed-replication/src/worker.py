from common import *
import argparse,time,types,traceback

ap=argparse.ArgumentParser();ap.add_argument('--job',type=int,required=True);a=ap.parse_args()
job=json.loads((R/'analysis/jobs.json').read_text())[a.job]
model=job['model'];condition=job['condition'];seed=job['seed'];root=ROOTS[model]
run=R/'runs'/f'{model}-{condition}-s{seed}'
run.mkdir(parents=True,exist_ok=False)
write(run/'job.json',job)
pre=json.loads((R/'analysis/preflight.json').read_text())
assert sha(R/'REGISTRATION.md')==pre['registration_sha256']
for p,h in pre['source_hashes'].items():assert sha(B/p)==h,(p,'source changed')
(run/'data').mkdir();(run/'runs').mkdir()
(run/'model').symlink_to((root/'model').resolve(),target_is_directory=True)
for p in (root/'data').iterdir():
 if p.name!='worlds.json' and p.is_file():(run/'data'/p.name).symlink_to(p.resolve())
worlds=json.loads((root/'data/worlds.json').read_text())
if condition=='alias':worlds['original']['names']=ALIASES
write(run/'data/worlds.json',worlds)
snapshot=run/'driver_snapshot.py';snapshot.write_text(driver(model))
m=types.ModuleType('isolated_legacy_driver');m.__file__=str(snapshot)
exec(compile(snapshot.read_text(),str(snapshot),'exec'),m.__dict__)
m.ROOT=run;m.target=target
original_evaluate=m.evaluate

def independent(net,tok,world,out):
 import torch
 rows=[json.loads(line) for line in (S/'data/extended-test.jsonl').read_text().splitlines()]
 net.eval();net.config.use_cache=True;tok.padding_side='left';records=[];start=time.time()
 for ix in range(0,len(rows),4):
  batch=rows[ix:ix+4];prompts=[dsl.prompt(row,world['names']) for row in batch]
  ins=tok(prompts,return_tensors='pt',padding=True).to('cuda')
  with torch.inference_mode():z=net.generate(**ins,max_new_tokens=512,do_sample=False,pad_token_id=tok.eos_token_id,eos_token_id=tok.eos_token_id)
  tokens=z[:,ins.input_ids.shape[1]:]
  for row,prompt,raw,ids in zip(batch,prompts,tok.batch_decode(tokens,skip_special_tokens=True),tokens):
   expected=list(dsl.execute(row['x'],dsl.expand(row['chain'],world['library'])));pred=dsl.answer(raw)
   records.append({**row,'raw':raw,'expected':expected,'prediction':list(pred) if pred is not None else None,'correct':pred==tuple(expected),'generated_tokens':int((ids!=tok.eos_token_id).sum()),'max_new_tokens':512,'with_library':False,'prompt':prompt,'generated_token_ids':ids.tolist()})
 out.write_text(''.join(json.dumps(row)+'\n' for row in records))
 write(out.with_suffix('.summary.json'),dict(records=len(records),elapsed_seconds=time.time()-start,sha256=sha(out),batch_size=4,max_new_tokens=512))

def evaluate(net,tok,rows,world,out,with_library=False,fewshot=False):
 result=original_evaluate(net,tok,rows,world,out,with_library,fewshot)
 if out.name=='predictions.jsonl':independent(net,tok,world,run/'independent.jsonl')
 return result
m.evaluate=evaluate
sys.argv=[str(snapshot),'--condition',condition,'--seed',str(seed),'--microbatch','16','--accum','2','--steps','512']
if model=='qwen7b':sys.argv+=['--model','qwen7b','--lr','0.0003']
start=time.time()
try:
 m.main()
 legacy=run/'runs'/f'{condition}-original-s{seed}'
 summary=json.loads((legacy/'summary.json').read_text())
 assert summary['training']['counts']['examples']==16384
 assert len((legacy/'predictions.jsonl').read_text().splitlines())==560
 assert len((run/'independent.jsonl').read_text().splitlines())==480
 write(run/'complete.json',dict(job=job,legacy_output=str(legacy),seconds=time.time()-start,source_original_sha256=sha(source(model)),driver_sha256=sha(snapshot),summary=summary))
except BaseException as e:
 write(run/'failed.json',dict(error=repr(e),traceback=traceback.format_exc(),time=time.time()))
 raise
