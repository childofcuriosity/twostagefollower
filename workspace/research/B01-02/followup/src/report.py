from common import *
import statistics,time
r=json.loads((ROOT/'analysis/results.json').read_text());jobs=json.loads((ROOT/'analysis/completed.json').read_text());assert len(jobs)==12 and all(j['returncode']==0 for j in jobs)
rows=[json.loads(l) for l in (ROOT/'analysis/rows.jsonl').read_text().splitlines()]
labels={'base':'冻结基座','flat':'平坦轨迹训练后','macro':'宏标签训练后','mismatch':'宏模型+错配上下文','random':'均匀随机16次','frequency':'支持集频次启发式','exhaustive':'全部252候选贪心','no-library':'无宏库'}
table='\n'.join(f"| {labels[k]} | {v['test_compression']*100:.2f}% | {v['search_solved_fraction']*100:.2f}% | {v['mean_selected_size']:.2f} | {v['mean_unique_proposed_semantics']:.2f} |" for k,v in r['methods'].items())
ctable='\n'.join(f"| macro − {k.removeprefix('macro-vs-')} | {v['mean_compression_difference']*100:+.2f} | {' / '.join(f'{x*100:+.2f}' for x in v['seed_compression_differences'])} | {' 至 '.join(f'{x*100:+.2f}' for x in v['family_cluster_bootstrap_95'])} | {v['mean_search_difference']*100:+.2f} |" for k,v in r['comparisons'].items())
gpu=sum(j['wall_seconds'] for j in jobs)/3600
passed=r['prespecified_screen_passed']
verdict='通过相对随机提案的预设筛选，但训练后明显弱于冻结基座；不支持“一轮执行学习让模型更会提出有用抽象”。建议停止扩大当前执行训练路线，保留为反例和诊断。' if passed else '未通过预设筛选。当前证据不支持把上一轮的执行收益解释为更有用的抽象发现，不建议继续扩大这套短程序设置的算力投入。'
text=f'''# B01-02 后续实验：抽象提案是否随执行学习改善

完成时间（UTC）：{time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}。用户授权继续实验，本轮已完成，等待结果审核。

## 判断

**{verdict}**

这是使用已有Qwen2.5-1.5B及flat/macro适配器的实测，不是新增提案策略训练。负结果不能否定专门训练创新策略的可能性；正结果也不能代表多轮自我改进。协议在提案生成前固定，分析代码在查看效用结果前另行登记。

## 实际设计

- 8个独立任务家族，各有3个隐含短操作模式，均不与上一轮9个宏语义等价；每家族16条支持程序、128条测试程序。支持与测试精确函数语义隔离，未要求各测试程序彼此语义不同。每家族等权重。
- 模型只看未标注隐含边界的支持程序，生成16次长度2–3的候选宏。语法由有限token trie约束，合法空间252条；重复、恒等提案消耗预算，不补采样。
- base、flat、macro各3次运行，另有3个macro错配上下文对照。旧训练种子为11/22/33；base三次只改变采样种子。
- 所有方法用相同支持集贪心规则选择至多3个语义不同宏；库定义成本计入收益，不利用测试集选择。随机组也只有16次提案；频次/全枚举计算量不同，仅为参照。
- 共12个模型作业、1,536条真实提案。没有新增参数训练，没有重跑上一轮30个训练。

## 主要结果

压缩率是未见程序的净描述长度降低比例，不是神经模型答题正确率。搜索率是外部符号广度优先搜索在3,000次动作扩展内发现完整目标函数的比例。

| 方法 | 测试净压缩率 | 搜索发现率 | 平均库大小 | 每16次提案的不同语义数* |
|---|---:|---:|---:|---:|
{table}

*全枚举使用252次，空库为0；其余方法为16次。确定性启发式/空库在三个seed上重复列入配对分析，不是三次独立实验。宏与基本操作均算一个搜索动作，但宏需要更多底层操作，实际计数见逐家族原始记录。

| 比较 | 压缩差（百分点） | 三seed差 | 家族bootstrap 95%区间 | 搜索差（百分点） |
|---|---:|---|---|---:|
{ctable}

预设筛选：macro相对随机平均压缩提升≥2个百分点，三个seed差值均正，且搜索发现率不低超过2个百分点。判定：**{'通过' if passed else '未通过'}**。区间按8个任务家族聚类，条件于已有检查点；没有将1,536次提案当作独立训练重复。

## 为什么整体判断仍然是否定当前路线

macro相对随机的压缩差为+7.69个百分点，但家族bootstrap区间约−3.11至+18.13个百分点，跨家族不确定性仍大。“通过筛选阈值”不等于显著优于随机。更关键的是，相对冻结base下降18.52个百分点，三个seed均下降，家族区间约−26.76至−10.01个百分点。搜索发现率也比base低6.71个百分点。上一轮“执行更好”没有转化为“提案更好”。

macro优于flat且优于错配上下文，说明宏训练后仍有上下文适配信号；不能将其解释为比训练前更强。每16次提案的不同语义数从base约10.08降到macro约5.33、flat约3.00，多样性收缩与效用下降同时出现，但本实验没有证明多样性下降就是因果机制，更不能据此诊断所有通用能力遗忘。支持集频次启发式的57.04%压缩率也明显更高，但其候选获取计算量不同。

## 事后敏感性复核

两个问题在主结果之后追加，原结果不覆盖，详见[修订声明](analysis/amendments.md)与[完整2×2对照](analysis/sensitivity.json)。

- 原选库器在语义去重时保留最先出现的写法，而压缩要求字面片段匹配。改为先比较支持收益、选中后排除同语义候选：base压缩38.79%、macro19.60%、flat1.53%、随机11.74%；方向保持。全枚举参考提升到57.04%，与频次启发式相同，说明原全枚举劣势来自代表写法选择，而非候选越多越差。
- 保持原选库，改为3,000次基本操作执行预算：base搜索率58.95%、macro55.96%、随机49.22%、flat49.48%；macro仍弱于base。两个改动同时应用也保持这一方向。

因此不建议追加大模型或更多同类执行训练。若继续主线，应另设计直接优化提案效用且检验未见任务家族的训练，加入保持基座提案能力的对照；这是下一步待审核设计，本轮没有悄悄开始该训练。

## 解释边界

1. 上一轮模型学的是执行轨迹，并未接受“提出高效抽象”的奖励或监督。本轮直接检查其迁移，不能把未训练的技能失败解释为创新不可学习。
2. 支持轨迹由正确执行器生成，所有方法相同；不是模型自主解出的成功经验。任务仍是人工DSL，宏语法只有252种。
3. 主要指标是连续原语复用的压缩收益；有压缩不保证搜索更快，加入宏也增加分支因子。因此搜索率单独报告，不挑较好的一个替代失败指标。
4. 等预算指提案次数及相同下游选库规则。模型推理、随机抽样、频次统计的计算成本不同；等动作扩展也不是等基本操作执行成本。
5. 任务与旧训练库分离，但仍使用相同六原语；不是自然语言、真实代码或跨原语系统迁移。
6. 不按本测试集调prompt、温度、候选次数或重新筛家族；保留所有提案、重复及负收益候选。

## 审计与复现

- [预注册协议](PROTOCOL.md)、[机制边界](MECHANISM.md)、[首次登记哈希](analysis/registration.json)、[评估代码登记](analysis/evaluation-registration.json)。
- [机器可读结果](analysis/results.json)、[逐方法/种子/家族记录](analysis/rows.jsonl)、[校验与文件哈希](analysis/verification.json)。
- `runs/*/proposals.jsonl`保留完整提示、生成原文、候选索引与token数；`data/tasks.json`保留全部支持/测试程序和隐含模式；`data/candidates.json`给出候选全集。
- 沿用父目录`runs/*/adapter`及项目根目录`.training-venv`；新增文件全部在本目录树。基础模型和适配器哈希见父目录`analysis/artifact-verification.json`。
- 本轮累计设备预留约{gpu:.3f} GPU·小时，CPU分析墙钟{r['seconds']:.1f}秒；设备预留包含进程加载等等待，不是GPU内核占用时间。任务独立分卡运行，没有NCCL多卡训练。

在项目根目录先`source training-env.sh`。数据构造为`python workspace/research/B01-02/followup/src/common.py`；生成由`src/launch.py`调度（已存在运行目录会拒绝覆盖）；统计、验证和报告分别运行`src/analyze.py`、`src/verify.py`、`src/report.py`。复现时应使用新的运行目录保留原始证据。
'''
(ROOT/'REPORT.md').write_text(text)
(ROOT/'analysis/cost.json').write_text(json.dumps({'reserved_gpu_hours':gpu,'cpu_analysis_wall_seconds':r['seconds'],'model_jobs':12,'raw_proposals':1536},indent=2))
print('Wrote report:',verdict)
