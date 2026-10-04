# 扩展研究已完成，等待统一结果审核

2026-09-24。用户“做深做大”的本轮授权工作已完成；结论入口[CONCLUSIONS.md](CONCLUSIONS.md)，全部结果[REPORT.md](REPORT.md)，补充控制[SUPPLEMENT.md](SUPPLEMENT.md)。不自动扩大到其他候选或发布论文。

10个阶段全部完成：replications、robust、loops、branches、gradients、coverage、length、legacy、timecourse、original-gradients。24条三轮闭环、18条同起点分支、三个模型、两种执行语义；补充控制明确标为事后实验。各阶段完成标记在analysis/，总流水线日志为根目录logs/training/rsi-finish-v3.log。

审计通过：50,464条执行记录、180,864条提案、150个适配器哈希；回放/打乱回放辅助token匹配，分支起点一致，三个原配方重跑最终权重精确一致。六组图已生成并检查代表性图形。最终交付哈希另存analysis/final-artifacts.json，保留原始verification.json不覆盖。

核心判断：原配方的执行/提案分离稳健，但新闭环不退化；主因果分支区间跨零，外部退化提案者的数字压力结果方向一致但不确定，字符串未复现。因此不宣称普遍RSI瓶颈或可靠修复机制。下一步建议受控因素拆分及独立代码任务上的真实学习增益检验，详见结论，不继续盲目扩大toy训练。

所有环境与资产在当前项目目录。长任务低频检查偏好继续有效。未发布、未上传研究结果。
