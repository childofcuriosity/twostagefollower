# 完成审计

2026-09-28。按COMPLETION_REQUIREMENTS.md逐项验收，结论：本轮限定Goal已完成。不是方法有效性的预先承诺。

| 要求 | 权威证据与核验 | 结果 |
|---|---|---|
| 原始模型、无adapter、不改旧训练实验 | models/qwen7b及qwen14b/download-manifest.json；worker.py直接AutoModelForCausalLM加载原始目录，未调用训练或PEFT；旧dsl及评分器SHA保持一致；本轮写入限prompt-only及顶层交接文档 | 通过 |
| 7B起步与授权备选 | 7B七档448条探索全保留；L2 STEP3/32、L5 0/32；analysis/precheck-diagnosis.json和fallback-decision.json；14B完整重复流程 | 通过 |
| 四组Prompt与统一示例 | analysis/method-audit.json逐字规范化核验；两模型四模板完全一致；ALIAS映射匹配旧正式清单；analysis/rendered-precheck-STEP.txt记录真实chat系统前缀 | 通过 |
| 探索及选长 | 两模型每档32题、STEP/NAME，每模型448条；fallback14/analysis/length-selection.json只读STEP；仅L2满足区间；无补测触发 | 通过；按规则一档而非强凑两档 |
| 新题与分片一次生成 | fallback14/analysis/completion-audit.json核验预检12、探索224、正式512和示例的底层题零重叠；final-research-audit.json核验四组同题、8份256题分片不重叠且合并无增删 | 通过，2,048条正式输出 |
| 正式冻结 | fallback14/data/formal-L2-manifest.json于00:36:17 UTC写入；早于全部8个running.json.start；源码及frozen-source逐文件哈希相同；各worker持有相同manifest哈希 | 通过 |
| 解码与容量 | 每分片generation-config.json：do_sample=false，num_beams=1，repetition_penalty=1；四组256上限；正确目标最高78、输入最高493，小于32768上下文；token IDs、解码文本和EOS逐题核验 | 通过 |
| 严格评分、配对统计 | 原评分器与独立轨迹比较一致；3040条再次评分；正式raw/graded逐题一致；scores-formal-L2.json给出各组差、10,000次配对bootstrap区间及discordant数；未将重复greedy当seed | 通过 |
| 错误与标题、停止原因 | analysis/formal-errors-reviewed.json及逐题文件；标题符合单列；all-stop-reasons.json：正式2048EOS；探索7B3条、14B10条length；预检全EOS | 通过，含显式分析修正 |
| 错误分类修正保留 | 初版将额外原始操作混作增加调用、将空Trace:混作调用段；postanalysis/error_review.py修正99条辅助标签；原标签、原分数与原始输出不动；error-review-validation.json的7种定向案例通过 | 通过；非结果驱动的推理条件更改 |
| 成本 | final-research-audit.json成本由逐批GPU同步generate时间及调度外层时长求和；正式0.198分配GPU小时、全轮1.046；报告区分并行墙钟、分配时间与内核活跃时间 | 通过 |
| 资源及异常 | 60个调度作业全部returncode0，失败记录空；仅本机8卡，正式四组各分两片同时运行；每阶段均不足1小时；完成后nvidia-smi八卡0MiB、0%，进程检查无worker/dispatch/pipeline/download残留 | 通过 |
| 最终交付及边界 | 顶层REPORT.md直接回答主比较、有效长度/错误和成本；7B_EXPLORATION.md；Prompt、配置、原始数据/输出、旧/复核评分全保留；未启动独立跨模型确认、真实任务或对外发布 | 通过 |

## 审计执行入口

- 主流程：`fallback14/src/report.py`（生成阶段审计；重跑会重建初版自动报告，顶层正式报告另存）。
- 研究复核：`postanalysis/final_audit.py`，结果`analysis/final-research-audit.json`。
- 辅助错误口径复核：`postanalysis/error_review.py`，结果`analysis/formal-errors-reviewed.json`与`graded-formal-errors-reviewed.jsonl`。
- 定向原始操作、正确/错误轨迹测试：`analysis/implementation-validation.json`、`fallback14/analysis/implementation-validation.json`和`analysis/error-review-validation.json`。

证据支持的结论：14B L2的NAME−STEP为−0.78个百分点，95%区间跨0；ALIAS有辅助阳性，但同步改输入输出存在归因边界。本轮没有建立纯Prompt原名复述的有效长度，也没有否定所有可能Prompt与任务上的收益。
