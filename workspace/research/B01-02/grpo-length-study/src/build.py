from common import *
import math,shutil,time
from transformers import AutoTokenizer,AutoConfig
assert not (ROOT/'datasets/manifest.json').exists(),'Data already built'
lengths=[3,4,5,6,7];used={L:set() for L in lengths};sources=[];seen=set()
for path,dirs,files in os.walk(B):
 dirs[:]=[d for d in dirs if d not in ['grpo-length-study','models','model','runs','checkpoints','snapshots','frozen-source','.git','__pycache__','eval']]
 if 'data' not in Path(path).relative_to(B).parts:continue
 for f in files:
  if not f.endswith('.jsonl'):continue
  p=Path(path)/f
  if p.resolve() in seen:continue
  seen.add(p.resolve());counts={L:0 for L in lengths}
  for line in p.read_text().splitlines():
   x=json.loads(line)
   if not isinstance(x,dict) or not isinstance(x.get('chain'),list) or not isinstance(x.get('x'),list) or len(x['x'])!=4:continue
   L=len(x['chain'])
   if L in used:used[L].add(key(x));counts[L]+=1
  if sum(counts.values()):sources.append(dict(path=str(p),sha256=sha(p),counts=counts))
base=json.loads((ROOT/'config/inherited.json').read_text());man=dict(created=time.time(),sources=sources,lengths={})
for L in lengths:
 folder=ROOT/f'datasets/L{L}';folder.mkdir(exist_ok=True)
 saverows(folder/'excluded-old.jsonl',[dict(chain=list(k[0]),x=list(k[1])) for k in sorted(used[L])]);entry=dict(old_unique_excluded=len(used[L]),datasets={})
 for offset,(split,n) in enumerate([('train',4096),('validation',256),('test',512),('precheck',64)],1):
  seed=920000+10*L+offset;rng=random.Random(seed);rows=[]
  while len(rows)<n:
   row=dict(id=f'L{L}-{split}-{len(rows):05d}',split=split,depth=L,chain=[rng.randrange(9) for _ in range(L)],x=[rng.randrange(10) for _ in range(4)])
   if key(row) in used[L]:continue
   used[L].add(key(row));rows.append(row)
  p=folder/f'{split}.jsonl';saverows(p,rows);entry['datasets'][split]=dict(n=n,seed=seed,sha256=sha(p))
 man['lengths'][str(L)]=entry
for taskpath in sorted(ROOT.glob('*/task.json')):
 root=taskpath.parent;task=json.loads(taskpath.read_text());model=B/f'prompt-only/models/qwen{task["model"]}';L=task['length'];tok=AutoTokenizer.from_pretrained(model,local_files_only=True);mcfg=AutoConfig.from_pretrained(model,local_files_only=True)
 entry=man['lengths'][str(L)];manifest=dict(created=time.time(),model_revision=json.loads((model/'download-manifest.json').read_text())['revision'],task=task['id'],length=L,old_unique_excluded=entry['old_unique_excluded'],datasets={},prompt_sha256={c:sha(OLD/f'prompts/{c}.txt') for c in CONDITIONS},legacy_score_sha256=sha(B/'scale-study/src/audit.py'))
 for split,meta in entry['datasets'].items():
  p=root/f'data/{split}.jsonl';shutil.copy2(ROOT/f'datasets/L{L}/{split}.jsonl',p);rows=readrows(p);limits={}
  for c in CONDITIONS:
   targets=tok([target(x,c) for x in rows],add_special_tokens=False).input_ids
   inputs=tok([tok.apply_chat_template([dict(role='user',content=prompt(x,c))],tokenize=False,add_generation_prompt=True) for x in rows],add_special_tokens=False).input_ids
   limits[c]=dict(max_target=max(map(len,targets))+1,max_input=max(map(len,inputs)))
  manifest['datasets'][split]=dict(meta,limits=limits)
 cap=math.ceil((1.25*max(v['max_target'] for m in manifest['datasets'].values() for v in m['limits'].values())+64)/256)*256
 assert all(v['max_input']+cap<=mcfg.max_position_embeddings for m in manifest['datasets'].values() for v in m['limits'].values())
 task.update(max_new_tokens=cap,model_revision=manifest['model_revision']);write(taskpath,task)
 manifest.update(max_new_tokens=cap,context=mcfg.max_position_embeddings);write(root/'data/manifest.json',manifest)
 for seed in SEEDS:
  order=list(range(4096));random.Random(seed).shuffle(order);order=order[:1600];write(root/f'data/order-s{seed}.json',dict(seed=seed,indices=order,updates=[order[i:i+16] for i in range(0,1600,16)]))
 for c in CONDITIONS:
  (root/'config'/f'prompt-{c}.txt').write_text(prior.template(c));assert sha(root/'config'/f'prompt-{c}.txt')==manifest['prompt_sha256'][c]
 cfg=dict(base,protocol='precheck-v1',task_id=task['id'],model_path=str(model),model_revision=manifest['model_revision'],length=L,max_new_tokens=cap)
 write(root/'config/precheck-v1.json',cfg)
 print(task['id'],'cap',cap,'excluded',entry['old_unique_excluded'],flush=True)
# Exact shared L5 data between sizes.
for split in ['train','validation','test','precheck']:assert sha(ROOT/f'7b-L5/data/{split}.jsonl')==sha(ROOT/f'14b-L5/data/{split}.jsonl')
write(ROOT/'datasets/manifest.json',man)
print('DATA_PREPARED',flush=True)
