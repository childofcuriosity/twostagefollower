from common import *
from transformers import AutoTokenizer
import re

jobs=[];checks=[];freeze={};baseline={}
for model,root in ROOTS.items():
 tok=AutoTokenizer.from_pretrained(root/'model',local_files_only=True)
 for p in (source(model),B/'src/dsl.py',root/'data/train.jsonl',root/'data/test.jsonl',S/'data/extended-test.jsonl'):
  freeze[str(p.relative_to(B))]=sha(p)
 for condition in CONDITIONS:
  for seed in (11,22,33):
   paths=(root/f'runs/{condition}-original-s{seed}/predictions.jsonl' if condition in ('flat','macro') else L/f'runs/{model}-{condition}-s{seed}/runs/{condition}-original-s{seed}/predictions.jsonl',
          S/f'extended/{model}/{condition}-s{seed}.jsonl' if condition in ('flat','macro') else L/f'runs/{model}-{condition}-s{seed}/independent.jsonl')
   for path in paths:baseline[str(path.relative_to(B))]=sha(path)
  names=ALIASES if condition=='alias' else WORLD['names']
  count=0;new_tokens=0;old_tokens=0
  for line in (root/'data/train.jsonl').read_text().splitlines():
   row=json.loads(line);old=dsl.target(row,WORLD['library'],'macro',WORLD['names']);new=target(row,WORLD['library'],condition,names)
   strip=lambda s:'\n'.join(x for x in s.splitlines() if not re.fullmatch(r'[A-Za-z][A-Za-z0-9]*:',x))
   assert strip(new)==strip(old)
   prompt=dsl.prompt(row,names);base_prompt=dsl.prompt(row,WORLD['names'])
   if condition!='alias':assert prompt==base_prompt
   else:
    for a,b in zip(ALIASES,WORLD['names']):prompt=prompt.replace(a,b)
    assert prompt==base_prompt
   new_tokens+=len(tok(new,add_special_tokens=False).input_ids)+1
   old_tokens+=len(tok(old,add_special_tokens=False).input_ids)+1
   count+=1
  assert count==4096
  checks.append(dict(model=model,condition=condition,rows=count,target_tokens=new_tokens,macro_tokens=old_tokens))
  for seed in SEEDS:jobs.append(dict(model=model,condition=condition,seed=seed,steps=512,microbatch=16,accum=2,lr=3e-4))
assert len(jobs)==204
write(R/'analysis/preflight.json',dict(passed=True,source_hashes=freeze,baseline_hashes=baseline,checks=checks,aliases=dict(zip(WORLD['names'],ALIASES)),registration_sha256=sha(R/'REGISTRATION.md')))
write(R/'analysis/jobs.json',jobs)
print('prepared',len(jobs),'jobs',flush=True)
