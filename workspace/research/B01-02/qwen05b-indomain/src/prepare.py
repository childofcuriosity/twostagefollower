from common import *
from transformers import AutoTokenizer

tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True)
source=B/'src/run.py'
train=[json.loads(x) for x in (B/'data/train.jsonl').read_text().splitlines()]
test=[json.loads(x) for x in (B/'data/test.jsonl').read_text().splitlines() if json.loads(x)['split']=='iid']
assert len(train)==4096 and len(test)==128 and set(len(x['chain']) for x in train+test)=={1,2}
checks=[]
for condition in CONDITIONS:
 names=ALIASES if condition=='alias' else WORLD['names']
 maxlen=0;tokens=0
 for row in train:
  t=target(row,WORLD['library'],condition,names)
  old=dsl.target(row,WORLD['library'],'macro',WORLD['names'])
  strip=lambda s:'\n'.join(x for x in s.splitlines() if not re.fullmatch(r'[A-Za-z][A-Za-z0-9]*:',x))
  assert strip(t)==strip(old)
  p=dsl.prompt(row,names);p0=dsl.prompt(row,WORLD['names'])
  if condition!='alias':assert p==p0
  else:
   for a,b in zip(ALIASES,WORLD['names']):p=p.replace(a,b)
   assert p==p0
  maxlen=max(maxlen,len(tok(dsl.prompt(row,names),add_special_tokens=False).input_ids)+len(tok(t,add_special_tokens=False).input_ids)+1)
  tokens+=len(tok(t,add_special_tokens=False).input_ids)+1
 assert maxlen<=256
 checks.append(dict(condition=condition,rows=len(train),max_training_length=maxlen,target_tokens_per_epoch=tokens))
write(R/'analysis/preflight.json',dict(model_revision=json.loads((MODEL/'download-manifest.json').read_text())['revision'],model_files_sha256={x.name:sha(x) for x in MODEL.iterdir() if x.is_file() and x.name!='download-manifest.json'},source_sha256=sha(source),train_sha256=sha(B/'data/train.jsonl'),test_sha256=sha(B/'data/test.jsonl'),worlds_sha256=sha(B/'data/worlds.json'),registration_sha256=sha(R/'REGISTRATION.md'),checks=checks,aliases=dict(zip(WORLD['names'],ALIASES)),seeds=list(SEEDS)))
print('prepared',len(SEEDS),'STEP baseline runs; target lengths',checks)
