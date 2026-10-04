# 完成核验

主矩阵109824条（新增102624、复用7200），操作上下文16896条，新程序确认9600条，合计136320条正式覆盖。不是136320个独立题目。当前两轮校准320条原始轨迹、首次归档校准80条另存，不计正式样本。

- 主矩阵：analysis/completion-audit.json，analysis/formal-source-freeze.json，analysis/adapter-hashes.json。
- 操作上下文：context-intervention/analysis/completion-audit.json，实际生成输入逐条重建；新评测器完整历史模式在两个尺度各40题与旧评测器逐条一致。
- 新程序确认：fresh-confirmation/analysis/completion-audit.json，9600条、99481生成事件，明确no_oracle_inputs与actual_generation_contexts_reconstructed均为true。
- 完整分析组装：analysis/final-analysis-complete.json；人工复核最终图、统计口径、固定抽样成功/失败案例及宽松评分敏感性；补齐144格子任务表和16组事后函数范围诊断。
- 所有失败校准和硬件差异保留。3B在本机统一重评，避免把5090与PRO6000数值差异混入方法比较。原始来源及token hash可追溯。
- 资源账见RESOURCE_ACCOUNTING.md：78个已结束评测/校准作业，31.62分配GPU小时（含加载等墙钟时间）；本轮无新增训练。最终三阶段调度/分析进程已退出，现场8卡均无显存占用。未重新使用已交还远程机器。

完成的是当前获准的稳定性研究及登记跟进；不代表未验证的现实Agent/RSI总体目标已完成。最终判断见CONCLUSIONS.md。
