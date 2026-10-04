from common import *
from transformers import AutoTokenizer
import ast
results=[];jobs=[];freeze={}
for model,root in ROOTS.items():
 tok=AutoTokenizer.from_pretrained(root/'model',local_files_only=True)
 for p in [source(model),B/'src/dsl.py']:
  freeze[str(p.relative_to(B))]=sha(p)
 # AST comparison isolates changed argument allow-list and output path; all training statements unchanged.
 orig=source(model).read_text();assert code(model).count("'position','alias'")==1
 for condition in ['position','alias']:
  names=ALIASES if condition=='alias' else WORLD['names']
  maxlen=0;tokens=0;orig_tokens=0;n=0
  for line in (root/'data/train.jsonl').read_text().splitlines():
   row=json.loads(line);old=dsl.target(row,WORLD['library'],'macro',WORLD['names']);new=target(row,WORLD['library'],condition,names)
   strip=lambda s:'\n'.join(x for x in s.splitlines() if not re.fullmatch(r'[A-Za-z][A-Za-z0-9]*:',x))
   assert strip(old)==strip(new)
   assert 'EndTool' not in new and 'Done' not in new
   p=dsl.prompt(row,names);p0=dsl.prompt(row,WORLD['names'])
   if condition=='position':assert p==p0
   else:
    back=p
    for a,b in zip(ALIASES,WORLD['names']):back=back.replace(a,b)
    assert back==p0
   enc=tok(p,add_special_tokens=False).input_ids+tok(new,add_special_tokens=False).input_ids+[tok.eos_token_id]
   maxlen=max(maxlen,len(enc));tokens+=len(tok(new,add_special_tokens=False).input_ids)+1;orig_tokens+=len(tok(old,add_special_tokens=False).input_ids)+1;n+=1
  assert n==4096 and maxlen<=256
  results.append(dict(model=model,condition=condition,rows=n,max_training_length=maxlen,new_target_tokens_per_epoch=tokens,old_target_tokens_per_epoch=orig_tokens,
   labels={s:tok(s+':',add_special_tokens=False).input_ids for s in (ALIASES if condition=='alias' else [f'step{i}' for i in range(1,9)])}))
  for seed in [11,22,33]:
   cp=root/f'runs/macro-original-s{seed}/config.json';c=json.loads(cp.read_text());f=json.loads((root/f'runs/flat-original-s{seed}/config.json').read_text())
   assert c['source_sha256']==sha(source(model))==f['source_sha256']
   for key in ['steps','microbatch','accum']:assert c['args'][key]==f['args'][key]
   assert (c['args']['steps'],c['args']['microbatch'],c['args']['accum'])==(512,16,2)
   jobs.append(dict(model=model,condition=condition,seed=seed,baseline_config=str(cp),source_hash=sha(source(model)),microbatch=16,accum=2,steps=512,lr=3e-4))
 for p in (root/'data').glob('*.json*'):freeze[str(p.relative_to(B))]=sha(p)
freeze[str((S/'data/extended-test.jsonl').relative_to(B))]=sha(S/'data/extended-test.jsonl')
write(R/'analysis/preflight.json',dict(passed=True,checks=results,aliases=dict(zip(WORLD['names'],ALIASES)),frozen_source_data_hashes=freeze))
write(R/'analysis/jobs.json',jobs)
print('Preflight passed:',len(jobs),'jobs; label token counts retained')
