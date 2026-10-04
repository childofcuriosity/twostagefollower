"""Declared post-hoc robustness analysis; preserve primary protocol and results."""
from common import *
from collections import deque
import statistics
rows=[json.loads(l) for l in (ROOT/'analysis/rows.jsonl').read_text().splitlines()];tasks=load()
def select_lexical(programs,proposals):
 # Consider all spellings before semantic exclusion; selected library still
 # has at most one representative of each semantic function.
 available=sorted(set(proposals));chosen=[];seen={IDENTITY}
 for _ in range(3):
  old=utility(programs,chosen)['net_saving'];best=None
  for c in available:
   if sig(CANDIDATES[c]) in seen:continue
   score=utility(programs,chosen+[c])['net_saving']
   if score>old:best=c;old=score
  if best is None:break
  chosen.append(best);seen.add(sig(CANDIDATES[best]))
 return sorted(chosen)
@lru_cache(maxsize=100000)
def transition(state,ops):return tuple(execute(x,ops) for x in state)
@lru_cache(None)
def reach(library,primitive_budget):
 actions=[(o,) for o in OPS]+[CANDIDATES[c] for c in library];queue=deque([IDENTITY]);found={IDENTITY};count=0;primitive=0
 while queue:
  state=queue.popleft()
  for ops in actions:
   if (primitive+len(ops)>3000 if primitive_budget else count>=3000):return found,count,primitive
   nxt=transition(state,ops);count+=1;primitive+=len(ops)
   if nxt not in found:found.add(nxt);queue.append(nxt)
 return found,count,primitive
records=[]
for r in rows:
 f=tasks[r['family']]
 for selector in ['registered','lexical-first']:
  lib=r['selected'] if selector=='registered' else select_lexical(f['support'],r['proposals'])
  comp=utility(f['test'],lib)['fraction']
  for primitive in [False,True]:
   found,count,ops=reach(tuple(lib),primitive)
   rate=sum(sig(tuple(p)) in found for p in f['test'])/len(f['test'])
   if selector=='registered' and not primitive:assert rate==r['search']['fraction']
   records.append(dict(method=r['method'],seed=r['seed'],family=r['family'],selector=selector,budget_unit='primitive' if primitive else 'action',selected=lib,compression=comp,search_rate=rate,expansions=count,primitive_operations=ops))
summary={}
for selector in ['registered','lexical-first']:
 for unit in ['action','primitive']:
  key=selector+'/'+unit;summary[key]={}
  for method in sorted({r['method'] for r in rows}):
   chosen=[r for r in records if r['selector']==selector and r['budget_unit']==unit and r['method']==method]
   summary[key][method]={'compression':statistics.mean(r['compression'] for r in chosen),'search_rate':statistics.mean(r['search_rate'] for r in chosen)}
(ROOT/'analysis/sensitivity-rows.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in records))
(ROOT/'analysis/sensitivity.json').write_text(json.dumps({'posthoc':True,'reason':'Original pre-deduplication retains first syntax for each semantic class although compression is lexical; macro actions have variable primitive costs. Check both choices without altering primary results.','results':summary},indent=2));print(json.dumps(summary,indent=2))
