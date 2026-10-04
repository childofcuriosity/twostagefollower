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
lines=['# 评分边界案例与补充错误归类','','严格评分同时要求正确操作、全部状态和最终Answer；标题是独立合规指标。下表只解释已保存的原始输出，不改变评分。','','| 条件/seed | 严格失败 | 数字步骤 | 操作序列 | 仅最终Answer | 额外Trace标题（主分不扣） |','|---|---:|---:|---:|---:|---:|']
for x in records:
 e=x['exclusive_reason_priority'];h=x['titles']
 lines.append(f'| {x["condition"]}/{x["seed"]} | {x["strict_failures"]} | {e.get("numeric_step",0)} | {e.get("operation_sequence",0)} | {e.get("final_Answer_only",0)} | {h.get("extra_Trace_heading_only",0)} |')
lines+=['','NAME seed302的49条、seed303的4条标题不合规，全部由额外`Trace:`造成；删除这一额外标题后，工具身份和顺序均符合要求。原评分器允许一般标题行，因此这里不会算作未知额外行或扣二值奖励。不能把90.43%的全标题合规率解释为只有90.43%的工具名称正确。','']
for x in cases:
 lines.extend([f'## {x["condition"]} seed{x["seed"]}，{x["id"]}',f'严格轨迹={x["grading"]["strict"]}；标题全合规={x["grading"]["header_compliant"]}。输入{x["input"]}，工具索引{x["chain"]}。','','实际输出：','```text',x['raw'],'```','','标准输出：','```text',x['expected'],'```',''])
(R/'CASE_REVIEW.md').write_text('\n'.join(lines)+'\n')
with (R/'REPORT.md').open('a') as f:f.write('\n标题与最终Answer的补充核验见[CASE_REVIEW.md](CASE_REVIEW.md)：NAME端点53条全标题不合规均为额外`Trace:`，工具名及顺序本身正确；STEP seed301另有1条中间轨迹全对而最终Answer抄错。主评分未改。\n')
print('Supplemental endpoint classification and cases written.')
