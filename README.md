# stepname

研究多步执行任务中，输出当前工具名称是否有助于模型学习和完整执行。本仓库是研究工作区的**源码与报告归档**，保留实验之间的原有相对路径；不是包含全部训练权重、逐题轨迹和运行环境的完整备份。

## 当前主要问题

受控任务给出四位数字、九种工具的定义和正确调用顺序，模型需要展开操作、计算中间状态并输出答案。STEP 条件在每次调用前使用统一的 `step:` 标签；NAME 条件使用当前工具名称。正确顺序已经给定，因此该实验主要检验执行学习，不等同于开放环境中的自主规划。

研究从执行能力与提案能力的比较，发展到模型规模、分开训练与组合、标签对照，以及二值奖励 GRPO 训练。历史真实 Agent 实验也保留在独立目录中，不能把受控数字任务的结果直接视为真实 Agent 迁移结果。

## 最新结果：GRPO 长度扩展

2026-09-29 完成 7B L3/L4/L5、14B L5/L6/L7 共六个组合；每个组合包含 STEP/NAME 与三个配对随机种子，共 36 次正式训练，每次 100 次更新。L 表示依次调用的工具数量。奖励为整条执行轨迹是否完全正确。

| 组合 | STEP 测试成功率 | NAME 测试成功率 |
|---|---:|---:|
| 7B L3 | 8.27% | 32.75% |
| 7B L4 | 0.91% | 4.17% |
| 7B L5 | 0.00% | 0.85% |
| 14B L5 | 32.94% | 70.77% |
| 14B L6 | 4.56% | 38.74% |
| 14B L7 | 0.72% | 7.29% |

表中为三个种子的均值，每组使用 512 道新测试题。14B L5 是唯一符合预先登记的 STEP 验证成功率 20%–90% 窗口的组合；NAME−STEP 的配对测试差均值为 37.83 个百分点。两组原模型提示词起点不同，学习增益之差为 32.75 个百分点。7B L5 未观察到学习改善；三种子仍属初步重复，不能据此断言普遍因果机制、创新性或真实 Agent 泛化。

主要入口：[最新结论](workspace/research/B01-02/grpo-length-study/CONCLUSIONS.md)、[完整报告](workspace/research/B01-02/grpo-length-study/REPORT.md)、[方法](workspace/research/B01-02/grpo-length-study/METHOD.md)、[审计](workspace/research/B01-02/grpo-length-study/COMPLETION_AUDIT.md)。历史报告中“已完成”“原始数据在本目录”等措辞描述原实验工作区，不表示所有证据文件都包含在此归档中。

## 实验地图

所有路径均位于 `workspace/research/B01-02/`。

| 目录 | 内容 |
|---|---|
| `src/`、根目录 `PROTOCOL.md` / `REPORT.md` | 原始任务与实验 |
| `followup/`、`rsi-study/` | 执行与提案能力、闭环研究历史 |
| `agent-completion-plan/` | 长任务完成率研究计划 |
| `scale-study/` | 模型规模与标签实验 |
| `agent-study/`、`agent-study-v3/`、`agent-reliability/` | 真实 Agent 与工具协议可靠性探索 |
| `oracle-study/`、`stability-study/` | 顺序和操作分开学习、组合与稳定性 |
| `label-controls/`、`label-seed-replication/` | 标签位置、改名和种子复核 |
| `prompt-only/`、`prompt-only-length-short-20260929/` | 纯提示词与短测探索 |
| `grpo-binary/` | 固定长度二值奖励 GRPO |
| `grpo-length-study/` | 最新六组合长度扩展 |
| `qwen05b-fixedlength/`、`qwen05b-indomain/` | 早期小模型对照 |

初始候选与文献记录见 [candidates.md](workspace/research/2026-09-23-batch01/candidates.md) 和 [sources.md](workspace/research/2026-09-23-batch01/sources.md)。旧状态文件保留为历史材料；当前结论优先查阅各实验的结论、方法和完成审计。

## 使用与复现限制

- 根目录 `training-requirements.in` 与 `training-requirements.lock.txt` 保存原训练依赖记录。请在适合自己硬件的独立 Python/CUDA 环境中安装；锁定文件是原环境记录，不保证在任意平台可直接安装。
- 保留 `workspace/research/B01-02/` 层级：部分实验通过相邻目录导入任务、解析器和评估代码。先阅读对应 `METHOD.md`、`REGISTRATION.md`、`PROTOCOL.md` 或复现文档，再运行相应 `src/` 脚本。
- 未运行新训练，也未重构归档源码。部分脚本保留原本的本地绝对路径、GPU 拓扑、模型目录和远程调度假设；它们需要按自己的环境配置。远程工具引用的私有服务器配置未提供。不要直接启动历史调度脚本。
- 全量权重、检查点、逐题数据、候选输出、日志、运行时、服务器基础设施及私有配置未上传。部分报告链接指向这些未归档产物，无法仅凭本仓库重新完成全量原始证据审计。需要重新生成数据、获取模型并按协议运行，或另行取得对应原始产物。
- 小规模汇总 JSON/CSV、实验配置、源码与报告图用于理解结果；它们不能替代完整原始轨迹。自动扫描只用于发现常见凭据形态，不构成代码正确性或可复现性验证。

[ARCHIVE_MANIFEST.json](ARCHIVE_MANIFEST.json) 记录所选文件、大小、SHA-256 及归档改动。原工作区文件保持不变。没有添加未经确认的开源许可证。
