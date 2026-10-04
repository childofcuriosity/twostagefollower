from common import *
import os,time
from transformers import AutoTokenizer
assert not (R/'data/manifest.json').exists(),'Data already frozen; do not overwrite'
used={key(EXAMPLE)};sources=[];seen=set()
# Read all existing dataset directories; skip huge model/run artifacts. Original evaluated rows originate in these datasets.
for path,dirs,files in os.walk(B):
 dirs[:]=[d for d in dirs if d not in ['grpo-binary','models','model','runs','checkpoints','snapshots','frozen-source','.git','__pycache__']]
 if 'data' not in Path(path).relative_to(B).parts:continue
 for f in files:
  if not f.endswith('.jsonl'):continue
  p=Path(path)/f;resolved=p.resolve()
  if resolved in seen:continue
  seen.add(resolved);n=0
  for line in p.read_text().splitlines():
   x=json.loads(line)
   if isinstance(x,dict) and isinstance(x.get('chain'),list) and len(x['chain'])==2 and isinstance(x.get('x'),list) and len(x['x'])==4:
    used.add(key(x));n+=1
  sources.append(dict(path=str(p),sha256=sha(p),L2_rows=n))
old_count=len(used);saverows(R/'data/excluded-old-L2.jsonl',[dict(chain=list(k[0]),x=list(k[1])) for k in sorted(used)])
manifest=dict(created=time.time(),model_revision=json.loads((MODEL/'download-manifest.json').read_text())['revision'],old_unique_L2_excluded=old_count,sources=sources,datasets={},prompt_sha256={c:sha(OLD/f'prompts/{c}.txt') for c in CONDITIONS},legacy_score_sha256=sha(B/'scale-study/src/audit.py'))
tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True)
for split,n,seed in [('train',4096,910001),('validation',256,910002),('test',512,910003),('precheck',64,910004)]:
 rng=random.Random(seed);rows=[]
 while len(rows)<n:
  row=dict(id=f'{split}-{len(rows):05d}',split=split,depth=2,chain=[rng.randrange(9) for _ in range(2)],x=[rng.randrange(10) for _ in range(4)])
  if key(row) in used:continue
  used.add(key(row));rows.append(row)
 p=R/f'data/{split}.jsonl';saverows(p,rows)
 limits={c:dict(max_target=max(len(tok(target(x,c),add_special_tokens=False).input_ids)+1 for x in rows),max_input=max(len(tok.apply_chat_template([dict(role='user',content=prompt(x,c))],tokenize=True,add_generation_prompt=True)) for x in rows)) for c in CONDITIONS}
 assert all(v['max_target']<=256 and v['max_input']+256<=32768 for v in limits.values())
 manifest['datasets'][split]=dict(n=n,seed=seed,sha256=sha(p),limits=limits)
for seed in SEEDS:
 order=list(range(4096));random.Random(seed).shuffle(order);order=order[:1600]
 write(R/f'data/order-s{seed}.json',dict(seed=seed,indices=order,updates=[order[i:i+16] for i in range(0,1600,16)]))
for c in CONDITIONS:
 (R/'config'/f'prompt-{c}.txt').write_text(prior.template(c));assert sha(R/'config'/f'prompt-{c}.txt')==manifest['prompt_sha256'][c]
write(R/'data/manifest.json',manifest);print(json.dumps({k:v for k,v in manifest.items() if k!='sources'},indent=2))
