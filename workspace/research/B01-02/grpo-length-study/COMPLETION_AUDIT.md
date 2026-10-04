# 完成审计

结论：用户指定的六个模型/长度组合、36个正式run及全部预定评测、分析已完成。未缩减低分组，未追加模型、长度、seed、局部奖励或真实任务。本轮得到正负结果，完成不以正结果为条件。

| 要求 | 当前实物证据与核验结果 |
|---|---|
| 7B L3/L4/L5，14B L5/L6/L7，仅STEP/NAME×3seed | 六任务配置、18个配对作业exit0；36个run完成记录，各100更新。 |
| 原始Instruct权重及固定revision，无SFT/旧adapter | [原模型与数据审计](analysis/data-model-final-audit.json)：7B的13文件、14B的17文件全部大小和SHA256匹配原下载登记；revision与六冻结配置一致。 |
| 真正从原起点开始，配对初始化 | [优化器审计](analysis/optimizer-audit.json)：36个step0的LoRA B全零、优化器状态为空；任务分析核验同seed两组初始化哈希一致，正式resume均为空。 |
| 原九工具、四位输入、原Prompt/例子/chat/严格评分 | 模板在六任务config中；原Prompt、DSL、工具库、评分器归档于snapshots/reference-inputs；[生命周期审计](analysis/lifecycle-audit.json)核验原件及快照哈希。tokenizer全部原文件哈希匹配。评分语义边界在[METHOD.md](METHOD.md)明确。 |
| 4096训练/256验证/512新测试/64预检，分组及历史去重 | [原模型与数据审计](analysis/data-model-final-audit.json)逐条重建29个历史来源的调用链+初值集合，核验各集合内部唯一、集合之间及与旧题互斥；L5两模型数据逐字节一致。 |
| 同seed题序、16题×8候选、有效batch和采样预算一致 | 六任务analysis/results.json逐update/rank核验实际候选题目ID与固定order-s*.json一致，每更新128候选。配置继承审计与冻结配置确认除指定模型/长度/生成上限及元数据外沿用旧超参数。 |
| 只有完整轨迹0/1任务奖励，标题独立，无局部奖励 | 每任务implementation-tests.json：128正确轨迹及每条3变异、1968历史输出奖励精确一致；全部460800正式候选和119808实际评测重新评分，保存分数与重算一致。 |
| 整回答优势、prompt/padding无策略梯度、EOS有效 | 单元核验优势、mask、真实EOS梯度及逐回答均值聚合；实际候选优势逐条与同题8奖励重算匹配。[token审计](analysis/cost-and-token-audit.json)核验所有output_ids长度、EOS位置和截断上限，与loss记录token总数一致。 |
| 预检、冻结、恢复可用，配置不按NAME收益选择 | 12组预检原始4更新及step2→4恢复，候选一致、adapter最大差0、优化器状态精确一致；全部测试通过后统一冻结。正式作业启动时间均晚于冻结时间。 |
| 100次真实更新，数值正常 | 36个run的两rank日志均完整1…100；小时健康记录未见非有限值。优化器端点全部参数状态step=100，adapter/优化器张量全部有限、LoRA为FP32。 |
| step0/10/…/100 checkpoint含可恢复状态 | 396个固定checkpoint：adapter文件哈希、更新数、配置哈希核验，两rank RNG与优化器均存在；12组独立恢复预检证明恢复路径可用。 |
| 固定验证全曲线；测试只step0/100，无择优端点 | 每任务280评测分片，全组1680；所有测试元数据step仅0/100。原始step0每条件任务生成一次供三个seed引用，36个零增量adapter支持此复用。实际输出119808，未把引用冒充新增输出。 |
| 全部逐seed、配对差、均值/波动、四固定门槛 | [REPORT.md](REPORT.md)及六任务REPORT.md、analysis/results.json；固定60/70/80/90门槛，未达到不补造步数。完整更新/计算量曲线保留，PNG/PDF/SVG可独立导出。 |
| 错误、标题、主动结束、额外输出、截断 | 六任务CASE_REVIEW.md与analysis/error-details.json；重叠错误标志在results.json。9条正式候选及2条评测上限截断保留，其他均EOS；EOS不等于成功。标题错误不混成调用错误。 |
| 实际采样量、输出token、GPU成本 | [COSTS.md](COSTS.md)、[token审计](analysis/cost-and-token-audit.json)、[端点推理成本](analysis/endpoint-costs.json)、[生命周期审计](analysis/lifecycle-audit.json)。正式67172424训练输出token、17552357评测输出token；累计分配135.998 GPUh。嵌套计时不重复相加。 |
| 全部原始产物独立保留，旧实验不改 | 新目录下冻结配置、独立数据、原始候选/奖励、所有checkpoint、原始评测、日志与分析齐全。历史数据、模型、评分器和Prompt仅只读引用并校验哈希，没有旧实验重训或覆盖。 |
| 故障与资源调度留档 | 无正式训练/评测失败标记。旧调度器因计划内资源重分配被主动SIGTERM，训练未中断；所有18正式配对作业、12预检作业及8评测worker均exit0。原/替代控制器和v2/v3资源记录保留。 |
| 完整释放资源 | [现场资源核验](analysis/resource-release.json)：本机8卡及两远程各4卡全部0 MiB，三机均无本轮train/evaluate进程。CPU分析作业也exit0。 |
| 限制与后续不越界 | [CONCLUSIONS.md](CONCLUSIONS.md)区分训练收益、初始Prompt差异、地板、seed波动及机制假设。只将14B L5按预登记STEP验证窗口列为下一轮候选，不声称独立确认、创新性或真实任务迁移已完成；没有启动后续实验或发布。 |

## 数量核对

- 36正式run×100更新×16题×8候选＝460800候选。
- 36run×11固定checkpoint＝396 checkpoint。
- 每任务：原模型2条件×(256验证+512测试)＋6run×(10×256验证+512测试)＝19968实际输出；6任务＝119808。
- 原模型12个条件任务×2数据分片类型×4 shard＝96任务；正式36run×11次评测×4 shard＝1584；合计1680评测分片。
- 预检及恢复实际候选另为12×(4+2)×128＝9216，不并入正式候选，不作为额外seed。

## 审计方式与剩余事项

全组分析守护进程已正常完成，所有六任务的候选、原始评测和checkpoint均已全量复核，不仅依靠完成标记。额外审计重新检查原始模型文件、历史去重、实际优化器端点和token流。最终交付清单与文档哈希保存在`analysis/final-audit.json`。

本轮无剩余实验或分析事项。后续独立重复、机制对照、奖励改进、真实任务迁移及论文创新性调研属于新的工作范围，不包含在本轮完成声明内。
