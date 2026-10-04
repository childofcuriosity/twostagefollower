# 第二阶段完成验收

2026-09-25，本轮批准的oracle训练与消融已经完成。验收范围是四尺度、三个训练条件、三个seed、匹配oracle推理对照与完整分析；不是宣告真实Agent/RSI研究整体完成，也不是证明某个机制必须成立。

|验收项|实际证据|结论|
|---|---|---|
|36项正式训练|全部512步、16384样本；四个中间适配器及最终适配器存在；loss/梯度有限；监督token数逐项与登记mask一致|通过|
|60个检查点/模式组合|每个560原测试+480独立确认，ID、输入和工具链逐条对齐；合计62400|通过|
|独立评分|另写基本操作/状态转换与来源检查，重新验算全部62400条，与原评分一致；原文件SHA256已存|通过|
|人工/模型token衔接|全部正式事件逐token解码、重建上下文，前缀长度/hash一致；人工片段重新编码一致|通过|
|训练mask与参考解|四尺度各4096训练题的来源与loss mask检查，1040测试参考解检查；两个专用mask分割联合监督|通过|
|交接器错误注入|10项，包含错误名称不纠正、错误数字传递、缺边界失败、批量异步结束|通过|
|正确答案不被预算截断|四尺度各5136参考轨迹的分段/整体编码一致；最大header/body/输出/总上下文分别2/33/282/412 token|通过|
|新进程模型复跑|各尺度seed11联合检查点，40输入×3模式；四尺度480条完整记录完全一致|通过，限固定原batch|
|输入和模型配置未漂移|数据、模型配置/tokenizer/下载manifest哈希与权重文件大小核查；推理与协议源码哈希对齐所有正式run|通过；未全量重算基座权重hash|
|配对统计与报告|104个同环境对比单元、20个模型/长度乘积单元、全量失败分类、逐seed差、bootstrap和固定随机badcase|完成|
|资源释放|六台5090此前已核查释放；本机8卡显存0 MiB，无本研究训练、评测、复跑或watch进程|完成|

机器可读验收：analysis/completion-audit.json。原始评分验算：analysis/results-audit.json。token重放：analysis/token-replay.json。最后命令记录：analysis/final-audit-steps.json与logs/final-audit.log。可复现步骤：[METHOD_AND_REPRODUCTION.md](METHOD_AND_REPRODUCTION.md)。

## 异常、修复和解释边界

- 正式36项作业全部正常退出，无失败seed被丢弃或重试替换。32B最后一项从排队改为外部空闲GPU训练，原队列只接管评测；训练main函数AST不变。租约及验收见analysis/external-adoption-complete.json、handoff-source-check.json和adoption-preflight.json。
- 全部训练评测结束后，停止只负责每15分钟轮询的睡眠watcher，改由当前进程立即执行最终全套审计。没有停止训练或评测；记录在analysis/supervisor-manual-handoff.json。
- 最终绘图首次因训练环境没有matplotlib失败，随后使用已有项目分析环境成功渲染PNG/SVG/PDF，未修改训练环境。分析环境没有pip，包版本清单改由importlib.metadata读取。最终绘图环境见infrastructure/plotting-environment.json；图像已人工视觉检查。此类交付辅助错误没有改变任何实验输入、原始输出或评分。
- 24,960条同检查点oracle干预配对中有19条在相同token前缀下提前出现模型输出差异，集中在小模型；不宣称它们是干净的token干预。全部列在analysis/intervention-pairs.json的exceptions；固定batch复跑通过不等于跨batch不变。排除异常的敏感性分析不改变主表分母，详见CONCLUSIONS.md。
- 专用训练与联合训练的监督token量、结束token监督及梯度权重不相同。结果是目标mask干预的实测效果，不能据此唯一认定内部独立学习机制。均值收益有seed异质性；不同模型有反向结果，全部保留。

原始62,400条结果及480条复跑记录均已保留。成本总计约22.76单GPU进程小时，含导入/加载/保存和校准/复跑，跨两类GPU，复跑部分按完成文件时间估算；不是纯GPU kernel活跃时间。详细口径为analysis/cost-total.json；不把原队列等待外部训练的CPU时间重复算成GPU训练。

最终研究判断见[CONCLUSIONS.md](CONCLUSIONS.md)。本轮第二阶段要求的实施、运行、对照、审计、解释和交付无待办；新增机制实验与真实Agent迁移是后续研究议题，未虚报为已完成。
