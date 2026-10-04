# 查新记录（2026-09-23）

检索由本次助手通过网页检索/原文阅读完成；另独立验证 EvoScientist 的 Tavily 工具真实可用。不是声称 EvoScientist 已自主完成整个研究闭环。检索并不穷尽所有论文，未检出不能证明首创；仅将下面核对过的原始论文作为候选卡依据。

| 原始来源 | 核对范围 | 对候选的约束 |
|---|---|---|
| [INFUSER, 2606.09052v4](https://arxiv.org/html/2606.09052v4) | §2、§3、§6局限 | 优化器感知效用奖励已存在，目标开发集依赖要控制 |
| [SOAR, 2601.18778v1](https://arxiv.org/html/2601.18778v1) | §3、迁移实验、附录B算力和种子 | 短程学生更新、多副本均值、垫脚石和promotion均有先例 |
| [DARC, 2601.13761v1](https://arxiv.org/html/2601.13761v1) | 方法、Cross-solver generalization、附录B | 跨学生规模课程复用已被展示 |
| [Beyond Uncertainty, 2608.30035v1](https://arxiv.org/html/2608.30035v1) | §4及实验 | 异构模型答案分歧奖励出题已存在，不能当作新方法 |
| [LILO, 2310.19791v2](https://arxiv.org/html/2310.19791v2) | 方法/代码压缩目标 | 自动发现和命名可复用函数库已有先例 |
| [Notes to Self, 2607.20372v1](https://arxiv.org/html/2607.20372v1) | §3–4，GRPO train vs train+test | 训练时用抽象、推理时不用抽象也已评估 |
| [SPEE, 2608.02139v1](https://arxiv.org/html/2608.02139v1) | Stage I/II和实验设置 | 经验池演化、效用筛选、特权经验蒸馏及RL已有组合 |
| [Rethinking Continual Experience Internalization, 2606.04703v1](https://arxiv.org/html/2606.04703v1) | 方法、内化策略对比、附录C/D | 反复内化崩塌、原则级经验和off-policy修复均非新问题 |
| [Learning to Self-Evolve, 2603.18620v1](https://arxiv.org/html/2603.18620v1) | §3.3、式6及其后说明 | 提出累计跨轮目标，但实际简化为单步上下文更新 |
| [SEA, 2607.00871v1](https://arxiv.org/html/2607.00871v1) | §1贡献、§3、局限 | 审核证书/长期门控已有系统，不将普通显著性门控当创新 |

代表性查询（从宽到窄；未命中的查询不作为证据）：
- language model self generated curriculum cross student transfer teacher meta learning 2026
- language model curriculum delayed utility stepping stones non myopic self improvement 2026
- language model invented abstractions counterfactual semantic intervention internalization 2026
- "self-evolution" "curriculum" "cross-model"
- "self-improvement" "delayed" "curriculum" LLM
- "abstraction" "internalization" "self" LLM executable
- "Beyond Uncertainty: Multi-Solver Disagreement" arxiv
- "Rethinking Continual Experience Internalization" arxiv
- "DARC" "2601.13761"

检索发现的二手页面用于定位论文，未将其评价当作原文结论。后续机制分析须继续追踪最近邻参考文献及引用，尤其检索“cross-learner utility/generalization”“task complementarity/non-myopic curriculum”“causal abstraction internalization”，发现重复即修改或淘汰候选。
