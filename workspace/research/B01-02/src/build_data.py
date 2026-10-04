import json,random,hashlib,itertools
from pathlib import Path
from dsl import NAMES,OPS,expand,signature,execute,prompt,target
from transformers import AutoTokenizer
ROOT=Path(__file__).resolve().parents[1];rng=random.Random(900)
libinfo=json.loads((ROOT/'data/library.json').read_text());lib=[v['ops'] for v in libinfo['selected']]
tok=AutoTokenizer.from_pretrained(ROOT/'model',local_files_only=True)
length=lambda s:len(tok(s,add_special_tokens=False).input_ids)
names=[s for s in NAMES if length('\n'+s+':')==length('\nstep:')]
if len(names)<len(lib):raise RuntimeError('Need token-length matched names')
names=names[:len(lib)]
worlds={'original':{'library':lib,'names':names},'renamed':{'library':lib,'names':names[1:]+names[:1]},'semantic':{'library':lib[1:]+lib[:1],'names':names}}
(ROOT/'data/worlds.json').write_text(json.dumps(worlds,indent=2))
trainchains=[(i,) for i in range(len(lib))]+list(itertools.product(range(len(lib)),repeat=2))
trainkeys={signature(expand(c,w['library'])) for c in trainchains for w in worlds.values()}
uid=0;seen=set()
def row(chain,split,pressure=False):
 global uid
 while True:
  x=tuple(rng.randrange(10) for _ in range(4))
  if pressure:
   a,b=rng.choices([0,1,8,9],k=2);x=rng.choice([(a,a,a,a),(a,b,b,a),(a,b,a,b)])
  key=(tuple(chain),x)
  if key not in seen:seen.add(key);break
 uid+=1
 return {'id':uid,'split':split,'chain':list(chain),'x':x,'depth':len(chain)}
train=[row(rng.choice(trainchains),'train') for _ in range(4096)]
iid=[row(rng.choice(trainchains),'iid') for _ in range(128)]
dev=[row(rng.choice(trainchains),'dev') for _ in range(128)]
usedkeys=set(trainkeys);ood=[];dev_ood=[];pressure=[];tries=0
for depth in [3,4,5]:
 count=0
 while count<44:
  tries+=1
  if tries>200000:raise RuntimeError('Insufficient semantically novel tasks')
  c=tuple(rng.randrange(len(lib)) for _ in range(depth));keys={signature(expand(c,w['library'])) for w in worlds.values()}
  if keys & usedkeys:continue
  usedkeys.update(keys)
  if count<32:ood.extend(row(c,'ood') for _ in range(4))
  elif count<40:dev_ood.extend(row(c,'dev_ood') for _ in range(4))
  else:pressure.extend(row(c,'pressure',True) for _ in range(4))
  count+=1
for name,rows in [('train',train),('dev',dev+dev_ood),('test',iid+ood+pressure)]:
 (ROOT/f'data/{name}.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
# Verify exact active-token equality for primary control on every training row.
checks={};maxseq=0
for condition in ['flat','macro','shuffled','natural']:
 lens=[length(target(r,lib,condition,names)) for r in train]
 checks[condition]={'target_tokens':sum(lens),'min':min(lens),'max':max(lens)}
 if condition=='flat':flat=lens
 elif condition in ['macro','shuffled']:assert lens==flat,(condition,'token mismatch')
 maxseq=max(maxseq,max(length(prompt(r,names)+target(r,lib,condition,names)) for r in train))
report={'train':len(train),'dev':len(dev+dev_ood),'test':len(iid+ood+pressure),'primary_token_match':True,'target_token_counts':checks,'max_train_sequence':maxseq,'train_unique_semantic_keys_all_worlds':len(trainkeys),'test_ood_semantic_overlap_with_train':0,'ood_depths':[3,4,5],'stress_is_input_distribution_not_new_domain':True,'hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'data').glob('*.json*')}}
(ROOT/'data/audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
