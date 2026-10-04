# 方法与复核入口

本轮范围、选择规则和预算见[运行前登记](REGISTRATION.md)。原实验位于相邻`grpo-binary`与`prompt-only`目录，均只读引用；本轮训练、数据及结果独立保存。

## 固定协议

- Qwen2.5-7B-Instruct：revision `a09a35458c702b33eeacc393d103063234e8bc28`，固定L3/L4/L5。
- Qwen2.5-14B-Instruct：revision `cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8`，固定L5/L6/L7。
- 每组合STEP/NAME、seed301/302/303；每run100更新，16题×8候选。每长度4096训练、256固定验证、512新测试、64独立预检。100更新使用按seed打乱后的1600道训练题，不称作一个完整epoch。
- 保留原九工具、四位数字、给定调用计划、Prompt和例子。STEP只要求`step:`；NAME要求当前工具名称。完整模板在各任务`config/prompt-STEP.txt`、`prompt-NAME.txt`，参考原件归档于`snapshots/reference-inputs`。chat模板来自原始tokenizer配置，其SHA256与下载登记匹配。
- 生成规则：每个工具索引和输入数字独立均匀采样，按调用链+初值去重；训练/验证/测试/预检互斥，并排除登记的29个历史数据来源中的同长度题。L5两个模型的四个集合逐字节相同。示例固定L2，与本轮所有L3–L7不同。

## 训练与奖励

沿用前轮可运行实现：冻结BF16基座，LoRA r16、alpha32、dropout0，作用于q/k/v/o/gate/up/down七投影。LoRA参数、分支计算及优化器状态为FP32，PEFT将分支输出转回基座输出类型；没有量化、额外SFT或旧adapter。不能把它描述为所有运算均BF16。

双卡DDP，microbatch4；采样batch32，temperature1、top_p1、top_k0。AdamW学习率1e-5、5更新线性warmup后恒定，betas(0.9,0.999)、eps1e-8、weight_decay0；梯度范数裁剪1。采用确定性算法、原SDPA与梯度检查点设置。

任务奖励只有严格轨迹0/1：操作序列、所有中间状态及唯一最终Answer都符合历史评分语义才为1。工具/标题合规不加分，不作逐字符奖励；没有前缀或局部步骤奖励。标题归一化后送入历史评分器，标题合规另列。历史评分允许部分一般标题行，并不把“Answer一定是最后一行”的更严格规范额外加为新主评分条件。

每题8个候选，以该组奖励的样本标准差(ddof=1)+1e-4标准化优势。全0或全1组优势为0，仍可能存在KL梯度。优势应用于完整回答的有效输出token；逐回答取有效token平均，再对回答平均。真实EOS计入，prompt与padding排除。单元核验覆盖其实际梯度。

每轮新采样后只做一次optimizer更新（μ=1）。实现的比率前向为1，clip_epsilon0.2不构成实际多轮策略裁剪；不把它宣传为进行了多轮PPO。参考策略为同一冻结基座禁用adapter，KL系数0.04，估计项为`exp(logp_ref-logp)- (logp_ref-logp)-1`。KL是优化正则，不是额外任务部分奖励。

同seed两条件使用同LoRA初始化、题序、有效batch、采样配置和更新数，在同一个物理双卡slot顺序运行。生成轨迹和随机消耗允许不同。实际输出token和GPU计时分别报告，不把相同更新数当相同计算量。

## 预检、冻结和评测

每条件任务先4次预检更新，再由step2恢复至step4。12组恢复后的候选、adapter和优化器状态均一致；adapter最大差为0。每任务另核验128条正确轨迹及每条3种变异、1968条历史输出奖励、优势和mask/EOS梯度。所有正式run从原始起点重新开始；配置在正式训练前统一冻结，没有按NAME领先程度改超参数。

按所有集合的正确目标轨迹预检预算：`ceil((1.25×最大正确目标token+64)/256)×256`；L3/L4上限256，L5/L6/L7上限512，同长度两条件/模型一致，且最大输入+预算不超过32768上下文。没有按正式结果调整上限。少量错误生成触及上限保留为截断。

保存step0/10/…/100的adapter、优化器及两rank RNG；每个固定检查点评测256验证题。原始模型step0每条件任务实际生成一次并供三个seed引用；36个step0 adapter均核验LoRA B全零，因此共享原始策略评测有依据。新测试只在step0及step100各512题，不选最佳checkpoint、不重试择优。全部greedy，eval batch32。

预先固定60%、70%、80%、90%验证门槛，未达到保持未达到。后续组合的初筛只用STEP step100验证三seed均值20%–90%，全六组合保留。这个探索性筛选不构成独立确认。

## 资源与异常记录

本机8卡、两远程各4卡，均为RTX PRO6000 Blackwell Server Edition。正常按小时检查。完整作业记录在`infrastructure`，巡检在`logs/hourly-checks.jsonl`。

正式训练没有OOM、数值故障或中断重启。唯一非零控制器退出是首小时资源重分配时主动停止旧调度器；六个在跑训练不受影响，四个旧评测worker先正常排空退出，再从持久队列恢复调度。`resource-reallocation-v2.json`和`v3.json`分别记录7训练slot/2评测卡及尾段增加2评测卡。冻结训练/评测代码、配置及原始输出均未改变。旧调度器与替代调度器源码均保留。

## 复核已有产物

从项目根目录执行，`GRPO_TASK_ROOT`替换为六任务之一；以下不调用模型生成或启动训练。

```bash
export GRPO_TASK_ROOT="$PWD/workspace/research/B01-02/grpo-length-study/14b-L5"
.analysis-venv/bin/python workspace/research/B01-02/grpo-length-study/postanalysis/analyze_task.py
.analysis-venv/bin/python workspace/research/B01-02/grpo-length-study/postanalysis/report_task.py
.analysis-venv/bin/python workspace/research/B01-02/grpo-length-study/postanalysis/error_details.py
```

六任务分析齐后：`aggregate.py`生成全组报告和图；`audit_data_models.py`核验历史去重及原始模型完整文件哈希；`audit_lifecycle.py`核验冻结/作业/数据与完整占用时间；`cost_and_tokens.py`逐条核验实际输出token、EOS/上限及成本；最后`endpoint_costs.py`添加贪心端点推理成本。

`audit_optimizer.py`用项目`.training-venv`（先`source training-env.sh`）在CPU核验实际step0/100的参数与优化器，不使用GPU。审计结果保存在`analysis/*audit.json`。全套验收与产物清单见[COMPLETION_AUDIT.md](COMPLETION_AUDIT.md)。
