"""Offline factorization audit. No model inference, training, or checkpoint selection."""
import collections,hashlib,json,re,sys,math
from pathlib import Path
import numpy as np
from audit import check,dsl,lib
R=Path(__file__).resolve().parents[1]
NAMES=json.loads((R/'qwen32b/data/worlds.json').read_text())['original']['names']
nameidx={n:i for i,n in enumerate(NAMES)}
def fold(chain):return int(hashlib.sha256(json.dumps(chain).encode()).hexdigest()[:8],16)%5

def parse(row,condition):
 segments=[];unparsed=[];state=tuple(row['x']);answers=[]
 for line in row['raw'].splitlines():
  if not line.strip():continue
  h=re.fullmatch(r'([a-z]+):',line)
  op=re.fullmatch(r'(rev|rot|inc|neg|swap|ends) ([0-9]) ([0-9]) ([0-9]) ([0-9])',line)
  ans=re.fullmatch(r'Answer: ([0-9]) ([0-9]) ([0-9]) ([0-9])',line)
  if h:segments.append({'label':h[1],'ops':[],'numeric_ok':True,'start':state})
  elif op:
   end=tuple(map(int,op.groups()[1:]));ok=dsl.step(state,op[1])==end
   if segments:segments[-1]['ops'].append(op[1]);segments[-1]['numeric_ok'] &= ok
   else:unparsed.append(line)
   state=end
  elif ans:answers.append(tuple(map(int,ans.groups())))
  else:unparsed.append(line)
 for s in segments:
  tool=nameidx.get(s['label']);s['tool']=tool
  s['B_ops']=tool is not None and s['ops']==lib[tool]
  s['B']=s['B_ops'] and s['numeric_ok']
 slots=[]
 for i,tool in enumerate(row['chain']):
  s=segments[i] if i<len(segments) else None
  A=bool(s and s['tool']==tool)
  B=bool(s and s['B'])
  J=bool(s and s['ops']==lib[tool] and s['numeric_ok'])
  slots.append({'i':i,'tool':tool,'A':A,'B_observed':B if s and s['tool'] is not None else None,'J':A and B,'flat_local':J})
 a=check(row);L=len(row['chain'])
 names_ok=len(segments)==L and all(s['A'] for s in slots)
 structural=not unparsed and len(answers)==1 and answers[0]==state and len(segments)==L
 decomposed=names_ok and all(s['J'] for s in slots) and structural
 return dict(id=row['id'],chain=row['chain'],length=L,fold=fold(row['chain']),slots=slots,segments=segments,name_sequence_ok=names_ok,all_named_expansions_ok=bool(segments) and all(s['B'] for s in segments),decomposed_success=decomposed,structural_ok=structural,strict=a['strict_trace'],answer=a['accuracy'],condition=condition)

def rates(rs):
 d=collections.defaultdict(lambda:[0,0])
 def add(key,v):d[key][0]+=int(v);d[key][1]+=1
 for r in rs:
  for s in r['slots']:
   add(('A',),s['A']);add(('A_length',r['length']),s['A']);add(('A',r['length'],s['i']),s['A'])
   add(('J',r['length'],s['i']),s['J'])
  for s in r['segments']:
   if s['tool'] is not None:
    add(('B',),s['B']);add(('B_length',r['length']),s['B']);add(('B',s['tool']),s['B']);add(('B_ops',),s['B_ops'])
 return d

def prob(d,key,fallback=None):
 v=d.get(key)
 if not v or not v[1]:v=d.get(fallback)
 return v[0]/v[1] if v and v[1] else None

def main():
 sources={};groups=collections.defaultdict(list);flatgroups=collections.defaultdict(list)
 manifest=json.loads((R/'analysis/results.json').read_text())['source_sha256']
 items=[('main',Path(p),h) for p,h in manifest.items()]
 ext=json.loads((R/'analysis/extended-results.json').read_text())['manifest']
 items += [('independent',R/p,h) for p,h in ext.items() if '/frozen' not in p]
 for family,p,h in items:
  assert hashlib.sha256(p.read_bytes()).hexdigest()==h
  sources[str(p)]=h
  model=next((x for x in ['qwen32b','qwen7b','qwen3b'] if x in str(p)),'qwen1.5b')
  match=re.search(r'(flat|macro)(?:-original)?-s(11|22|33)',str(p));assert match,p
  c,seed=match[1],int(match[2])
  for row in map(json.loads,p.read_text().splitlines()):
   if family=='main' and row['split']!='ood':continue
   r=parse(row,c);r.update(family=family,model=model,seed=seed)
   (groups if c=='macro' else flatgroups)[family,model,seed].append(r)
 predictions=[];summary=[];unitcounts=collections.Counter()
 for key,rs in groups.items():
  family,model,seed=key;ds=rates(rs);flat={r['id']:r for r in flatgroups[key]};assert flat.keys()=={r['id'] for r in rs}
  for f in range(5):
   train=[r for r in rs if r['fold']!=f];d=rates(train)
   for r in [r for r in rs if r['fold']==f]:
    L=r['length'];pa,pb=prob(d,('A_length',L),('A',)),prob(d,('B_length',L),('B',))
    pos=[prob(d,('A',L,s['i']),('A',))*prob(d,('B',s['tool']),('B',)) for s in r['slots']]
    joint=[prob(d,('J',L,s['i'])) for s in r['slots']]
    assert all(v is not None for v in joint)
    predictions.append(dict(family=family,model=model,seed=seed,id=r['id'],chain=r['chain'],length=L,fold=f,pooled_product=(pa*pb)**L,position_tool_product=math.prod(pos),position_joint_product=math.prod(joint),actual=r['decomposed_success'],strict=r['strict'],answer=r['answer'],flat_strict=flat[r['id']]['strict'],flat_answer=flat[r['id']]['answer']))
  for L in sorted({r['length'] for r in rs}):
   sub=[r for r in rs if r['length']==L];d=rates(sub)
   summary.append(dict(family=family,model=model,seed=seed,length=L,n=len(sub),slot_A=prob(d,('A',)),observed_B=prob(d,('B',)),observed_B_ops=prob(d,('B_ops',)),name_sequence=sum(r['name_sequence_ok'] for r in sub)/len(sub),strict=sum(r['strict'] for r in sub)/len(sub),decomposed=sum(r['decomposed_success'] for r in sub)/len(sub),strict_minus_decomposed=sum(r['strict'] and not r['decomposed_success'] for r in sub)))
  for r in rs:
   assert not r['decomposed_success'] or r['strict'],r
   unitcounts['macro_trajectories']+=1;unitcounts['required_tool_slots']+=len(r['slots']);unitcounts['emitted_segments']+=len(r['segments'])
 rng=np.random.default_rng(20260925);aggregate=[]
 for family,model in sorted({(r['family'],r['model']) for r in predictions}):
  for L in [0]+sorted({r['length'] for r in predictions if r['family']==family and r['model']==model}):
   rs=[r for r in predictions if r['family']==family and r['model']==model and (not L or r['length']==L)]
   fields=['actual','strict','answer','flat_strict','flat_answer','pooled_product','position_tool_product','position_joint_product']
   row=dict(family=family,model=model,length=L,n=len(rs),**{k:float(np.mean([r[k] for r in rs])) for k in fields})
   # Bootstrap held-out residuals by program, averaging observed seeds. Estimator-fit uncertainty excluded.
   bychain=collections.defaultdict(list)
   for r in rs:bychain[tuple(r['chain'])].append(r['position_tool_product']-r['actual'])
   vals=np.array([sum(v) for v in bychain.values()]);weights=np.array([len(v) for v in bychain.values()]);ix=rng.integers(len(vals),size=(2000,len(vals)));boot=vals[ix].sum(axis=1)/weights[ix].sum(axis=1)
   row['prediction_minus_actual']=row['position_tool_product']-row['actual'];row['conditional_program_bootstrap95']=np.quantile(boot,[.025,.975]).tolist();row['programs']=len(vals)
   aggregate.append(row)
 out=dict(method='5-fold by exact input program chain, shared across seeds. Fit within each model/seed/dataset family. No inference. A: emitted label at required position correct; missing=0. B: expansion correct for actually emitted known label, with arithmetic relative to emitted incoming state; missing B unobservable, excluded, NOT treated as oracle. Pooled=(pA(length)*pB(length))^L, fit separately by length. Position/tool=product pA(length,position)*pB(tool). Joint=product p(A and B at position), diagnoses cross-position factorization only. Stop/segment count separately checked in actual decomposition success. Not evidence of counterfactual oracle ability. Bootstrap conditional on fitted out-of-fold predictions, excludes fit uncertainty.',counts=dict(unitcounts),sources=sources,per_seed_length=summary,aggregate=aggregate)
 (R/'analysis/subtask-factorization.json').write_text(json.dumps(out,indent=2))
 (R/'analysis/subtask-factorization-predictions.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in predictions))
 with (R/'analysis/subtask-factorization-segments.jsonl').open('w') as f:
  for rs in groups.values():
   for r in rs:f.write(json.dumps(r)+'\n')
 print(json.dumps(aggregate,indent=2))
if __name__=='__main__':main()
