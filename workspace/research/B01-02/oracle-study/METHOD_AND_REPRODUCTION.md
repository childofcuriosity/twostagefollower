# 第二阶段具体做法与复现入口

本轮只回答原玩具任务的oracle消融问题：把“名称序列”和“工具内部展开”分别作为监督目标，能否分别学会、与联合训练有何差异。模型是Qwen2.5 Base 1.5B、3B、7B、32B，采用LoRA监督微调，没有Agentic RL，也没有让模型在线创造新工具。本轮由本目录脚本直接训练评测。

## 题目与两个子任务

输入是四个数字和一个已给定顺序的工具名称列表，要求从左到右执行。9个固定工具各包含2或3条基本操作；基本操作有6种，其中这套库实际用到5种。输入提供基本操作说明，不逐题提供工具定义；名称对应的固定展开从训练样本学习。**顺序任务A是按输入复述完整名称列表并在正确位置结束，不是从目标推导计划。** 展开任务B要求所有规定工具的操作行、数字和工具结束位置全部正确。

例如输入数字`1 2 3 4`，工具为`red black`，正确输出为：

```text
red:
rot 2 3 4 1
inc 3 4 5 2
EndTool
black:
inc 4 5 6 3
swap 5 4 6 3
EndTool
Done
```

三个训练条件看到完全相同的正确文本，区别在loss：

|条件|模型学习预测|程序在oracle推理时提供|
|---|---|---|
|joint 联合训练|名称、操作、EndTool、Done|无|
|order_oracle 展开专用训练|操作和EndTool|每个正确名称，以及整条任务的Done|
|operation_oracle 顺序专用训练|名称和Done|模型实际选中工具的操作及EndTool|

顺序专用模型选错工具时，程序执行那个错误工具，不改成参考答案；提前Done也直接记错。展开专用模型虽然得到正确名称，仍能遗漏操作、写错数字、过早EndTool或超预算。错误数字能解析时会原样进入后续状态。所有人工片段训练label为`-100`，并逐token检查来源边界；它们作为上下文供之后的模型token使用，不计作模型预测正确。

程序/模型轮流输出时，从保存的完整token历史重新调用模型。每次记录实际token ID、来源、前缀长度与SHA256；没有跨人工插入片段复用旧KV缓存。结束由显式换行/EndTool/Done识别，不能按参考答案的操作行数截断。16工具上限只是防跑飞，不替模型决定正确长度。四个tokenizer各5136条参考轨迹已检查分段/整体编码一致；参考header最长2 token、body最长33 token、整条输出最长282 token、含输入最长412 token，分别低于24/128/2048/4096限制。具体预算见REGISTRATION.md。

## 数据、训练与配对比较

训练4096题，394题单工具、3702题双工具，90种程序，四轮共16384样本、512优化步。没有在长调用测试上训练。原测试560题包含128同分布、384未见长组合、48压力题；另有480条此前固定的独立确认输入，3/4/5/6/8工具各24程序×4输入。这些测试输入与训练输入无完全重复，长程序与训练程序也不重合。独立确认集不是本轮结果出来后新建的盲测集；只是与原训练/测试输入分离的固定集合。逐项交叉检查见analysis/data-audit.json。

每尺度×3训练条件×seed11/22/33，共36项训练。每个joint检查点除自主推理外，再接受两种oracle帮助；两个专用检查点各测对应oracle环境。共60个检查点/推理模式组合，每个1040题，合计62400条正式轨迹。每长度的288条计数是96输入在3个训练seed上的输出，不是288个独立程序。

主检查点事先固定step512，step64/128/256也保留；未按测试表现选检查点。所有条件相同输入、次序、batch与训练步数，但监督token量不同。每四轮联合监督1,001,552 token，展开监督890,016 token，顺序监督111,536 token。因此这是目标mask干预，不能同时声称隔离了监督量、loss权重、梯度干扰或显式模块化结构的效果。

关键训练比较是“专用检查点+oracle”对“联合检查点+同一种oracle”，把推理时得到的帮助控制住。关键推理比较是“同一联合检查点+oracle”对“同一检查点自主执行”。专用oracle成绩直接与联合自主成绩相减同时改了训练和推理，不是单因素因果比较。

## 乘积应该怎样理解

同一个联合模型的完整正确事件可以分为A和B，其概率恒等于`P(A) × P(B|A)`。用`P(A) × P(B)`代替需要额外的统计独立假设。

本轮专用模型的A、B来自两个不同检查点、两个oracle推理环境。记录同一题上两个oracle任务是否都正确，再与各seed的边际概率乘积比较，可以检查这些**测试输出**的相关性；不能证明联合模型内部真的分成两个独立模块。也不能把乘积与联合自主准确率的差全部归为相关性，因为训练目标和推理环境已变。两专用模型的同题均对统计不是实际运行双模型组合Agent，后者本轮没有测试。

## 环境与证据复现

所有环境、缓存、数据、适配器和日志在本项目。小模型在六台8×5090服务器运行，32B在本机PRO6000 96GB运行；同尺度比较使用同类硬件。远程服务器已交还，不应照旧调度文件再次连接。台账见infrastructure/SERVERS.md；凭据与研究产物隔离，不在公开文档列出。

共同环境为Python3.12.3、torch2.7.1+cu128、transformers4.51.3、peft0.15.2、accelerate1.6.0、numpy2.2.6。完整配置在每run的config.json；训练曲线train.jsonl；适配器adapter/与checkpoints/；原始推理evaluation-*.jsonl；训练/评测完成摘要training-complete.json与evaluation-complete.json。环境包清单与hash见infrastructure/；输入、模型配置、tokenizer与权重文件清单见analysis/reproducibility-inputs.json。模型权重文件记录大小和下载manifest，未另外重算所有大权重文件的SHA256。

在项目根目录可重新执行只读结果验算并刷新派生报告：

```bash
source training-env.sh
python workspace/research/B01-02/oracle-study/src/data_audit.py
python workspace/research/B01-02/oracle-study/src/reference_budget_audit.py
python workspace/research/B01-02/oracle-study/src/audit_results.py
python workspace/research/B01-02/oracle-study/src/token_replay.py
python workspace/research/B01-02/oracle-study/src/diagnostics.py
python workspace/research/B01-02/oracle-study/src/compare.py
python workspace/research/B01-02/oracle-study/src/products.py
python workspace/research/B01-02/oracle-study/src/product_uncertainty.py
python workspace/research/B01-02/oracle-study/src/mechanisms.py
python workspace/research/B01-02/oracle-study/src/intervention_pairs.py
python workspace/research/B01-02/oracle-study/src/report.py
.analysis-venv/bin/python workspace/research/B01-02/oracle-study/src/plots.py
python workspace/research/B01-02/oracle-study/src/completion_audit.py
```

这些脚本不重训、不覆盖原始输出。绘图使用已有项目`.analysis-venv`的matplotlib3.10.1；训练环境未为绘图改动。模型新进程复跑使用src/reproduce.py，每尺度固定120条、保持原batch组合；记录见analysis/reproduction/。训练脚本与复跑脚本拒绝覆盖已存在的输出目录；若重做训练应在新的实验目录建立独立run，不删除本轮原始结果。完整启动参数与分配见infrastructure/allocation.json和logs/。

唯一正式调度变更为把原排队的32B顺序专用seed33提前放到空闲GPU2训练，原队列等待它完成后负责评测。main训练函数AST保持一致，数据、超参、推理与评分不变；租约、旧源码、错误路径检查均有记录。其他后增脚本均为离线分析，不改正式输出。
