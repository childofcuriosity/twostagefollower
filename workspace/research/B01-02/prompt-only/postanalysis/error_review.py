"""Post-run analysis-label correction only. Frozen scores and inference remain untouched."""
import collections,itertools,json,re,sys
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];R=BASE/'fallback14';sys.path.insert(0,str(R/'src'))
from common import *
from score import OP,HEADER,ANSWER,grade
# Recognition is deliberately conservative: ambiguous operation alignments stay tool_or_order.
def classify(row):
 lines=[s for s in row['raw'].splitlines() if s.strip() and not HEADER.fullmatch(s)]
 truth=[s for s in target(row,row['condition']).splitlines() if not HEADER.fullmatch(s)]
 emitted=[s.split()[0] for s in lines if OP.fullmatch(s)];desired=[LIB[t] for t in row['chain']]
 flat=list(itertools.chain.from_iterable(desired));bounds=[0]
 for ops in desired:bounds.append(bounds[-1]+len(ops))
 # Whole-call deletion whose entire surviving operation sequence is exact.
 deletion=next((bounds[a] for a in range(len(desired)) for b in range(a+1,len(desired)+1) if emitted==list(itertools.chain.from_iterable(desired[:a]+desired[b:]))),None)
 segments=[];current=[]
 for s in row['raw'].splitlines():
  if HEADER.fullmatch(s):
   if current:segments.append(current);current=[]
  elif OP.fullmatch(s):current.append(s.split()[0])
 if current:segments.append(current)
 # Ignore empty titles such as Trace:. A whole inserted call requires an extra complete known tool segment.
 insertion=None
 if len(segments)>len(desired):
  for j in range(len(segments)):
   if segments[j] in LIB and segments[:j]+segments[j+1:]==desired:
    insertion=sum(len(x) for x in segments[:j]);break
 op_index=0;answer_count=sum(bool(ANSWER.fullmatch(s)) for s in lines)
 for i in range(max(len(lines),len(truth))):
  if i>=len(lines):return ('omitted_call' if op_index in bounds[:-1] else 'tool_or_order') if i<len(truth)-1 else 'format',i,len(segments)
  s=lines[i]
  if i>=len(truth):return 'format' if not OP.fullmatch(s) else ('extra_call' if insertion is not None else 'tool_or_order'),i,len(segments)
  t=truth[i]
  if s!=t:
   sm=OP.fullmatch(s);tm=OP.fullmatch(t)
   if not sm and not ANSWER.fullmatch(s):kind='format'
   elif ANSWER.fullmatch(s) and (answer_count!=1 or any(OP.fullmatch(x) for x in lines[i+1:])):kind='format'
   elif deletion is not None and deletion<=op_index:kind='omitted_call'
   elif insertion is not None and insertion<=op_index:kind='extra_call'
   elif ANSWER.fullmatch(s) and tm:kind='omitted_call' if emitted==flat[:len(emitted)] and len(emitted) in bounds[:-1] else 'tool_or_order'
   elif sm and tm:kind='tool_or_order' if sm.group(1)!=tm.group(1) else 'numeric'
   elif sm:kind='tool_or_order'
   else:kind='numeric'
   return kind,i,len(segments)
  if OP.fullmatch(s):op_index+=1
 return 'none',None,len(segments)
allrows=[];summaries={};groups={}
for c in CONDITIONS:
 rows=readrows(R/f'runs/formal-L2-{c}/predictions.jsonl');gg=[]
 for row in rows:
  old=grade(row);kind,index,segments=classify(row)
  assert (kind=='none')==bool(old['strict']),row['id']
  gg.append(dict(id=row['id'],condition=c,strict=old['strict'],first_error=kind,first_error_line=index,nonempty_operation_segments=segments,original_first_error=old['first_error'],changed=kind!=old['first_error']))
 groups[c]=gg;allrows+=gg;summaries[c]=dict(first_errors=dict(collections.Counter(x['first_error'] for x in gg)),changed_labels=sum(x['changed'] for x in gg),nonempty_segments=dict(collections.Counter(x['nonempty_operation_segments'] for x in gg)))
paired={}
for c in CONDITIONS[1:]:
 paired[c]=dict(recovered_by_STEP_error=dict(collections.Counter(s['first_error'] for s,v in zip(groups['STEP'],groups[c]) if not s['strict'] and v['strict'])),lost_by_condition_error=dict(collections.Counter(v['first_error'] for s,v in zip(groups['STEP'],groups[c]) if s['strict'] and not v['strict'])))
saverows(BASE/'analysis/graded-formal-errors-reviewed.jsonl',allrows)
write(BASE/'analysis/formal-errors-reviewed.json',dict(reason='Correct initial auxiliary label conflation: extra primitive != extra tool call; early intermediate Answer followed by further operations is format; empty Trace: is not a call.',strict_scores_unchanged=True,counts=summaries,paired=paired,code_sha256=sha(Path(__file__))))
print(json.dumps(dict(counts=summaries,paired=paired),indent=2))
