from common import *
import argparse,collections,importlib.util,time
import numpy as np
spec=importlib.util.spec_from_file_location('legacy',B/'scale-study/src/audit.py');legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
HEADER=re.compile(r'^[A-Za-z][A-Za-z0-9]*:$')
OP=re.compile(r'^(rev|rot|inc|neg|swap|ends) ([0-9]) ([0-9]) ([0-9]) ([0-9])$')
ANSWER=re.compile(r'^Answer: [0-9] [0-9] [0-9] [0-9]$')
def grade(row):
 raw=row['raw'];c=row['condition'];lines=raw.splitlines()
 normalized='\n'.join('step:' if HEADER.fullmatch(s) else s for s in lines)
 pred=dsl.answer(raw)
 oldrow=dict(row,raw=normalized,prediction=list(pred) if pred is not None else None,correct=pred is not None and list(pred)==row['expected'])
 g=legacy.check(oldrow)
 actual=[s for s in lines if s.strip() and not HEADER.fullmatch(s)]
 truth=[s for s in target(row,c).splitlines() if not HEADER.fullmatch(s)]
 canonical=actual==truth
 strict=([s for s in actual if OP.fullmatch(s)]==[s for s in truth if OP.fullmatch(s)] and [s for s in actual if ANSWER.fullmatch(s)]==[truth[-1]] and all(OP.fullmatch(s) or ANSWER.fullmatch(s) for s in actual))
 assert strict==bool(g['strict_trace']),(row['id'],actual,truth,g)
 headings=[s[:-1] for s in lines if HEADER.fullmatch(s)]
 need=labels(row,c)
 segments=[];current=None;format_lines=[]
 for i,s in enumerate(lines):
  if not s.strip():continue
  if HEADER.fullmatch(s):
   current=[];segments.append(current)
  elif OP.fullmatch(s):
   if current is not None:current.append(s.split()[0])
  elif not ANSWER.fullmatch(s):format_lines.append(i)
 emitted=[s.split()[0] for s in actual if OP.fullmatch(s)]
 expected=list(dsl.expand(row['chain'],LIB))
 first=None;first_index=None
 # First observed divergence ignoring headings (heading compliance is separate).
 for i in range(max(len(actual),len(truth))):
  if i>=len(actual):first='omitted_call';first_index=i;break
  if i>=len(truth):first='extra_call' if OP.fullmatch(actual[i]) else 'format';first_index=i;break
  if actual[i]==truth[i]:continue
  first_index=i;s=actual[i];t=truth[i];sm=OP.fullmatch(s);tm=OP.fullmatch(t)
  if not sm and not ANSWER.fullmatch(s):first='format'
  elif ANSWER.fullmatch(s) and tm:first='omitted_call'
  elif sm and ANSWER.fullmatch(t):first='extra_call'
  elif sm and tm:
   if sm.group(1)!=tm.group(1):
    # A pure whole-call deletion/insertion at this divergence is observable from segment sequences.
    desired=[LIB[x] for x in row['chain']]
    deletion=any(segments==desired[:j]+desired[j+1:] for j in range(len(desired)))
    insertion=any(segments[:j]+segments[j+1:]==desired for j in range(len(segments)))
    first='omitted_call' if deletion else 'extra_call' if insertion else 'tool_or_order'
   else:first='numeric'
  else:first='numeric' # Correct-format Answer with incorrect digits.
  break
 return dict(id=row['id'],condition=c,length=row['depth'],strict=int(strict),canonical_order=int(canonical),header_compliant=int(headings==need),matched_headers=sum(x==y for x,y in zip(headings,need)),required_headers=len(need),emitted_headers=len(headings),first_error=first or 'none',first_error_trace_line=first_index,under_calls=len(headings)<len(need),over_calls=len(headings)>len(need),operation_mismatch=emitted!=expected,numeric_step_error=g['numeric_step_error'],format_error=bool(format_lines) or bool(g['missing_or_multiple_answer']),finish_reason=row['finish_reason'],generated_tokens=row['generated_tokens'],text_tokens=row['text_tokens'],input_tokens=row['input_tokens'],allocated_generate_seconds=row['allocated_generate_seconds'],legacy=g)
def main():
 p=argparse.ArgumentParser();p.add_argument('--phase',required=True);p.add_argument('--lengths',nargs='+',type=int,required=True);p.add_argument('--conditions',nargs='+',default=list(CONDITIONS));a=p.parse_args()
 for L in a.lengths:
  allrows=[];groups={};summaries={}
  for c in a.conditions:
   run=R/f'runs/{a.phase}-L{L}-{c}';assert (run/'complete.json').exists()
   rr=readrows(run/'predictions.jsonl');expected=readrows(R/f'data/{a.phase}-L{L}.jsonl');assert [x['id'] for x in rr]==[x['id'] for x in expected]
   gg=[grade(x) for x in rr];groups[c]=gg;allrows+=gg
   summaries[c]=dict(n=len(gg),correct=sum(x['strict'] for x in gg),rate=np.mean([x['strict'] for x in gg]),header_compliance=np.mean([x['header_compliant'] for x in gg]),first_errors=dict(collections.Counter(x['first_error'] for x in gg)),finish_reasons=dict(collections.Counter(x['finish_reason'] for x in gg)),mean_output_tokens=np.mean([x['generated_tokens'] for x in gg]),mean_text_tokens=np.mean([x['text_tokens'] for x in gg]),mean_input_tokens=np.mean([x['input_tokens'] for x in gg]),generate_seconds=sum(x['allocated_generate_seconds'] for x in gg),run=json.loads((run/'complete.json').read_text()))
  paired={}
  for c in a.conditions:
   if c=='STEP':continue
   d=np.array([x['strict']-y['strict'] for x,y in zip(groups[c],groups['STEP'])]);rng=np.random.default_rng(740001)
   boot=np.mean(d[rng.integers(0,len(d),(10000,len(d)))],axis=1)
   paired[c]=dict(difference=float(d.mean()),ci95=np.quantile(boot,[.025,.975]).tolist(),better=int((d>0).sum()),worse=int((d<0).sum()),both_correct=sum(x['strict'] and y['strict'] for x,y in zip(groups[c],groups['STEP'])),method='10000 paired item percentile bootstrap; fixed analysis seed 740001')
  saverows(R/f'analysis/graded-{a.phase}-L{L}.jsonl',allrows)
  write(R/f'analysis/scores-{a.phase}-L{L}.json',dict(phase=a.phase,length=L,results=summaries,paired_vs_STEP=paired,legacy_sha256=sha(B/'scale-study/src/audit.py')))
  print(json.dumps(dict(phase=a.phase,length=L,rates={c:summaries[c]['rate'] for c in a.conditions},paired=paired)),flush=True)
if __name__=='__main__':main()
