import collections,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'analysis/subtask-factorization.json').read_text())
rows=[json.loads(l) for l in (R/'analysis/subtask-factorization-segments.jsonl').read_text().splitlines()]
parts=['# 已有轨迹的单工具分解与乘积预测\n','本次只离线读取已有输出，无推理、无训练。四个Qwen2.5 Base尺度，各三个训练种子。分析10368条名称组轨迹及对应10368条step轨迹；名称组含48384个要求调用位置、40119个实际输出段。原测试384题×3seed/模型，独立确认480题×3seed/模型。不是所有轨迹均为独立程序。\n',
'## 评分与预测\n',
'- A：第i个实际输出的名称等于输入要求的第i个名称。缺失计错，不能只在输出过的段里算。\n- B：一个实际输出的合法名称之后，基本操作序列完整对应这个名称，数字转换正确。即使名称选错但按该名称正确展开，B仍正确。数字正确性以实际输入状态计算；不能当作oracle的正确状态测量。\n- 未输出名称的后续B不可观测，不计成失败或成功；因此B有幸存样本选择，不能直接解释为独立调用准确率。\n- 主要预测：同模型、同seed、同长度估计pA与pB，对长度L预测(pA×pB)^L。5折按完整工具序列分组，在其他4折估计，预测留出折。原题不同数字输入和三个seed对同序列使用相同折。\n- 敏感性：逐位置pA(L,i)乘以逐工具pB(tool)，再连乘；另存逐位置联合成功率连乘。这些估计对有限样本和条件分组敏感，不能挑最接近的一个当独立性证明。\n- 整体主评分：指定操作轨迹和全部数字、最终答案均正确；区别于仅最终答案正确。10368条重组结果与已有严格评分全部一致。额外段、最终回答和格式也检查；乘积模型没有单独拟合最终结束，属于其适用边界。\n- 最小评分检查覆盖名称错误但展开正确、缺段、工具内部截断、算术错误四种情况。\n',
'## 原3–5调用题\n','| 模型 | 单位置名称正确 | 已输出名称的展开正确 | 完整名称序列正确 | 简单乘积预测整题 | 实际名称组整题 | 实际step整题 |\n|---|---:|---:|---:|---:|---:|---:|']
unit=[]
for model in ['qwen1.5b','qwen3b','qwen7b','qwen32b']:
 rs=[r for r in rows if r['family']=='main' and r['model']==model];slots=[s for r in rs for s in r['slots']];segs=[s for r in rs for s in r['segments'] if s['tool'] is not None]
 a=sum(s['A'] for s in slots)/len(slots);b=sum(s['B'] for s in segs)/len(segs);names=sum(r['name_sequence_ok'] for r in rs)/len(rs)
 z=next(r for r in d['aggregate'] if r['family']=='main' and r['model']==model and r['length']==0)
 unit.append(dict(model=model,A_correct=sum(s['A'] for s in slots),A_total=len(slots),B_correct=sum(s['B'] for s in segs),B_total=len(segs),name_sequence=names))
 parts.append('| '+model+' | '+' | '.join(f'{100*v:.2f}%' for v in [a,b,names,z['pooled_product'],z['actual'],z['flat_strict']])+' |')
parts+=['\n## 32B按长度：简单乘积与更细分乘积\n','| 数据集 | 调用数 | 简单乘积 | 位置/工具细分乘积 | 实际名称组 | 实际step |\n|---|---:|---:|---:|---:|---:|']
for family in ['main','independent']:
 for z in d['aggregate']:
  if z['model']=='qwen32b' and z['family']==family and z['length']:
   parts.append(f'| {family} | {z["length"]} | '+' | '.join(f'{100*z[k]:.2f}%' for k in ['pooled_product','position_tool_product','actual','flat_strict'])+' |')
parts+=['\n## 判断\n','原3–5调用题的简单乘积预测与实际名称组整体差距为约0.6–2.4个百分点；在这个汇总层面，用户提出的两部分分解有定量支持。32B已输出名称后的完整展开约99.6%，名称序列完整正确约74.7%，完整执行约73.0%，描述性上主要损失在名称序列完整性/选择，而非给定已生成名称后的数字运算。\n',
'但独立确认集32B在5/6/8调用上简单乘积明显低估：47.35/21.01/9.54%对57.99/32.64/24.65%。说明不能把原测试的接近推广为普遍独立；细分位置和工具后的预测仍低估。失败可能在整条轨迹内聚集，包含提前停止后后续名称均缺失这一结构依赖，也可能来自程序/状态难度差异及不可观测B的选择偏差。当前只支持概率近似在部分长度有效，不识别内部独立学习机制。\n',
'更细分乘积在原测试四尺度上预测22.83/52.59/55.47/69.09%，对实际29.77/59.72/57.90/73.00%；说明总体接近会受到概率估计方式影响，不能只展示较有利的汇总公式。\n',
'无名称的step输出没有独立可观测的名称选择事件，不能从轨迹强行造出与名称组同义的A、B。此次将其严格整题成绩作为基线，而不把它的每段操作当作模型显式选择了某名称。\n',
'该分析不是oracle实验：既没有纠正名称也没有补齐未发生的工具执行。需要oracle干预才能补齐这些反事实能力证据。\n',
'## 可复核文件\n','- `src/subtask_factorization.py`：读取原始文件、核验哈希、段落评分、程序分组交叉预测。\n- `analysis/subtask-factorization.json`：数据来源、逐seed/长度指标、汇总与条件bootstrap区间（仅固定预测残差的程序重采样，不覆盖拟合不确定性，不据此断言统计等价）。\n- `analysis/subtask-factorization-segments.jsonl`：所有名称、基本操作、状态与A/B逐项评分。\n- `analysis/subtask-factorization-predictions.jsonl`：每题留出预测和实际成绩。\n- `analysis/subtask-factorization-checks.json`：评分边界检查。\n']
(R/'SUBTASK_FACTORIZATION.md').write_text('\n'.join(parts))
(R/'analysis/subtask-factorization-unit-counts.json').write_text(json.dumps(unit,indent=2))
(R/'analysis/subtask-factorization-source-hashes.json').write_text(json.dumps({name:hashlib.sha256((R/name).read_bytes()).hexdigest() for name in ['src/subtask_factorization.py','src/report_subtask_factorization.py','SUBTASK_FACTORIZATION.md']},indent=2))
print('\n'.join(parts[:9]));print(json.dumps(unit))
