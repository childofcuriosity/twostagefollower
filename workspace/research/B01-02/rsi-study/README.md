# 执行学习与改进能力分离：研究工作区

本轮已完成，等待统一结果审核。先读[结论与推荐](CONCLUSIONS.md)，再看[完整报告](REPORT.md)、[补充控制](SUPPLEMENT.md)和[工作状态](WORK_STATUS.md)。设计依据：[协议](PROTOCOL.md)、[理论与可识别性](MECHANISM.md)、[最近邻](literature/NEAREST.md)。

## 数据和运行

- `data/families.json`：32个独立隐含模式家族，12训练/4开发/16测试，支持集12条、测试64条。精确语义隔离与适用域写在协议中。
- `data/loop-eval-*.json`：两种执行语义下各256条固定评测。短程序、未见家族组合、更长/更难压力集分开。
- `models/`：两个新增模型的固定Hub revision与下载SHA256；原1.5B沿用`../model`。
- `replications/*/runs/`：新模型第一轮设置复核，512步LoRA，包含逐题输出和适配器。
- `runs/robust-*`：三提示、温度与K预算评测，原始提案分组JSONL。
- `runs/loop-*`：三轮参数更新，轮0–3的检查点、执行输出、提案、训练样本与损失。
- `runs/branch-*`：同一shared轮1起点，更新/冻结提案源的128步分支。
- `runs/gradient-*`：只读梯度对齐诊断，不更新参数。
- `analysis/`：登记、修订、结果、统计和完整性审计。
- `figures/`：六组PNG/SVG/PDF图，包含所有seed及主要区间。

## 环境与命令

所有命令在项目根目录执行。训练环境沿用`.training-venv`，分析绘图在独立`.analysis-venv`；缓存、临时文件和代理由`source training-env.sh`设置，不更改全局环境。

```bash
source training-env.sh
python workspace/research/B01-02/rsi-study/src/analyze_robust.py
python workspace/research/B01-02/rsi-study/src/analyze_loops.py
python workspace/research/B01-02/rsi-study/src/verify.py
.analysis-venv/bin/python workspace/research/B01-02/rsi-study/src/plots.py
```

所有训练与诊断启动器均已完成，不要重复启动。单任务入口如`src/loop.py --domain digits --condition shared --seed 11`会拒绝覆盖已有目录；复现应使用新研究目录或新的运行ID，不能删除现有证据。

依赖：根目录`training-requirements.lock.txt`及本目录`analysis-requirements.lock.txt`。模型新下载使用标准库和curl，不增加训练依赖。

完整分析顺序见`src/finish.py`；报告生成后运行`src/supplements.py`，结论审核文档独立保留。`analysis/final-artifacts.json`记录最终交付文件哈希；原始训练审计见`analysis/verification.json`。本次10个阶段全部完成，没有遗留GPU作业。
