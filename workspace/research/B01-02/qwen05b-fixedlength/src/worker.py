from common import *
import argparse,time,traceback,types

p=argparse.ArgumentParser();p.add_argument('--length',type=int,required=True);p.add_argument('--phase',choices=('explore','formal'),required=True);p.add_argument('--condition',choices=CONDITIONS,required=True);p.add_argument('--seed',type=int,required=True);p.add_argument('--retry',type=int,default=0);a=p.parse_args()
assert a.length>=10
assert (a.seed in EXPLORE_SEEDS and a.condition in ('flat','macro')) if a.phase=='explore' else (a.seed in FORMAL_SEEDS)
data_root=R/f'data/L{a.length}'
if a.phase=='formal':data_root=data_root/'formal'
pre=json.loads((data_root/('formal-manifest.json' if a.phase=='formal' else 'explore-manifest.json')).read_text())
assert sha(B/'src/run.py')==pre['original_driver_sha256']
assert sha(B/'src/dsl.py')==pre['dsl_sha256']
assert sha(data_root/'train.jsonl')==pre['train_sha256'] and sha(data_root/'test.jsonl')==pre['test_sha256']
run=R/f'runs/{a.phase}-L{a.length}-{a.condition}-s{a.seed}{f"-retry{a.retry}" if a.retry else ""}'
run.mkdir(parents=True,exist_ok=False)
write(run/'job.json',vars(a))
(run/'data').mkdir();(run/'runs').mkdir();(run/'model').symlink_to(MODEL.resolve(),target_is_directory=True)
for src in data_root.iterdir():
 if src.is_file() and src.name!='worlds.json':(run/'data'/src.name).symlink_to(src.resolve())
worlds=json.loads((B/'data/worlds.json').read_text())
if a.condition=='alias':worlds['original']['names']=ALIASES
write(run/'data/worlds.json',worlds)
driver=snapshot()
assert driver.count('if maxlen>256:')==1 and driver.count('max_new_tokens=256')==1
driver=driver.replace('if maxlen>256:',f'if maxlen>{pre["train_cap"]}:')
driver=driver.replace('max_new_tokens=256',f'max_new_tokens={pre["generation_cap"]}')
snap=run/'driver_snapshot.py';snap.write_text(driver)
m=types.ModuleType('isolated_driver');m.__file__=str(snap)
exec(compile(driver,str(snap),'exec'),m.__dict__)
m.ROOT=run;m.target=target
microbatch=8 if a.length>=40 else 16
accum=32//microbatch
sys.argv=[str(snap),'--condition',a.condition,'--seed',str(a.seed),'--microbatch',str(microbatch),'--accum',str(accum),'--steps','512']
start=time.time()
try:
 m.main()
 q=run/'runs'/f'{a.condition}-original-s{a.seed}'
 summ=json.loads((q/'summary.json').read_text())
 assert summ['training']['counts']['examples']==16384
 assert len((q/'predictions.jsonl').read_text().splitlines())==512
 write(run/'complete.json',dict(job=vars(a),seconds=time.time()-start,summary=summ,driver_sha256=sha(snap),test_sha256=pre['test_sha256']))
except BaseException as exc:
 write(run/'failed.json',dict(error=repr(exc),traceback=traceback.format_exc(),time=time.time()))
 raise
