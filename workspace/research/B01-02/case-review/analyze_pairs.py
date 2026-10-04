from pathlib import Path
import json,re,sys,collections,random,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'));import dsl
world=json.loads((ROOT/'data/worlds.json').read_text());lib=world['original']['library'];names=world['original']['names']

def audit(row,ops):
 raw=row['raw']; state=tuple(row['x']); emitted=[]; errors=[]; extra=[];answers=[];headers=[]
 for line in raw.splitlines():
  m=re.fullmatch(r'(rev|rot|inc|neg|swap|ends) ([0-9]) ([0-9]) ([0-9]) ([0-9])',line)
  if m:
   op=m[1];actual=tuple(map(int,m.groups()[1:]));expected=dsl.step(state,op)
   if actual!=expected:errors.append({'step':len(emitted)+1,'expected':expected,'actual':actual})
   emitted.append(op);state=actual
  elif re.fullmatch(r'Answer: ([0-9]) ([0-9]) ([0-9]) ([0-9])',line):answers.append(list(map(int,line.split(':')[1].split())))
  elif re.fullmatch(r'[a-z]+:',line):headers.append(line[:-1])
  elif line.strip():extra.append(line)
 truth=list(dsl.execute(row['x'],ops));assert truth==row['expected']
 pred=answers[-1] if answers else None
 assert pred==row['prediction'] and (pred==truth)==row['correct'],row['id']
 prefix=emitted==ops[:len(emitted)] and len(emitted)<len(ops)
 bounds=[];n=0
 for i in row['chain']:n+=len(lib[i]);bounds.append(n)
 completed=bounds.index(len(emitted))+1 if prefix and len(emitted) in bounds else None
 clean=not errors and len(answers)==1 and not extra and pred==list(state)
 if clean and prefix and completed==2:category='correct_first_two_then_answer'
 elif clean and prefix and completed is not None:category='correct_other_tool_prefix_then_answer'
 elif clean and prefix:category='correct_prefix_stop_inside_tool'
 elif emitted==ops and clean:category='fully_correct_trace'
 elif emitted==ops and errors:category='correct_ops_arithmetic_error'
 elif not answers or extra or len(answers)!=1:category='format_or_missing_answer'
 elif errors:category='wrong_ops_and_arithmetic_error'
 elif pred!=list(state):category='answer_disagrees_with_last_state'
 else:category='wrong_operation_sequence'
 mismatch=next((j+1 for j,(a,b) in enumerate(zip(ops,emitted)) if a!=b),None)
 if mismatch is None and len(ops)!=len(emitted):mismatch=min(len(ops),len(emitted))+1
 return dict(category=category,correct=pred==truth,expected_ops=ops,emitted_ops=emitted,arithmetic_errors=errors,first_operation_mismatch=mismatch,completed_tools_if_prefix=completed,headers=headers,extra_lines=extra,answer_count=len(answers),answer_matches_last_state=pred==list(state),generated_tokens=row['generated_tokens'],at_generation_limit=row['generated_tokens']>=256)

allcases=[];sources={};counts=[]
for model,root in [('qwen1.5b',ROOT),('qwen3b',ROOT/'rsi-study/replications/qwen3b'),('smol1.7b',ROOT/'rsi-study/replications/smol1.7b')]:
 for seed in [11,22,33]:
  data={}
  for c in ['macro','flat']:
   p=root/f'runs/{c}-original-s{seed}/predictions.jsonl';sources[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest();data[c]={r['id']:r for r in map(json.loads,p.read_text().splitlines())}
  assert len(data['macro'])==len(data['flat'])==560
  for i,m in sorted(data['macro'].items()):
   f=data['flat'][i];assert (m['x'],m['chain'],m['split'])==(f['x'],f['chain'],f['split'])
   if not (m['correct'] and not f['correct']):continue
   ops=list(dsl.expand(m['chain'],lib));ma=audit(m,ops);fa=audit(f,ops)
   allcases.append(dict(model=model,seed=seed,id=i,split=m['split'],input=dsl.prompt(m,names),tools=[dict(name=names[j],ops=lib[j]) for j in m['chain']],expected_answer=m['expected'],macro_raw=m['raw'],flat_raw=f['raw'],macro_audit=ma,flat_audit=fa))
(OUT/'all-discordant-pairs.jsonl').write_text(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in allcases))
summary=dict(total=len(allcases),unique_test_ids=len({c['id'] for c in allcases}),categories=dict(collections.Counter(c['flat_audit']['category'] for c in allcases)),macro_categories=dict(collections.Counter(c['macro_audit']['category'] for c in allcases)),at_generation_limit=sum(c['flat_audit']['at_generation_limit'] for c in allcases),by_model={},source_sha256=sources)
for model in ['qwen1.5b','qwen3b','smol1.7b']:
 summary['by_model'][model]={}
 for split in ['ood','pressure']:
  rs=[c for c in allcases if c['model']==model and c['split']==split]
  summary['by_model'][model][split]=dict(n=len(rs),categories=dict(collections.Counter(c['flat_audit']['category'] for c in rs)))
(OUT/'attribution-summary.json').write_text(json.dumps(summary,indent=2))
# Read samples from each model x seed; include all exceptions if few, otherwise seeded category samples.
rng=random.Random(20260925);chosen=[]
for model in summary['by_model']:
 for seed in [11,22,33]:
  rs=[c for c in allcases if c['model']==model and c['seed']==seed];chosen.extend(rng.sample(rs,min(3,len(rs))))
exceptions=[c for c in allcases if c['flat_audit']['category']!='correct_first_two_then_answer' or c['macro_audit']['category']!='fully_correct_trace']
for cat in sorted({c['flat_audit']['category'] for c in exceptions}):
 rs=[c for c in exceptions if c['flat_audit']['category']==cat];chosen.extend(rs if len(rs)<=15 else rng.sample(rs,15))
chosen=list({(c['model'],c['seed'],c['id']):c for c in chosen}.values())
(OUT/'manual-review-sample.jsonl').write_text(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in chosen))
print(json.dumps({k:v for k,v in summary.items() if k!='source_sha256'},indent=2));print('Manual sample',len(chosen),'exception records',len(exceptions))
