# 复现与资源口径

本轮只使用已有项目训练/分析环境与本机PRO6000。逐run config.json、driver_snapshot.py、train.jsonl、模型适配器和输出均保留在runs。analysis/preflight.json及baseline-freeze.json记录数据/原源码/旧输出哈希，analysis/launch.json记录生成包装器版本；大模型初始adapter与原同seed初始adapter逐文件hash核验。

正常运行检查频率一小时一次，进程完成事件自动衔接，不按分钟扫描GPU。失败日志若有会保留，不覆盖重跑。源码调用目标构造函数以外的训练算法沿原文件，具体diff见TRAINER_DIFF.md。

|模型|新作业数|单GPU进程墙钟合计小时|
|---|---:|---:|
|qwen1.5b|6|0.65|
|qwen3b|6|1.01|
|qwen7b|6|4.41|
|qwen32b|6|15.91|

合计21.98 GPU小时。含模型加载、训练、开发集/正式推理，不等于GPU内核活跃时间或纯训练时间，不包含旧基准的历史训练成本。

在项目根目录，完成后可重新做离线评分/统计（会刷新派生报告，不重训或覆盖原始输出）：

```bash
source training-env.sh
python workspace/research/B01-02/label-controls/src/analyze.py
```

新训练使用worker.py --job INDEX，配置来自analysis/jobs.json，调度记录见analysis/dispatch.json。worker拒绝覆盖已有run；需要真正重做时应先建立独立的同层实验目录并保留原始记录，不直接删除现有runs。完整基座与旧控制组依赖原项目路径，本目录不是脱离项目即可独立运行的软件包。
