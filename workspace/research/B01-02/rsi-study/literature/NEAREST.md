# 最近邻与本研究可区分的问题

查新日期2026-09-24；已读取原论文HTML，以下是摘要性研究定位，不以搜索缺失证明新颖性。

- [Absolute Zero: Reinforced Self-play Reasoning with Zero Data](https://arxiv.org/html/2505.03335v1)，2025。共享模型提案与解题，联合奖励。消融去掉提案训练性能下降，作者已提出任务干扰解释。因此“提案者需要训练”“多角色会干扰”不是本研究首创。
- [Towards Understanding Self-play for LLM Reasoning](https://arxiv.org/html/2510.27072v1)，2025。分析AZR角色熵和冻结提案变体；冻结变体熵更高，训练后高采样预算能力仍受基座约束。不能把多样性下降本身当新机制。
- [Skill Self-Play](https://arxiv.org/html/2607.22529v1)，2026。技能引导提案、求解及课程共同演化；技能专用数据会过度专门化，冻结提案者/反馈求解器有负面影响。需要区分它的正向共同进化与我们执行单目标的受控分离。
- [From Reasoning Traces to Reusable Modules](https://arxiv.org/html/2606.18089v1)，2026。已有组合模块/路由及SFT/RL分工研究，第一轮轨迹标签不是开放式概念发现证据。

待建立的差异：同初始化模型在执行与独立提案效用上的配对变化；同一后续学习器更换提案来源的反事实分支；目标对齐回放与打乱回放的机制控制；完整失败/反例以及提示、预算、模型、语义域的适用范围。若这些不能成立，只能报告受限现象，不宣称已建立新的RSI理论。

额外混淆来源：[Understanding Catastrophic Forgetting in Language Models via Implicit Inference](https://arxiv.org/html/2309.10105v2)，ICLR 2024。提出微调可改变隐式任务判断，部分“遗忘”能通过改变提示恢复。因此即使三种提示仍退化，也不能证明能力从参数中消失；本研究使用有限预算下的可用提案效用措辞，并明确不排除其他提示恢复。

采样预算对照来源：[Does Reinforcement Learning Really Incentivize Reasoning Capacity in LLMs Beyond the Base Model?](https://arxiv.org/abs/2504.13837)，2025。以高采样预算评估基座与训练后模型的覆盖差异。我们的K曲线借用这一评测思路，不把它宣称为新方法，也不将RL结论直接移植到LoRA执行SFT。
