from pathlib import Path
import json,csv,collections,sys,hashlib
O=Path(__file__).resolve().parent;R=O.parent;sys.path.insert(0,str(R/'src'));import dsl
cases=[json.loads(l) for l in (O/'all-discordant-pairs.jsonl').read_text().splitlines()];s=json.loads((O/'attribution-summary.json').read_text());strict=[c for c in cases if c['macro_audit']['category']=='fully_correct_trace'];ex=[c for c in cases if c not in strict]
s['supplemental']={'flat_header_counts':dict(collections.Counter(len(c['flat_audit']['headers']) for c in cases)),'generated_tokens_range':[min(c['flat_audit']['generated_tokens'] for c in cases),max(c['flat_audit']['generated_tokens'] for c in cases)],'strict_macro_trace_subset':len(strict),'strict_subset_categories':dict(collections.Counter(c['flat_audit']['category'] for c in strict)),'nonexact_macro_trace_count':len(ex),'nonexact_macro_globally_equivalent':sum(dsl.signature(c['macro_audit']['expected_ops'])==dsl.signature(c['macro_audit']['emitted_ops']) for c in ex),'manual_review_sample_count':69,'manual_review_completed':True}
(O/'attribution-summary.json').write_text(json.dumps(s,indent=2))
with (O/'all-discordant-index.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['model','seed','id','split','tools','flat_category','macro_trace_exact','flat_steps','required_steps'])
 for c in cases:w.writerow([c['model'],c['seed'],c['id'],c['split'],' '.join(t['name'] for t in c['tools']),c['flat_audit']['category'],c['macro_audit']['category']=='fully_correct_trace',len(c['flat_audit']['emitted_ops']),len(c['flat_audit']['expected_ops'])])
labels={'correct_first_two_then_answer':'前两个工具完整正确，然后输出答案','wrong_operation_sequence':'操作序列错误，所输出操作的数字计算正确','correct_prefix_stop_inside_tool':'正确执行了前缀，但在某个工具内部结束','wrong_ops_and_arithmetic_error':'操作序列与数字计算均有错误','format_or_missing_answer':'步骤格式异常（本批为gold被当作基本操作）'}
rows='\n'.join(f"| {labels[k]} | {v} | {v/len(cases):.2%} |" for k,v in s['categories'].items())
modelrows=[]
for model in s['by_model']:
 rs=[c for c in cases if c['model']==model];n=sum(c['flat_audit']['category']=='correct_first_two_then_answer' for c in rs);modelrows.append(f'| {model} | {len(rs)} | {n} | {n/len(rs):.2%} |')
text=f'''# 工具标签正确、统一标签错误：全量案例归因

本分析只读取既有模型输出，不重新训练或生成。分析对象是第一阶段执行实验，不是压缩提案实验。

## 数据规模与口径

每次训练使用4,096条：1次工具调用394条、2次调用3,702条（90.38%）。开发集224条：短题128、开发长题96。测试集560条：短调用128、长组合384、压力48。开发集不计入下面的测试分析。

三个模型Qwen2.5-1.5B、Qwen2.5-3B、SmolLM2-1.7B，各训练seed 11/22/33，每个seed配对macro与flat。按相同题目ID、数字输入和工具调用链对齐，从全部560测试题筛选macro最终答案正确且flat最终答案错误。

得到1,473条模型—seed—题目配对记录，覆盖370个不同测试题ID，其中长组合1,302条、压力171条、短调用0条。不同seed/模型重复测同一道题，不能作为1,473个独立测试题做显著性推断。

程序对全部案例重算执行真值、检查最终答案、原语顺序、逐步数字计算及格式。另按模型×seed各随机读3条，并补读少见类型与macro过程异常样例，去重共69条，抽样seed=20260925。没有人工逐条阅读全部1,473条。

## 全量可观测错误类型

| flat错误类型 | 条数 | 占条件样本比例 |
|---|---:|---:|
{rows}

| 模型（三seed合计） | 条件案例 | 正确前两工具后结束 | 比例 |
|---|---:|---:|---:|
{chr(10).join(modelrows)}

全部1,473条flat输出恰好包含两个step:段，并主动写出Answer。输出55–85个token，生成上限256，触及上限0条；不是生成长度预算耗尽造成的截断。没有缺失Answer的记录。

164条“操作序列错误”中，第一工具全部正确，偏离发生在之后。有的直接跳过第二工具，改执行后面的工具；有的把其他工具操作混入第二段。8条前缀不完整者也只有两个step:段，但不能都称“恰好执行前两个工具”。唯一数字计算错误案例为qwen1.5b/seed33/题4873，第一步rev就把输入8 8 8 8写成6 8 8 8。三个格式异常为qwen3b/seed11/题4626–4628，出现gold加数字的行；并非没有最终答案。

## 对成功一侧的严格复核

macro答案正确不必然代表过程正确。本批1,473条中，1,448条完整操作序列和数字过程正确；另外25条操作序列不同但最终答案匹配。25条中12条整段操作与要求在全部数字输入上语义等价；另外13条仅在当前测试输入上答案匹配，不能认定正确执行了所要求的程序。

只保留macro过程也完全正确的1,448条后，flat中仍有1,281条（88.47%）正确执行前两个工具后结束。其余155条操作序列错误、8条前缀不完整、3条格式异常、1条操作及算术错误。主要观察不依赖这些答案碰巧匹配或等价改写的案例。

## 原因判断与边界

已经直接观察到的是：两段式输出模板和过早给出答案占主导，数字运算能力不是这批差异的主要问题。训练中90.38%的样例恰好调用两个工具，且没有超过两个工具的训练样例。因此一个有依据的假设是：统一step标签模型学到了“两段后结束”的训练分布习惯，工具身份标签有助于继续追踪未完成调用。

这仍是行为证据和机制假设，未完成因果识别。两个step段不等于内部只能处理两个工具；错误类型也不能单独证明某种注意力机制。需固定其余条件，干预调用序号、剩余调用数提示或训练长度分布才能区分。此次未新增这些实验。

该比例仅适用于“macro答案正确、flat答案错误”的条件样本，不能推及所有flat失败或所有macro成功。压力输入含对称数字，更需同时报告过程与答案。

## 文件

- [全部1,473条原始输入输出与逐题核验](all-discordant-pairs.jsonl)
- [可筛选案例索引](all-discordant-index.csv)
- [完整分模型/测试划分统计及原始文件哈希](attribution-summary.json)
- [69条人工阅读抽样](manual-review-sample.jsonl)
- [可复现分析脚本](analyze_pairs.py)

历史训练结果未被修改。本次分析及全部导出均在当前目录。
'''
(O/'ATTRIBUTION.md').write_text(text)
print('Report written; cases',len(cases),'strict',len(strict))
