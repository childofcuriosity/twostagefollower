"""Descriptive label/termination diagnostics, no new generation or condition selection."""
from common import *
import collections
from decimal import Decimal, ROUND_HALF_UP
rows=[json.loads(l) for l in (R/'analysis/graded.jsonl').read_text().splitlines()]
results=[]
for model in ROOTS:
 for condition in ['flat','macro','position','alias']:
  for seed in [11,22,33]:
   rs=[x for x in rows if (x['model'],x['condition'],x['seed'],x['dataset'])==(model,condition,seed,'independent')]
   c=collections.Counter();hist=collections.Counter()
   for x in rs:
    g=x['metrics'];labels=g['emitted_labels'];hist[len(labels)]+=1
    c['n']+=1;c['reaches_third_label']+=len(labels)>=3;c['exact_two_tools_correct_then_answer']+=g['exact_two_tools_early_answer'];c['strict_correct']+=g['strict_trace']
    if len(labels)>=3:c['third_label_expected']+=labels[2]==g['expected_labels'][2]
    if g['label_sequence_correct']:
     c['label_sequence_correct']+=1;c['strict_given_labels_correct_numerator']+=g['strict_trace']
   results.append(dict(model=model,condition=condition,seed=seed,counts=dict(c),emitted_label_count_histogram=dict(hist)))
write(R/'analysis/boundary-diagnostics.json',dict(results=results,note='Descriptive, conditioned-on-output rates not causal. All test tasks require at least three calls. STEP third-label identity is trivial and not comparable to identity binding. No new model inference.'))
lines=['# 第二次调用之后是否继续','按已登记的段数/提前结束指标补充描述；不是注意力机制或编号外推失败的独立因果证明。分母均为旧独立480题×3seed。','','|模型|条件|输出至少第三个段标签|正确完成两工具后提前Answer|完整轨迹|','|---|---|---:|---:|---:|']
for model in ROOTS:
 for condition in ['flat','macro','position','alias']:
  cc=collections.Counter()
  for x in results:
   if (x['model'],x['condition'])==(model,condition):cc.update(x['counts'])
  lines.append('|'+model+'|'+condition+'|'+'|'.join(str((Decimal(cc[k])*100/Decimal(cc["n"])).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))+"%" for k in ['reaches_third_label','exact_two_tools_correct_then_answer','strict_correct'])+'|')
lines+=['','所有seed、段数直方图及标签正确后的完整轨迹分层见analysis/boundary-diagnostics.json。条件于模型输出的分层有选择偏差，不能据此估计无偏训练效果。']
(R/'BOUNDARY_DIAGNOSTICS.md').write_text('\n'.join(lines)+'\n')
