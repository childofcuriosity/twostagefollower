from common import *
import argparse,collections,time
from transformers import AutoTokenizer

p=argparse.ArgumentParser();p.add_argument('--length',type=int,required=True);p.add_argument('--formal-test',action='store_true');a=p.parse_args()
assert a.length>=10
L=a.length;root=R/f'data/L{L}'
if a.formal_test:
 assert (root/'explore-manifest.json').exists()
 root=root/'formal'
else:
 root.mkdir(parents=True,exist_ok=False)
root.mkdir(parents=True,exist_ok=True)
train_path=R/f'data/L{L}/train.jsonl'
if a.formal_test:
 train=[json.loads(x) for x in train_path.read_text().splitlines()]
 explore=[json.loads(x) for x in (R/f'data/L{L}/explore-test.jsonl').read_text().splitlines()]
else:
 train=[];explore=[]
used={(tuple(x['chain']),tuple(x['x'])) for x in train+explore}
def generate(n,seed,split,offset):
 rng=random.Random(seed);rows=[];attempts=0
 while len(rows)<n:
  chain=tuple(rng.randrange(9) for _ in range(L))
  x=tuple(rng.randrange(10) for _ in range(4))
  key=(chain,x);attempts+=1
  if key in used:continue
  used.add(key);rows.append(dict(id=offset+len(rows)+1,split=split,chain=list(chain),x=list(x),depth=L))
 return rows,attempts
if not a.formal_test:
 train,train_attempts=generate(4096,10000+L,'train',L*10_000_000)
 (root/'train.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in train))
test_seed=(30000 if a.formal_test else 20000)+L
test,test_attempts=generate(512,test_seed,'iid',L*10_000_000+(2_000_000 if a.formal_test else 1_000_000))
test_path=root/('test.jsonl' if a.formal_test else 'explore-test.jsonl')
test_path.write_text(''.join(json.dumps(x)+'\n' for x in test))
if not a.formal_test:
 (root/'test.jsonl').symlink_to(test_path.resolve())
 for name in ('worlds.json','library.json','dev.jsonl'):
  (root/name).symlink_to((B/'data'/name).resolve())
else:
 (root/'train.jsonl').symlink_to(train_path.resolve())
 for name in ('worlds.json','library.json','dev.jsonl'):
  (root/name).symlink_to((B/'data'/name).resolve())

tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True)
checks={}
for c in CONDITIONS:
 names=ALIASES if c=='alias' else WORLD['names']
 train_targets=[target(x,WORLD['library'],c,names) for x in train]
 test_targets=[target(x,WORLD['library'],c,names) for x in test]
 max_train=max(len(tok(dsl.prompt(x,names),add_special_tokens=False).input_ids)+len(tok(t,add_special_tokens=False).input_ids)+1 for x,t in zip(train,train_targets))
 max_target=max(len(tok(t,add_special_tokens=False).input_ids)+1 for t in test_targets)
 checks[c]=dict(max_train_sequence=max_train,max_test_target_tokens=max_target,
                target_tokens_per_epoch=sum(len(tok(t,add_special_tokens=False).input_ids)+1 for t in train_targets))
 assert all('\n'.join(y for y in t.splitlines() if not y.endswith(':') or y.startswith('Answer:'))=='\n'.join(y for y in target(x,WORLD['library'],'flat',WORLD['names']).splitlines() if not y.endswith(':') or y.startswith('Answer:')) for x,t in zip(train,train_targets))
caps=(256,512,1024,1536,2048,3072,4096)
train_cap=next(x for x in caps if x>=max(v['max_train_sequence'] for v in checks.values()))
gen_cap=next(x for x in caps if x>=max(v['max_test_target_tokens'] for v in checks.values()))
assert gen_cap>=max(v['max_test_target_tokens'] for v in checks.values())
manifest=dict(length=L,phase='formal' if a.formal_test else 'explore',train_rows=len(train),test_rows=len(test),
 train_seed=10000+L,test_seed=test_seed,train_attempts=train_attempts if not a.formal_test else None,test_attempts=test_attempts,
 train_sha256=sha(train_path),test_sha256=sha(test_path),train_cap=train_cap,generation_cap=gen_cap,
 target_limits=checks,model_revision=json.loads((MODEL/'download-manifest.json').read_text())['revision'],
 original_driver_sha256=sha(B/'src/run.py'),dsl_sha256=sha(B/'src/dsl.py'),
 fixed_aliases=dict(zip(WORLD['names'],ALIASES)),sampler='exact L calls, independent uniform tools and digits; unique chain+digits across train/explore/formal',
 created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
write(root/('formal-manifest.json' if a.formal_test else 'explore-manifest.json'),manifest)
print(json.dumps({k:manifest[k] for k in ('length','phase','train_rows','test_rows','train_cap','generation_cap','target_limits')},indent=2))
