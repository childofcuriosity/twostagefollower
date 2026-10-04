# 实现与优化口径（预检阶段）

本地检索（含被.gitignore忽略的源码）未发现已有GRPO实现，环境未安装TRL/vLLM/datasets。复用已验证的Transformers/PEFT加载、旧Prompt及严格评分，编写可审计的双卡GRPO循环；数学定义参照[TRL v0.16.1官方GRPO说明](https://huggingface.co/docs/trl/v0.16.1/grpo_trainer)。这不是声称直接使用TRL Trainer。

每题8个候选，优势=(二值奖励−组均值)/(组内样本标准差+1e−4)。全0/全1组优势0，正常保留。loss先对每回答的有效输出token平均，再对候选等权平均。包括真实EOS，不包括prompt、padding；不截去错误回答或只奖励正确前缀。两rank各8题×8候选，DDP平均后等价全16题×8候选等权更新。

reference为同一冻结原始模型（禁用LoRA）；KL估计exp(logp_ref−logp_policy)−(logp_ref−logp_policy)−1。每批fresh rollout只做一次optimizer更新（μ=1），旧策略为本次更新前策略；实现用当前logp.detach作旧logp。clip ε=0.2保留于目标，但μ=1时ratio前向等于1，裁剪不实际截断本批更新；不把它宣称为多轮PPO式信任域约束。实际漂移通过KL、梯度范数及训练曲线监测。

预检候选配置：LoRA r16/alpha32/dropout0，七种投影；BF16基座、FP32可训练adapter主权重及AdamW状态，无量化；lr1e−5、5更新线性warmup后恒定，β0.04、梯度范数裁剪1。采样temperature1/top_p1/top_k0；完整回答上限沿用256，贪心评测配置不变。正式参数须在预检和恢复检验后写config/frozen.json，不能根据NAME是否领先挑配置。

checkpoint包含adapter、optimizer、各rank的CPU/CUDA/Python RNG状态以及更新计数。step0有配对初始化哈希；验证和测试基准由禁用adapter的同一原始权重生成，各seed引用同一组step0，不伪造额外独立重复。

冻结正式配置采用precheck-v2：启用torch.use_deterministic_algorithms(True)，CUBLAS_WORKSPACE_CONFIG=:4096:8；其余候选超参数不变。v1恢复检查出现反向/更新数值差异；v2两组恢复后的采样序列与奖励完全一致，最终adapter逐元素差为0。原始失败保留，不按NAME领先选择设置。正式六run均从原始模型重新初始化。

精度细节：没有额外AMP autocast。PEFT 0.15.2的Linear.forward把LoRA分支输入转换到adapter权重dtype，因此冻结基座线性/注意力使用BF16，LoRA分支参数及矩阵计算为FP32，合并输出转回基座dtype；Adam状态为FP32。这里的BF16 LoRA指不量化的BF16基座加LoRA混合精度训练，不声称所有可训练分支运算都为BF16。两组使用同一实现。

题序为对4096题训练池按seed作一次确定性shuffle，每个run的100×16预算使用前1600道（run内不重复）；相同seed的STEP/NAME题序逐题相同。4096是可用训练池规模，不将100更新写成完整训练epoch。
