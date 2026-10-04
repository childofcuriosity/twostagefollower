> 最新：位置/固定改名两新增条件已完成，四尺度×三seed。见[label-controls最终结论](label-controls/CONCLUSIONS.md)与[完成审计](label-controls/COMPLETION_AUDIT.md)。以下旧阶段记录保留为历史背景。

# B01-02 工作区

正在推进：[RSI扩展研究协议](rsi-study/PROTOCOL.md)，阶段进度见[rsi-study/WORK_STATUS.md](rsi-study/WORK_STATUS.md)。用户已授权多模型、闭环及因果干预实验。

最新：用户授权的[后续提案效用实验](followup/REPORT.md)已完成，揭示执行训练后提案弱于冻结基座；原始第一轮报告保持不变。

本轮理论和实验已完成，等待统一结果审核。首先阅读[结果报告](REPORT.md)。全部文件留在当前项目目录。

完成30次正式训练、1次校准、2个冻结基线及7个路由诊断；第二环境位于`secondary/`。报告区分事前主实验与事后诊断。

- `MECHANISM.md`：理论推导、可识别性、混淆与结论边界。
- `PROTOCOL.md`：实验前协议与通过/放弃标准。
- `src/`：下载、模型真实提案、验证器、数据、训练、评估和分析代码。
- `data/`：真实提案与轨迹、抽象库、隔离数据、审计与哈希。
- `runs/`：按条件/种子/世界保存checkpoint、训练日志和逐题输出。
- `analysis/`：协议哈希、修订、作业状态和最终统计。
- `model/`：固定revision的原始模型和下载哈希。

项目根目录的`training-env.sh`设置项目内全部缓存与公司代理；`install-training-env.sh`重建独立`.training-venv`。不依赖修改系统torch/transformers。

运行程序前在根目录执行：

```bash
source ./training-env.sh
```

按顺序运行`src/download_model.py`、`src/discover.py`、`src/build_data.py`。训练校准使用`src/run.py --condition flat --steps 20 --calibrate`。正式作业由`src/launch_suite.py`调度独立GPU进程，不是多卡NCCL训练；固定最终步数记录在校准决策文件中。`src/analyze.py`只分析已完成作业，不把缺失结果当零分。
