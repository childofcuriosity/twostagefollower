from common import *
import numpy as np
registration=json.loads((ROOT/'analysis/registration.json').read_text())
for name,h in registration['sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
# DP cross-check by exhaustive segmentation on random short programs.
def brute(p,lib):
 if not p:return 0
 options=[1+brute(p[1:],lib)]
 for c in lib:
  ops=CANDIDATES[c]
  if p[:len(ops)]==ops:options.append(1+brute(p[len(ops):],lib))
 return min(options)
rng=random.Random(331)
for _ in range(100):
 p=tuple(rng.choices(OPS,k=8));lib=rng.sample(range(252),3);assert description_cost(p,lib)==brute(p,lib)
for f in load():
 assert not ({sig(tuple(p)) for p in f['support']}&{sig(tuple(p)) for p in f['test']})
 assert len(f['support'])==16 and len(f['test'])==128
 for c in f['motifs']:
  assert sig(CANDIDATES[c]) not in {sig(tuple(r['ops'])) for r in json.loads((PARENT/'data/library.json').read_text())['selected']}
rows=[json.loads(l) for l in (ROOT/'analysis/rows.jsonl').read_text().splitlines()];assert len(rows)==192
for r in rows:
 f=load()[r['family']];assert select(f['support'],r['proposals'])==r['selected'];assert utility(f['test'],r['selected'])==r['test']
 assert r['search']['solved']==sum(x is not None for x in r['search']['first_discovery_costs'])
 for cost in r['search']['first_discovery_costs']:
  if cost:assert cost[0]<=3000 and cost[1]>=cost[0]
for p in (ROOT/'runs').glob('*/proposals.jsonl'):
 rs=[json.loads(l) for l in p.read_text().splitlines()];assert len(rs)==128
 for r in rs:assert r['raw']==','.join(CANDIDATES[r['candidate']])+'\n'
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.rglob('*') if p.is_file() and p.suffix in ['.py','.md','.json','.jsonl'] and p.name!='verification.json'}
(ROOT/'analysis/verification.json').write_text(json.dumps({'registered_files_unchanged':True,'independent_DP_checks':100,'families':8,'rows_verified':len(rows),'manifest':manifest},indent=2));print('Verified',len(rows),'analysis rows; registration unchanged')
