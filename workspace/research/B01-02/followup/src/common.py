import sys,json,itertools,random,hashlib
from pathlib import Path
from functools import lru_cache
ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT.parent
sys.path.insert(0,str(PARENT/'src'))
from dsl import OPS,execute,signature
CANDIDATES=[p for n in (2,3) for p in itertools.product(OPS,repeat=n)]
BASEPOINTS=[(0,0,0,0)]+[tuple(int(i==j) for i in range(4)) for j in range(4)]
@lru_cache(None)
def sig(p):return tuple(execute(x,p) for x in BASEPOINTS)
IDENTITY=sig(())
def load():return json.loads((ROOT/'data/tasks.json').read_text())
def description_cost(program,library):
 p=tuple(program);d=[0]+[999]*len(p)
 for i in range(len(p)):
  d[i+1]=min(d[i+1],d[i]+1)
  for c in library:
   op=CANDIDATES[c];n=len(op)
   if p[i:i+n]==op:d[i+n]=min(d[i+n],d[i]+1)
 return d[-1]
def utility(programs,library):
 raw=sum(map(len,programs));definition=sum(len(CANDIDATES[c])+1 for c in library)
 encoded=sum(description_cost(p,library) for p in programs)+definition
 return {'raw_length':raw,'encoded_length':encoded,'definition_cost':definition,'net_saving':raw-encoded,'fraction':(raw-encoded)/raw}
def select(programs,proposals):
 available=[];seen={IDENTITY}
 for c in proposals:
  s=sig(CANDIDATES[c])
  if s not in seen:available.append(c);seen.add(s)
 chosen=[]
 for _ in range(3):
  old=utility(programs,chosen)['net_saving'];best=None
  for c in sorted(available):
   value=utility(programs,chosen+[c])['net_saving']
   if value>old:old=value;best=c
  if best is None:break
  chosen.append(best);available.remove(best)
 return sorted(chosen)
def build():
 rng=random.Random(91407);old={sig(tuple(v['ops'])) for v in json.loads((PARENT/'data/library.json').read_text())['selected']}
 pool=[i for i,p in enumerate(CANDIDATES) if sig(p) not in old|{IDENTITY}];rng.shuffle(pool)
 families=[];used=set()
 for f in range(8):
  motifs=[]
  for i in pool:
   if sig(CANDIDATES[i]) not in used:
    motifs.append(i);used.add(sig(CANDIDATES[i]))
    if len(motifs)==3:break
  support=[];test=[];asts=set();support_sigs=set();tries=0
  while len(test)<128:
   tries+=1
   if tries>100000:raise RuntimeError('Insufficient independent task capacity')
   p=[]
   for _ in range(rng.choice([3,4,5])):
    p.extend(CANDIDATES[rng.choice(motifs)] if rng.random()<.8 else [rng.choice(OPS)])
   p=tuple(p);s=sig(p)
   if p in asts:continue
   if len(support)<16:support.append(p);support_sigs.add(s);asts.add(p)
   elif s not in support_sigs:test.append(p);asts.add(p)
  families.append(dict(id=f,motifs=motifs,support=support,test=test))
 (ROOT/'data/tasks.json').write_text(json.dumps(families,indent=2))
 (ROOT/'data/candidates.json').write_text(json.dumps(CANDIDATES))
 print('Built',len(families),'families')
if __name__=='__main__':build()
