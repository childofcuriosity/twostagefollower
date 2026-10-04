from pathlib import Path
import json,statistics,time
R=Path(__file__).resolve().parents[1];d=json.loads((R/'analysis/results.json').read_text());e=json.loads((R/'analysis/extended-results.json').read_text());ci=json.loads((R/'analysis/paired-inference.json').read_text())
assert not d['missing'];assert e['records_checked']==13440
fmt=lambda v:f'{100*v:.2f}%'
table=[]
for model in ['qwen1.5b','qwen3b','qwen7b','qwen32b']:
 for c in ['flat','macro']:
  r=next(r for r in d['summary'] if (r['model'],r['condition'],r['split'])==(model,c,'ood'))
  v=r['means'];table.append(f"| {model} | {c} | {fmt(v['accuracy'])} | {fmt(v['strict_trace'])} | {fmt(v['correct_prefix_early_answer'])} | {fmt(v['exact_two_tools_early_answer'])} | {fmt(v['two_output_segments'])} |")
error_table=[]
for row in d['summary']:
 if row['split']=='ood':
  v=row['means'];error_table.append(f"| {row['model']} | {row['condition']} | {fmt(v['wrong_operation'])} | {fmt(v['numeric_step_error'])} | {fmt(v['format_extra_lines'])} | {fmt(v['missing_or_multiple_answer'])} |")
extable=[]
for r in e['summary']:
 extable.append(f"| {r['model']} | {r['condition']} | {r['split']} | {fmt(r['accuracy'])} | {fmt(r['strict_trace'])} | {fmt(r['exact_two_tools_early_answer'])} |")
intervals=[]
for model,c in ci['comparisons'].items():
 x=c['ood']['accuracy'];intervals.append(f"| {model} | {100*x['mean']:+.2f} | {' / '.join(f'{100*v:+.2f}' for v in x['seed_differences'])} | {' 至 '.join(f'{100*v:+.2f}' for v in x['seed_t95'])} | {' 至 '.join(f'{100*v:+.2f}' for v in x['program_bootstrap95'])} |")
cal=[];cost=[]
for model in ['qwen7b','qwen32b']:
 z=json.loads((R/f'analysis/{model}-calibration.json').read_text());m=z['microbatch'];p=R/f'{model}/runs/flat-original-s11-probe-m{m}/summary.json';v=json.loads(p.read_text());cal.append(f"| {model} | {m} | {32//m} | {v['training']['peak_memory_bytes']/1024**3:.2f} | {v['training']['seconds']/2:.2f} |")
 for stage in ['completed','checkpoint-tests-completed']:
  for v in json.loads((R/f'analysis/{model}-{stage}.json').read_text()):cost.append(v['wall_seconds'])
 for v in z['probes']:cost.append(v['wall_seconds'])
# Use actual evaluation time, not waiting time, for extended passes.
for model in ['qwen1.5b','qwen3b','qwen7b','qwen32b']:
 for v in json.loads((R/f'extended/{model}/completed.json').read_text()):cost.append(v['wall_seconds'])
primary_cost=sum(cost)
supplement_cost=0
for lane in ['lr','instruct']:
 records=json.loads((R/f'analysis/supplement-{lane}-completed.json').read_text())
 assert all(x['returncode']==0 for x in records)
 supplement_cost+=sum(x['wall_seconds'] for x in records)
cost.append(supplement_cost)
(R/'analysis/cost.json').write_text(json.dumps({'gpu_reserved_hours_approx':sum(cost)/3600,'primary_and_confirmation_process_hours':primary_cost/3600,'supplement_process_hours':supplement_cost/3600,'note':'single-GPU subprocess wall times for new training, calibration, checkpoint evaluation; extended model loading omitted; pre-launch queue waiting and downloads excluded, but early checkpoint subprocesses may include waiting for saved weights; not GPU kernel busy time; includes completed supplement lane records; excludes unmeasured failed-start overhead and separate sharded smoke probe'},indent=2))
text=f'''# 模型规模与两段早停：第一阶段结果

生成UTC：{time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}。自动汇总已完成，科学判断需结合CONCLUSIONS.md的人工审核。执行者为Codex直接运行脚本，非EvoScientist聊天驱动。

## 设计与完成范围

同系列Qwen2.5 Base的1.5/3/7/32B，flat与macro各3训练seed。原1.5/3B复用旧适配器，7/32B各新增6次512步LoRA；4,096训练题、有效batch32，16,384次样例呈现。两组输入、基本操作与正确状态相同，仅输出段首step或对应工具名称不同。

原训练90.38%是两次调用，没有超过两次的训练题。所有原测试560条：IID128、长组合384、压力48；本报告分析全量输出，不以macro对flat错筛选。单模型seed为重复训练，同一道题多次测量不是独立样本。

注册检查点0/16/64/128/256/512，保存全部权重；在线开发集评测，训练完成后统一测试固定检查点，不据测试选最佳轮次。模型revision和SHA在models/*/download-manifest.json。

独立确认集480条：3/4/5/6/8调用各24个程序、每程序4个输入，共120个程序；精确功能与旧train/dev/test不重合。新测试最大生成512token，旧题256token。新题的冻结基线提供完整工具定义，不提供定义则基座不可能知道人为颜色映射；给定义与不给定义的成绩分开解释。

## 原测试：未见3–5调用，三个seed平均

| 模型 | 标签 | 答案正确率 | 完整轨迹正确率 | 正确前缀后提前回答 | 正确前两工具后结束 | 恰好输出两段 |
|---|---|---:|---:|---:|---:|---:|
{chr(10).join(table)}

“正确前两工具后结束”严格要求操作和数字前缀正确、主动写出对应中间状态答案，属于可直接验证的早停子集。其他操作错误/漏项不强行归入该类。“两段”只是输出行为，不代表过程正确。原始程序只保存非EOS token数，未保存末尾token ID：小于长度上限减一可根据生成配置推断在上限前遇到EOS；恰为上限减一则边界不确定；达到上限记为长度耗尽。这是推断证据，不冒充直接记录的停止原因。EOS不等于完成任务，主动写出中间答案也需结合完整轨迹判断。答案正确但轨迹不正确的情况不计入完整轨迹指标。

## 局部操作与格式错误

以下指标可以重叠，不能相加作为互斥原因占比。“操作选错”要求已输出的某个操作偏离应有顺序（或多出操作）；仅少执行后缀不计入此项。“数值算错”根据前一个已报告状态检查当前操作，避免把上游错误重复算成每一步算术错误。这些是行为证据，不是机制因果证明。

| 模型 | 标签 | 操作选错 | 数值算错 | 额外格式行 | 缺失或多个答案 |
|---|---|---:|---:|---:|---:|
{chr(10).join(error_table)}

## 配对差异与区间

下表为macro−flat答案正确率，单位百分点。seed区间以三个训练seed计算t区间，程序区间为固定这三个seed后按完整调用链聚类bootstrap，两个区间口径不同。

| 模型 | 均值差 | 三seed差 | seed 95% t | 程序聚类95% |
|---|---:|---|---|---|
{chr(10).join(intervals)}

## 新确认集与更长调用

frozen指未微调基座，提供工具定义；其他条件为训练后、不给定义。不能将此跨提示差直接归为训练增益/退化。

| 模型 | 条件 | 长度组 | 答案正确率 | 完整轨迹正确率 | 正确前两工具后结束 |
|---|---|---|---:|---:|---:|
{chr(10).join(extable)}

## 资源实测与实现检查

| 模型 | microbatch | 累积次数 | 两步校准峰值GiB | 校准秒/优化步 |
|---|---:|---:|---:|---:|
{chr(10).join(cal)}

约{sum(cost)/3600:.2f} GPU小时，见analysis/cost.json口径，包括补充训练/评测进程，不含网络下载、启动前排队、未完整计时的失败启动及单独跨卡冒烟；提前检查点评测的进程耗时可能包含等待权重就绪，不是纯GPU核忙碌时间。数据和缓存均在项目目录。

原microbatch16拆到4的BF16梯度测试未达到事先选择的3%相对差容差，保留失败记录；使用原microbatch16、仅启用梯度检查点的1.5B核对损失/梯度一致。各模型实际microbatch列在表中；若发生回退须承认浮点计算实现差异。主线未量化。

## 解释边界与未完成的研究分支

这是同系列规模相关性，不是参数规模的完全随机因果实验。不同预训练过程、架构与LoRA比例不能完全控制。模型更大不自动等于先验更稳定。

已完成3B/32B对称低学习率1e-4与32B-Instruct三个seed的flat/macro补充训练、固定最终测试及Instruct冻结基线，见[补充报告](SUPPLEMENT.md)。这仍不是真实Agent交互验证。冻结模型在当前协议下未建立可靠的初始长执行能力，先验保护/破坏仍无法据此识别。相同提示信息的训练前后比较见analysis/matched-context.json。

[结论与限制](CONCLUSIONS.md)报告全部主要发现、LoRA比例与协议偏差；analysis/outcome-diagnostics.json补充全量等价轨迹/偶然正确分类。固定曲线不按测试挑选检查点；开发集掌握阈值未在预登记中数值化，后补阈值只能作为探索性分析。

## 图表

![规模与两种停止指标](figures/scale-comparison.png)

![独立程序长度外推](figures/independent-lengths.png)

![完整固定检查点曲线](figures/learning-curves.png)

图像另提供同名SVG/PDF。三个图组已目视检查；曲线连接固定检查点均值，不代表未测量中间步骤的数值。

## 复现资料

- [逐题最终审计](analysis/final-case-audit.jsonl)、[原测试统计](analysis/results.json)、[独立确认统计](analysis/extended-results.json)。
- [配对区间](analysis/paired-inference.json)、[数据登记](analysis/extended-data-registration.json)、[注册与修订](WORK_STATUS.md)。
- 原始输出在各模型runs/和extended/，最终与中途LoRA适配器完整保留。
'''
(R/'REPORT.md').write_text(text);print('Report draft generated; manual conclusion required',flush=True)
