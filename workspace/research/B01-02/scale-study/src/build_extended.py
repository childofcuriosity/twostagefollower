import json,random,sys,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R.parent;sys.path.insert(0,str(P/'src'));import dsl
lib=json.loads((P/'data/worlds.json').read_text())['original']['library'];used=set()
for name in ['train','dev','test']:
 for line in (P/f'data/{name}.jsonl').read_text().splitlines():used.add(dsl.signature(dsl.expand(json.loads(line)['chain'],lib)))
nprior=len(used);rng=random.Random(2026092417);rows=[];count=0
for depth in [3,4,5,6,8]:
 selected=0
 for attempt in range(100000):
  c=[rng.randrange(len(lib)) for _ in range(depth)];sig=dsl.signature(dsl.expand(c,lib))
  if sig in used:continue
  used.add(sig);xs=set()
  while len(xs)<4:xs.add(tuple(rng.randrange(10) for _ in range(4)))
  for x in sorted(xs):count+=1;rows.append(dict(id=100000+count,split=f'length{depth}',chain=c,x=list(x),depth=depth,template=selected))
  selected+=1
  if selected==24:break
 assert selected==24,(depth,selected)
p=R/'data/extended-test.jsonl';assert not p.exists();p.write_text(''.join(json.dumps(r)+'\n' for r in rows))
(R/'analysis/extended-data-registration.json').write_text(json.dumps(dict(seed=2026092417,rows=len(rows),templates=120,depths=[3,4,5,6,8],programs_per_depth=24,inputs_per_program=4,prior_semantic_functions=nprior,new_semantic_functions=len(used)-nprior,no_overlap_with_prior_train_dev_test=True,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),max_new_tokens=512,reason='Prespecified held-out length extrapolation before new model results; terminal function disjoint across every template'),indent=2))
print('Extended confirmation test:',len(rows),'rows; no semantic overlap with previous train/dev/test')
