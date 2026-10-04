"""Descriptive paired attribution of existing outputs; no new inference/training."""
import json,sys,re,collections,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit import check,dsl,lib
R=Path(__file__).resolve().parents[1]
def category(row,a):
 if a['strict_trace']:return 'complete_correct'
 if a['correct_prefix_early_answer']:return 'correct_prefix_then_answer'
 if a['wrong_operation']:return 'operation_sequence_error'
 if a['numeric_step_error']:return 'numeric_error_without_operation_mismatch'
 if a['budget_hit']:return 'budget_hit_other'
 return 'other'
out={'scope':'Original 384 OOD tasks x seeds11,22,33. Answer accuracy pairs; descriptive categories prioritized prefix > operation mismatch > arithmetic, not causal mechanisms.','sources':{},'seeds':[],'examples':[]}
total=collections.Counter();cats=collections.defaultdict(collections.Counter);trans=collections.Counter();stoppos=collections.defaultdict(collections.Counter)
for seed in [11,22,33]:
 rows={}
 for c in ['flat','macro']:
  p=R/f'qwen32b/runs/{c}-original-s{seed}/predictions.jsonl';out['sources'][str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
  rows[c]={r['id']:r for r in map(json.loads,p.read_text().splitlines()) if r['split']=='ood'}
 assert rows['flat'].keys()==rows['macro'].keys()
 counts=collections.Counter()
 for id,f in rows['flat'].items():
  m=rows['macro'][id];assert (f['chain'],f['x'])==(m['chain'],m['x'])
  af,am=check(f),check(m);cf,cm=category(f,af),category(m,am)
  pair=('both_correct' if af['accuracy'] and am['accuracy'] else 'macro_only' if am['accuracy'] else 'flat_only' if af['accuracy'] else 'both_wrong')
  counts[pair]+=1;total[pair]+=1;cats[pair][cf+' -> '+cm]+=1;trans[cf+' -> '+cm]+=1
  for c,r,a in [('flat',f,af),('macro',m,am)]:
   if a['correct_prefix_early_answer']:
    n=a['emitted_ops'];bounds=[len(dsl.expand(r['chain'][:k],lib)) for k in range(1,len(r['chain'])+1)]
    k=bounds.index(n)+1 if n in bounds else 'inside_tool'
    stoppos[c][f"required{len(r['chain'])}_done{k}"]+=1
  if pair in ['macro_only','flat_only']:
   out['examples'].append({'seed':seed,'id':id,'pair':pair,'flat_category':cf,'macro_category':cm,'chain':f['chain'],'input':f['x'],'expected':f['expected'],'flat':f['raw'],'macro':m['raw'],'flat_audit':af,'macro_audit':am})
 out['seeds'].append({'seed':seed,'counts':dict(counts)})
out.update(totals=dict(total),paired_categories={k:dict(v) for k,v in cats.items()},all_transitions=dict(trans),prefix_stop_positions={k:dict(v) for k,v in stoppos.items()})
(R/'analysis/paired32-attribution.json').write_text(json.dumps(out,indent=2))
print(json.dumps({k:v for k,v in out.items() if k not in ['examples','sources']},indent=2))
for key in ['correct_prefix_then_answer','operation_sequence_error']:
 candidates=[x for x in out['examples'] if x['pair']=='macro_only' and x['flat_category']==key]
 if candidates:
  e=sorted(candidates,key=lambda x:(len(x['chain']),x['seed'],x['id']))[0]
  print('EXAMPLE',json.dumps(e,ensure_ascii=False))
