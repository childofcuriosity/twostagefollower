import sys,json,random,itertools,hashlib,re
from pathlib import Path
from functools import lru_cache
ROOT=Path(__file__).resolve().parents[1];PARENT=ROOT.parent
sys.path.insert(0,str(PARENT/'src'))
import dsl
OPS=dsl.OPS
CANDIDATES=[p for n in (2,3) for p in itertools.product(OPS,repeat=n)]
@lru_cache(None)
def sig(p):return dsl.signature(p)
IDENTITY=sig(())
def load():return json.loads((ROOT/'data/families.json').read_text())
def cost(p,lib):
 p=tuple(p);d=[0]+[999]*len(p)
 for i in range(len(p)):
  d[i+1]=min(d[i+1],d[i]+1)
  for c in lib:
   op=CANDIDATES[c];n=len(op)
   if p[i:i+n]==op:d[i+n]=min(d[i+n],d[i]+1)
 return d[-1]
def utility(programs,lib):
 raw=sum(map(len,programs));encoded=sum(cost(p,lib) for p in programs)+sum(len(CANDIDATES[c])+1 for c in lib)
 return (raw-encoded)/raw

def select(programs,proposals):
 available=sorted(set(proposals));chosen=[];seen={IDENTITY}
 for _ in range(3):
  old=utility(programs,chosen);best=None
  for c in available:
   if sig(CANDIDATES[c]) in seen:continue
   value=utility(programs,chosen+[c])
   if value>old:old=value;best=c
  if best is None:break
  chosen.append(best);seen.add(sig(CANDIDATES[best]))
 return sorted(chosen)
def proposal_prompt(f,style='instruction'):
 history='\n'.join(','.join(p) for p in f['support'])
 if style=='instruction':return 'Choose one reusable subprogram of exactly two or three operations from rev,rot,inc,neg,swap,ends. It should compress the following successful programs by replacing repeated contiguous operations. Return only comma-separated operations.\nPrograms:\n'+history+'\nReusable program:\n'
 if style=='concise':return 'Find a frequent contiguous 2- or 3-operation fragment. Allowed operations: rev,rot,inc,neg,swap,ends.\n'+history+'\nFragment:\n'
 if style=='fewshot':
  demos='Programs:\nrot,inc,swap\nrev,rot,inc\nrot,inc,ends\nReusable program:\nrot,inc\n\nPrograms:\nneg,swap,rev\ninc,neg,swap\nneg,swap,ends\nReusable program:\nneg,swap\n\n'
  return 'Extract a reusable contiguous fragment of two or three operations, as in these examples.\n'+demos+'Programs:\n'+history+'\nReusable program:\n'
 raise ValueError(style)
def model_path(name):return PARENT/'model' if name=='qwen1.5b' else ROOT/'models'/name

def build():
 rng=random.Random(9262401);old={sig(tuple(x['ops'])) for x in json.loads((PARENT/'data/library.json').read_text())['selected']}
 pool=list(range(252));rng.shuffle(pool);used=set(old)|{IDENTITY};families=[]
 for f in range(32):
  motifs=[]
  for c in pool:
   if sig(CANDIDATES[c]) not in used:motifs.append(c);used.add(sig(CANDIDATES[c]))
   if len(motifs)==3:break
  assert len(motifs)==3,(f,len(used))
  support=[];test=[];asts=set();ss=set()
  for attempt in range(100000):
   p=[]
   for _ in range(rng.choice([3,4,5])):p.extend(CANDIDATES[rng.choice(motifs)] if rng.random()<.8 else [rng.choice(OPS)])
   p=tuple(p)
   if p in asts:continue
   if len(support)<12:support.append(p);ss.add(sig(p));asts.add(p)
   elif sig(p) not in ss:test.append(p);asts.add(p)
   if len(test)==64:break
  assert len(test)==64
  families.append(dict(id=f,split='train' if f<12 else 'dev' if f<16 else 'test',motifs=motifs,support=support,test=test))
 (ROOT/'data/families.json').write_text(json.dumps(families,indent=2))
 (ROOT/'data/candidates.json').write_text(json.dumps(CANDIDATES))
 print('Built',len(families),'families, independent latent semantics',len(used)-len(old)-1)
if __name__=='__main__':build()
