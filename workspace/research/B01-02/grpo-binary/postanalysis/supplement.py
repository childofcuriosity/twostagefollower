import sys,json,collections,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'src'))
from common import HEADER,prior,target,write
records=[];cases=[]
for c in ['STEP','NAME']:
 for seed in [301,302,303]:
  rows=[json.loads(line) for p in (R/'eval/outputs').glob(f'{c}-s{seed}-step100-test-part*/predictions.jsonl') for line in p.read_text().splitlines()]
  assert len(rows)==512
  reasons=collections.Counter();title=collections.Counter()
  for row in rows:
   g=row['grading'];h=[s[:-1] for s in row['raw'].splitlines() if HEADER.fullmatch(s)];expected=prior.labels(row,c)
   if h==expected:title['fully_compliant']+=1
   elif [s for s in h if s!='Trace']==expected:title['extra_Trace_heading_only']+=1
   else:title['other_title_noncompliance']+=1
   if not g['strict']:
    z=g['legacy']
    if z['missing_or_multiple_answer']:reason='missing_or_multiple_Answer'
    elif g['extra_output']:reason='unrecognized_extra_lines'
    elif g['operation_mismatch']:reason='operation_sequence'
    elif g['numeric_error']:reason='numeric_step'
    elif not z['accuracy']:reason='final_Answer_only'
    else:raise AssertionError(row['id'])
    reasons[reason]+=1
   if (c,seed,row['id']) in [('STEP',301,'test-00474'),('NAME',302,'test-00039')]:
    cases.append(dict(condition=c,seed=seed,id=row['id'],input=row['x'],chain=row['chain'],raw=row['raw'],expected=target(row,c),grading=g))
  records.append(dict(condition=c,seed=seed,strict_failures=sum(reasons.values()),exclusive_reason_priority=dict(reasons),titles=dict(title)))
write(R/'analysis/endpoint-error-supplement.json',dict(records=records,cases=cases,note='Descriptive exclusive reason priority: answer count, extra unrecognized lines, operation sequence, numeric step, final Answer. Original primary scores unchanged.'))
lines=['# Scoring boundary cases and supplementary error categories','','Strict scoring requires correct operations, all states, and the final Answer. Headings are an independent compliance metric. The table below interprets saved raw outputs without changing scores.','','| Condition/seed | Strict failures | Numerical steps | Operation sequence | Final Answer only | Extra Trace heading (no primary-score penalty) |','|---|---:|---:|---:|---:|---:|']
for x in records:
 e=x['exclusive_reason_priority'];h=x['titles']
 lines.append(f'| {x["condition"]}/{x["seed"]} | {x["strict_failures"]} | {e.get("numeric_step",0)} | {e.get("operation_sequence",0)} | {e.get("final_Answer_only",0)} | {h.get("extra_Trace_heading_only",0)} |')
lines+=['','All 49 heading-noncompliant outputs for NAME seed302 and 4 for seed303 result from an extra `Trace:` heading. Removing that heading leaves compliant tool identities and order. The original scorer permits generic heading lines, so these are not unknown extra lines and incur no binary-reward penalty. A fully compliant heading rate of 90.43% must not be interpreted as only 90.43% correct tool names.','']
for x in cases:
 lines.extend([f'## {x["condition"]} seed{x["seed"]}，{x["id"]}',f'Strict trajectory={x["grading"]["strict"]}; full heading compliance={x["grading"]["header_compliant"]}. Input {x["input"]}, tool indices {x["chain"]}。','','Actual output:','```text',x['raw'],'```','','Reference output:','```text',x['expected'],'```',''])
(R/'CASE_REVIEW.md').write_text('\n'.join(lines)+'\n')
with (R/'REPORT.md').open('a') as f:f.write('\nSee [CASE_REVIEW.md](CASE_REVIEW.md) for supplementary heading and final-Answer checks: all 53 NAME endpoint heading violations are extra `Trace:` headings, with correct tool names and order. STEP seed301 also has 1 case with entirely correct intermediate states but an incorrectly copied final Answer. The primary score is unchanged.\n')
print('Supplemental endpoint classification and cases written.')
