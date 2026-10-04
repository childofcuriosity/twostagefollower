import collections,time
import numpy as np
from common import *
start=time.time();tasks=load();rows=[];old={sig(tuple(r['ops'])) for r in json.loads((PARENT/'data/library.json').read_text())['selected']}
@lru_cache(maxsize=100000)
def transition(state,ops):return tuple(execute(x,ops) for x in state)
search_cache={}
def search(library,targets,budget=3000):
 key=tuple(library)
 if key not in search_cache:
  actions=[(o,) for o in OPS]+[CANDIDATES[c] for c in library]
  found={IDENTITY:(0,0)};queue=collections.deque([IDENTITY]);count=0;primitive=0
  while queue and count<budget:
   state=queue.popleft()
   for ops in actions:
    if count==budget:break
    nxt=transition(state,ops);count+=1;primitive+=len(ops)
    if nxt not in found:found[nxt]=(count,primitive);queue.append(nxt)
  search_cache[key]=(found,count,primitive)
 found,count,primitive=search_cache[key]
 steps=[found.get(sig(tuple(p))) for p in targets]
 return {'budget':budget,'expansions':count,'primitive_operations':primitive,'solved':sum(s is not None for s in steps),'n':len(steps),'fraction':sum(s is not None for s in steps)/len(steps),'first_discovery_costs':steps,'unique_target_functions':len({sig(tuple(p)) for p in targets})}
for method in ['base','flat','macro','mismatch','random','frequency','exhaustive','no-library']:
 for seed in [11,22,33]:
  generated=[]
  if method in ['base','flat','macro','mismatch']:
   path=ROOT/f'runs/{method}-s{seed}';summary=json.loads((path/'summary.json').read_text());generated=[json.loads(l) for l in (path/'proposals.jsonl').read_text().splitlines()]
   assert len(generated)==128
  for f in tasks:
   if generated:proposals=[r['candidate'] for r in generated if r['family']==f['id']]
   elif method=='random':proposals=random.Random(seed*1000+f['id']).choices(range(len(CANDIDATES)),k=16)
   elif method=='frequency':
    counts=collections.Counter(tuple(p[i:i+n]) for p in f['support'] for n in (2,3) for i in range(len(p)-n+1))
    proposals=sorted(range(len(CANDIDATES)),key=lambda c:(-counts[CANDIDATES[c]]*(len(CANDIDATES[c])-1),c))[:16]
   elif method=='exhaustive':proposals=list(range(len(CANDIDATES)))
   else:proposals=[]
   selected=select(f['support'],proposals)
   row={'method':method,'seed':seed,'family':f['id'],'proposals':proposals,'unique_proposed_semantics':len({sig(CANDIDATES[c]) for c in proposals}),'identity_proposals':sum(sig(CANDIDATES[c])==IDENTITY for c in proposals),'old_library_proposals':sum(sig(CANDIDATES[c]) in old for c in proposals),'selected':selected,'selected_ops':[CANDIDATES[c] for c in selected],'support':utility(f['support'],selected),'test':utility(f['test'],selected),'search':search(selected,f['test'])}
   rows.append(row)
(ROOT/'analysis/rows.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
summary={}
for method in sorted({r['method'] for r in rows}):
 rs=[r for r in rows if r['method']==method]
 summary[method]={'test_compression':np.mean([r['test']['fraction'] for r in rs]),'search_solved_fraction':np.mean([r['search']['fraction'] for r in rs]),'mean_selected_size':np.mean([len(r['selected']) for r in rs]),'mean_unique_proposed_semantics':np.mean([r['unique_proposed_semantics'] for r in rs]),'identity_proposals':sum(r['identity_proposals'] for r in rs),'old_library_proposals':sum(r['old_library_proposals'] for r in rs),'mean_primitive_operations':np.mean([r['search']['primitive_operations'] for r in rs])}
comparisons={};rng=np.random.default_rng(7431);indices=rng.integers(0,8,(5000,8))
for other in ['flat','base','random','mismatch','frequency']:
 values=[];searchdiff=[]
 for seed in [11,22,33]:
  def vals(method,field,key):return np.array([next(r[field][key] for r in rows if r['method']==method and r['seed']==seed and r['family']==f) for f in range(8)])
  values.append(vals('macro','test','fraction')-vals(other,'test','fraction'))
  searchdiff.append(vals('macro','search','fraction')-vals(other,'search','fraction'))
 values=np.array(values);cluster=values.mean(axis=0);boot=cluster[indices].mean(axis=1)
 comparisons['macro-vs-'+other]={'mean_compression_difference':float(values.mean()),'seed_compression_differences':values.mean(axis=1).tolist(),'family_compression_differences':cluster.tolist(),'family_cluster_bootstrap_95':np.quantile(boot,[.025,.975]).tolist(),'mean_search_difference':float(np.mean(searchdiff))}
c=comparisons['macro-vs-random'];passed=c['mean_compression_difference']>=.02 and min(c['seed_compression_differences'])>0 and c['mean_search_difference']>=-.02
out={'methods':summary,'comparisons':comparisons,'prespecified_screen_passed':passed,'seconds':time.time()-start,'interpretation':'Compression is symbolic reuse; search is external BFS, not neural solving. Existing execution-trained checkpoints, not proposal-policy training. Base seeds are sampling repeats.'}
(ROOT/'analysis/results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
