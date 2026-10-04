# 第一阶段交付验收

审核依据：当前goal、`../agent-completion-plan/SCALE_AMENDMENT.md`及用户关于工作目录、低频检查、全部失败保留和服务器使用的指令。此验收只覆盖已批准第一阶段；不把真实Agent实验或新机制组算作已完成。

| 要求 | 实际证据与范围 | 结论 |
|---|---|---|
| 固定32B模型并完整下载 | `models/qwen32b/download-manifest.json`固定revision 1818d35814b8319459f4bd55ed1ac8709630f003，逐文件SHA；`analysis/qwen32b-remote-hash-audit.json`核对17权重分片 | 完成 |
| 7B同系列参照和Instruct桥接固定模型 | 各自models目录的download-manifest；revision d149729398750b98c0af14eb82c78cfe92750796、5ede1c97bbab6ce5cda5812749b4c0bdf79b18dd | 完成 |
| 实测显存、吞吐再正式训练 | `analysis/qwen7b-calibration.json`、`qwen32b-calibration.json`及runs probe summary；32B micro16有效batch32可运行；报告含实测数值 | 完成 |
| 7B/32B各flat/macro三seed512步 | 两个`*-completed.json`各6项returncode0；verify检查每步连续、数值有限、累计16384样例 | 完成 |
| 原1.5B/3B全量比较 | 原始24组主测试×560条=13440；来源路径/hash见results和verification；没有仅挑macro对flat错 | 完成 |
| 相同数据、训练剂量和token配对 | 登记数据hash未变；token审计4096题逐题相同；12新增主训练计数配对；梯度检查点保持micro16 | 完成，等步数不等FLOPs或LoRA比例 |
| 全部固定检查点0/16/64/128/256/512 | 12组×6中途适配器，加最终副本共84文件哈希；最终副本等于step512；各步全560题测试、三seed齐全 | 完成 |
| 短题/长题/轨迹/停止曲线 | results.curves有180个split检查点记录，最终512取主结果；learning-curves.png/svg/pdf；段数分布CSV | 完成 |
| 开发掌握匹配 | 72个开发文件、9216短题输出；90/95/99%全部敏感性与选中测试已齐，无missing；不读取测试选点 | 探索性完成；原计划遗漏数值阈值，无法声称预注册 |
| 各尺度给定义冻结基线 | 独立确认4个模型各480题冻结，统一原始文本提示+完整工具定义；7/32另有原560题冻结；Instruct另有官方chat冻结 | 完成；当前协议未建立冻结初始长执行能力 |
| 同提示训练前后比较 | matched-context.json核对26880条重复测量，7/32分别给定义/不给定义、原题ID和输入一致；六份冻结输出逐字一致 | 完成；重复冻结输出不算独立seed |
| 学习率和Instruct补充 | 3B/32B低LR各6组，32B-Instruct6组，共18训练；21280原始输出、126适配器哈希、完整训练步和计数核验 | 完成；3B硬件混淆明示 |
| 独立模板留出确认 | 480题、120个精确不同仿射程序；登记SHA；4模型各7轮=13440条；完整题目覆盖和来源哈希 | 完成 |
| 原始行为、局部错误和格式归因 | audit逐条重算真值、每个报告状态与操作、严格答案、格式、多答案、正确前缀与两工具停止；补充宽口径、段数分布 | 完成；指标有重叠，不冒充互斥因果分解 |
| 等价轨迹与偶然正确 | outcome-diagnostics审计48160条最终主/独立/补充输出；仿射签名精确判断全输入等价 | 完成 |
| 停止原因与生成上限 | 原始非EOS token数、上限、eos-before-cap推断/边界不确定/达到上限分类保留 | 完成记录审计；历史输出没有最终token ID，不能补造直接stop reason |
| 配对seed和程序不确定性 | paired-inference及extended-results：逐seed差、三seed t区间、按完整程序聚类bootstrap；区间口径清楚 | 完成；不将重复输入当独立模板 |
| 完整原始输出验收 | verification.json核对174文件、95200条：13440主最终+47040检查点/定义+13440独立+21280补充；逐题ID/输入/split/计算/hash全部核对 | 通过；matched-context为重审，不重复计入 |
| 图与报告可审核 | REPORT、CONCLUSIONS、SUPPLEMENT、STOPPING_DIAGNOSTICS；3图组PNG/SVG/PDF已目视检查，无标签遮挡，数量与统计匹配 | 完成 |
| 失败与复现材料 | microbatch-check失败保留；checkpointing-check成功；TLS/启动历史日志、5090跨卡8题一致性未通过记录未混入主结果；src、锁定环境、数据、权重、全部adapter保留 | 完成 |
| 所有环境在本目录、正常长任务低频检查 | 项目内.venv/.training-venv/.analysis-venv/.cache/.runtime、training-env；远程使用同共享目录；正常检查约15分钟 | 遵守 |
| 资源收尾 | 本机与两台PRO服务器最终compute-app查询为空，无scale-study Python任务；5090已交还且未再访问 | 完成，未关闭用户服务器 |

## 审核判断

结果支持“规模缓解固定两工具停止，但工具身份标签的长组合准确率收益在32B仍存在”。不支持把所有收益都归因于减少正确前缀提前回答，也没有证明原有长执行能力被微调破坏。预登记阈值遗漏和历史停止token不可恢复已作为明确限制保留，不用事后分析冒充原协议成功。

真实Agent应用、动态工具重命名、序号/剩余步骤和无关同长度标签控制属于下一阶段建议，等待用户结果审核。当前交付不宣称这些实验已做，也未擅自启动。
