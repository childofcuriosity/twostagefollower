import json,statistics,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
main=json.loads((ROOT/'analysis/results.json').read_text())
second=json.loads((ROOT/'secondary/analysis/results.json').read_text())
cost=json.loads((ROOT/'analysis/compute-cost.json').read_text())
secjobs=json.loads((ROOT/'secondary/analysis/completed.json').read_text())
assert len(secjobs)==6 and all(r['returncode']==0 for r in secjobs)
cost['reserved_gpu_hours_by_phase']['secondary']=sum(r['wall_seconds'] for r in secjobs)/3600
cost['total']=sum(cost['reserved_gpu_hours_by_phase'].values())
(ROOT/'analysis/compute-cost.json').write_text(json.dumps(cost,indent=2))
def mean(c,split,world='original',tag=''):
 return statistics.mean(json.loads((ROOT/f'runs/{c}-{world}-s{s}{tag}/summary.json').read_text())['evaluation']['groups'][split]['accuracy'] for s in [11,22,33])
def pc(x):return f'{100*x:.2f}%'
comparison=main['primary_comparisons']['macro-vs-flat']
sec_table='\n'.join(f"| {c} | {pc(statistics.mean(second['conditions'][c]['iid']))} | {' / '.join(pc(x) for x in second['conditions'][c]['ood'])} | {pc(statistics.mean(second['conditions'][c]['ood']))} | {pc(statistics.mean(second['conditions'][c]['pressure']))} |" for c in ['flat','macro'])
core_table='\n'.join(f"| {c} | {pc(mean(c,'iid'))} | {pc(mean(c,'ood'))} |" for c in ['flat','macro','natural','shuffled'])
files=list((ROOT/'runs').glob('*/predictions.jsonl'))+list((ROOT/'secondary/runs').glob('*/predictions.jsonl'))+list((ROOT/'analysis/routing-probe').glob('*.jsonl'))
raw_count=sum(sum(1 for _ in p.open()) for p in files)
report=f'''# B01-02 结果审核报告

状态：已完成本轮机制分析与实验，等待用户统一审核。生成时间（UTC）：{time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}。

## 我的判断

**发现了可重复的训练表示效应，但还没有证明“模型学会了创新”。建议暂不把当前题目推进为论文主线，保留机制观察及实验资产。**

主实验通过预设的3个百分点筛选阈值：按宏名称组织轨迹，比等信息、等训练token的平坦轨迹提高 **{comparison['mean_difference']*100:.2f} 个百分点**。不过失败主要发生在长链组织/提前停止；外部逐步路由能让两组都达到100%，已有内容寻址和组合泛化文献又非常接近。因此“大幅涨分”不能直接转换为新颖的抽象发现结论。新颖性判断在实验期间因补充查新而下调，这个变化保留在记录中。

## 实际做了什么

- 基座：Qwen/Qwen2.5-1.5B，固定revision `8faed761d45a263340a0528343f099c05c9a4323`；更新18,464,768个LoRA参数，rank16、alpha32。不是全参数预训练，也不是完整SPEE复现。
- 每个正式训练：512个优化步，batch32，16,384个训练样本呈现（4,096条数据重复4轮），种子11/22/33。原始主组每次2,430,112个非padding输入token，其中1,055,432个监督target token。
- 全部在本项目`.training-venv`运行：torch2.7.1+cu128、transformers4.51.3、peft0.15.2。利用本机RTX PRO 6000 Blackwell分卡运行独立作业；没有宣称完成NCCL多卡训练验收。
- 12个主对照训练、6个名称/语义干预、6个事后对齐对照、6个第二环境复核，共30个正式训练；另有1次训练校准、2个冻结模型基线、7个外部路由诊断。检查点和失败日志保留。
- 合计保留 **{raw_count:,} 条逐题原始记录**，包含同一评测题在不同模型/种子下的重复测量，不能当成同样多的独立测试题。

## 主实验结果

训练宏组合深度1–2，测试深度3–5；测试时不提供宏函数库，只保留各组相同的原语说明。最终OOD有384题，但只有96个不同程序组合，每个4个输入。精确仿射signature排除了与训练程序等价的测试函数。

| 条件 | 同分布IID均值 | 未见组合OOD均值 |
|---|---:|---:|
{core_table}

macro的三个OOD结果：30.73%、37.76%、20.83%；flat：0.26%、0%、0%。macro-flat配对差值均为正，均值29.69个百分点，按三个训练种子的t区间约 **8.60–50.78个百分点**。按程序聚类、条件于这三个checkpoint的描述性bootstrap约22.13–37.15个百分点。两种区间含义不同，不能将后者作为增加训练种子数的替代。

flat/macro/shuffled的真实累计训练输入token、监督token、样本数逐项完全相同。natural有更多监督token（1,312,060），属于次要对照。所有组推理上限同为256 token，但实际平均生成长度不同：flat约67.1、macro约90.7 token/题，**不能声称总推理算力相同**。

## 理论分析与干预说明了什么

1. **信息等价。** flat与macro的展开原语、每一步状态、最终答案、分组边界相同；macro标签可由输入里的函数调用顺序确定性恢复。故差异是有限训练下的表示组织/优化效应，不是新增监督信息。
2. **模块会执行，长链不一定会组织。** 原始flat种子11的383个OOD失败中，375个是正确前缀之后提前停止。外部循环按题面调用顺序逐个请求宏，后一步只用模型前一步输出、不喂oracle状态：flat和macro三个种子均100%（每次96个独立程序），冻结模型0%。这是不同推理流程和成本的事后诊断，不能替换自主OOD分数。
3. **改名不等于严格不变。** 名称循环置换后macro平均OOD为{pc(mean('macro','ood','renamed'))}，原始为{pc(mean('macro','ood'))}，种子间变化较大。可排除只依赖某一固定名字才能工作，但不能宣称名称不变性已充分成立。
4. **行为跟随训练语义。** 对新旧答案不同的550题，语义置换模型三个种子按新语义准确率45.09%–70.00%，旧语义匹配率均0%。这支持参数行为依赖新训练定义；置换也改变部分展开长度，不能把跨世界分数差纯归为语义因素。
5. **对齐替代解释仍存在。** 追加共享call-tags输入的配对训练：稳定宏标签平均OOD {pc(mean('macro','ood',tag='-tagged-stable'))}，每例随机调用标签平均 {pc(mean('macro','ood',tag='-tagged-call'))}。后者没有固定的输出标签→宏语义对应，也能有部分迁移，但种子波动大，不能宣称两者等价或确定谁更好。此实验改变了共同输入，不能直接与原flat作单因素比较。

完整推导、可识别性边界及480函数闭包分析见[MECHANISM.md](MECHANISM.md)。有限输入输出证据不能唯一确定神经网络内部算法；本轮没有做激活干预或神经概念定位。

## 第二个独立生成器（事后复核）

变长a/b字符串，独立原语实现与验证器。训练输入长度3–6，额外压力测试长度7–8；OOD仍为96程序×4输入。沿用模型提出的宏结构，在新的原语语义下分别训练；**不是零样本跨域迁移**。所有宏在长度3–8的全部二元字符串上验证仿射重建。

| 条件 | IID均值 | OOD种子11/22/33 | OOD均值 | 更长输入压力集 |
|---|---:|---|---:|---:|
{sec_table}

该环境macro-flat平均差值为{second['mean_difference']*100:.2f}个百分点。短二元字符串容易偶然匹配答案，需同时查看[第二环境统计](secondary/analysis/results.json)中的精确原语序列和四个输入全对的程序比例，不能只看答案正确率。其中四个输入全对的程序比例：flat三个种子均为0%，macro为29.17%、13.54%、22.92%；因此收益不完全由偶然答案匹配解释。更长输入压力集macro仅6.94%，长度泛化仍弱。它仍是人工DSL，不能替代自然代码/数学任务。

## 为什么不建议直接写成论文

最早“自发现”的证据本身很弱：128次逆向解题仅1次成功；160次提案仅17次格式有效，得到9个不同非恒等函数。132次提案首行无法按协议解析，11次长度不符，所以失败混有基座模型指令格式问题。选中的8个正压缩分数是相对于包含错解的轨迹频次，不能当成真实学习效用。

实际9个宏不含ends，闭包只有480种函数；库固定一次后再训练，没有证明迭代后更擅长在新领域提出有用抽象。我们还没有完成大规模基模训练、自然任务迁移、多模型家族复核或学习发现策略的比较。

最近邻越来越近：[Notes to Self](https://arxiv.org/html/2607.20372v1)和[SPEE](https://arxiv.org/html/2608.02139v1)已有经验抽象训练/内化；[From Reasoning Traces to Reusable Modules](https://arxiv.org/html/2606.18089v1)已研究组合模块及训练干预；[Your Context Is Not an Array](https://arxiv.org/html/2408.05506v1)已研究内容寻址标记和对齐如何影响长度泛化。我们当前的宏标注效果尚不足以和这些工作形成明确的新研究贡献。

**推荐决策：不扩到大模型或昂贵RL，不把本轮写成“AI学会创新”的论文。保留“模块能力与自主路由分离”的可复现观察，用于下一轮选题；若继续此题，应先找到现有内容寻址/路由文献未覆盖的问题，并把“在未见域提出更有用抽象”设为独立指标。后续方向等待本次审核。**

## 失败、验证与成本

- 保留原始安装网络慢请求、首次同步Tavily失败（项目先前冒烟）、本轮冻结基线参数启动失败、初始测试语义容量不足的失败记录；本轮协议修订按时间写在[amendments.md](analysis/amendments.md)。
- 冻结无库基线存在大量继续续写、多个Answer行的格式问题，不能当强基线。主训练组严格整行答案审计未发现由宽松解析造成的正确性虚增；最终审计见[parser-audit-final.json](analysis/parser-audit-final.json)。
- 独立重新计算逐题真值、检查数据隔离与真实训练token匹配，记录基础模型及适配器SHA256。主环境见[artifact-verification.json](analysis/artifact-verification.json)，第二环境见[verification.json](secondary/analysis/verification.json)。
- 按作业墙钟累计的设备预留估计约 **{cost['total']:.2f} GPU·小时**，含基线、干预、追加对照、路由诊断、第二环境、发现与校准；不是GPU内核busy time，也不含安装/下载等待。原48–120 GPU·小时是粗规划，本轮短序列LoRA筛选实际远低于它，不为用满预算而扩大实验。详见[compute-cost.json](analysis/compute-cost.json)。

## 审核入口与复现

- [完整表格](analysis/RESULT_TABLES.md)、[机器可读主统计](analysis/results.json)、[第二环境统计](secondary/analysis/results.json)。
- [事前协议](PROTOCOL.md)、[机制分析](MECHANISM.md)、[全部修订及事后分析声明](analysis/amendments.md)。
- `runs/*/predictions.jsonl`及`secondary/runs/*/predictions.jsonl`：逐题原始输出；各运行目录包含`config.json`、`train.jsonl`、`summary.json`和`adapter/`。
- `data/discovery-traces.jsonl`、`data/proposals.jsonl`：真实解题与提案，包含失败；`analysis/routing-probe/`：外部路由全部调用记录。
- 根目录`training-env.sh`、`install-training-env.sh`与`training-requirements.lock.txt`保存项目内环境。按README运行脚本；官方EvoSkills仍在原项目安装目录。所有新增环境、模型、缓存、结果均在当前根目录，未发布或提交论文。
'''
(ROOT/'REPORT.md').write_text(report)
print('Wrote report',len(report),'characters;',raw_count,'raw records;',cost['total'],'reserved GPU-hours')
