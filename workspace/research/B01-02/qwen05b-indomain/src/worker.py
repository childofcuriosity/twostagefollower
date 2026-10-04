from common import *
import argparse,types,time,traceback

p=argparse.ArgumentParser();p.add_argument('--condition',choices=CONDITIONS,required=True);p.add_argument('--seed',type=int,required=True);p.add_argument('--max-length',type=int,default=2);a=p.parse_args()
assert a.seed in SEEDS and a.max_length in range(2,9)
run=R/f'runs/L{a.max_length}-{a.condition}-s{a.seed}'
run.mkdir(parents=True,exist_ok=False)
write(run/'job.json',vars(a))
data_root=B/'data' if a.max_length==2 else R/f'data/L{a.max_length}'
pre=json.loads((R/'analysis/preflight.json').read_text()) if a.max_length==2 else json.loads((data_root/'manifest.json').read_text())
assert sha(B/'src/run.py')==pre['source_sha256']
if a.max_length==2:
 assert sha(data_root/'train.jsonl')==pre['train_sha256'] and sha(data_root/'test.jsonl')==pre['test_sha256']
else:
 assert sha(data_root/'train.jsonl')==pre['sha256']['train'] and sha(data_root/'test.jsonl')==pre['sha256']['test']
assert sha(B/'data/worlds.json')==pre['worlds_sha256']
(run/'data').mkdir();(run/'runs').mkdir()
(run/'model').symlink_to(MODEL.resolve(),target_is_directory=True)
for src in data_root.iterdir():
 if src.name!='worlds.json' and src.is_file():(run/'data'/src.name).symlink_to(src.resolve())
worlds=json.loads((B/'data/worlds.json').read_text())
if a.condition=='alias':worlds['original']['names']=ALIASES
write(run/'data/worlds.json',worlds)
driver=snapshot()
if a.max_length>=4:
 train_cap=pre['training_sequence_cap'];generation_cap=pre['generation_cap']
 if train_cap!=256:
  assert driver.count('if maxlen>256:')==1
  driver=driver.replace('if maxlen>256:',f'if maxlen>{train_cap}:')
 if generation_cap!=256:
  assert driver.count('max_new_tokens=256')==1
  driver=driver.replace('max_new_tokens=256',f'max_new_tokens={generation_cap}')
snap=run/'driver_snapshot.py';snap.write_text(driver)
m=types.ModuleType('isolated_driver');m.__file__=str(snap)
exec(compile(snap.read_text(),str(snap),'exec'),m.__dict__)
m.ROOT=run;m.target=target
original_read=m.read
def read(name):
 rows=original_read(name)
 return [x for x in rows if x['split']=='iid'] if name=='test' and a.max_length==2 else rows
m.read=read
sys.argv=[str(snap),'--condition',a.condition,'--seed',str(a.seed),'--microbatch','16','--accum','2','--steps','512']
start=time.time()
try:
 m.main()
 legacy=run/'runs'/f'{a.condition}-original-s{a.seed}'
 summ=json.loads((legacy/'summary.json').read_text())
 assert summ['training']['counts']['examples']==16384
 assert len((legacy/'predictions.jsonl').read_text().splitlines())==pre.get('test_rows',128)
 write(run/'complete.json',dict(job=vars(a),seconds=time.time()-start,summary=summ,driver_sha256=sha(snap)))
except BaseException as e:
 write(run/'failed.json',dict(error=repr(e),traceback=traceback.format_exc(),time=time.time()))
 raise
