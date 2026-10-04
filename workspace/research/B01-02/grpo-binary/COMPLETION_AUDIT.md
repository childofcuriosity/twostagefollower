# 完成验收与成本口径

2026-09-28，正式实验和分析已完成。核验依据为[final-audit.json](analysis/final-audit.json)、[results.json](analysis/results.json)、[resources-final.json](analysis/resources-final.json)。最终判断见[CONCLUSIONS.md](CONCLUSIONS.md)。

| 验收项 | 实际证据与结果 |
|---|---|
| 固定任务与起点 | 原始Qwen2.5-14B-Instruct，revision `cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8`；固定L2、九工具、原STEP/NAME Prompt、示例及chat模板；无SFT。Prompt和旧评分器哈希通过核验。 |
| 数据隔离 | 训练4096、验证256、测试512、预检64；内部及跨集合按调用链+输入去重，排除4954个旧L2组合。完整数据与来源哈希在[data/manifest.json](data/manifest.json)。每run固定预算使用训练池shuffle后的1600题，两条件题序相同。 |
| 评分与loss | 对照1968条旧输出、128条正确预检轨迹及每条3种变异；验证二值奖励、全同奖组零优势、prompt/padding不计loss、真实EOS参与loss、按每回答token均值再按候选均值聚合。见[implementation-tests.json](analysis/implementation-tests.json)。 |
| 预检与恢复 | STEP/NAME各4步；从step2恢复后step3/4候选及奖励完全一致，最终adapter最大差0。按正确性、有限数值及奖励区分度选择同一配置，不按NAME收益选参。见[precheck-complete.json](analysis/precheck-complete.json)。 |
| 配置冻结 | 冻结时间早于6run起点；3配对seed初始化hash相同，各run step0 LoRA B全零；所有正式run从原始起点启动，没有正式恢复或配置变更。见[freeze-manifest.json](config/freeze-manifest.json)、[frozen.json](config/frozen.json)、snapshots/formal-v1/。 |
| 完整训练 | 6run各100更新，16题×8候选/更新；共76800候选。逐条重算奖励、核对组内优势与题序通过。6个进程均正常退出。原始候选、日志和checkpoint在runs/v1-*。 |
| 固定checkpoint | 每run step0/10/…/100，共66个；adapter哈希、优化器、两rank RNG状态均核验。 |
| 全部预定评测 | 280分片，共19968条独立输出：原始step0的验证/测试1536条、60个训练后验证15360条、6个step100测试3072条。step0明确共享，不重复当seed证据。每条原始评分重算一致；测试未用于选checkpoint或改Prompt。 |
| 配对与曲线 | 全部seed端点、配对差、均值/样本SD及60/70/80/90%固定门槛；66点学习曲线。逐题表[paired-test-items.csv](analysis/paired-test-items.csv)，曲线表[learning-curves.csv](analysis/learning-curves.csv)。PNG/PDF/SVG图均保存。 |
| 错误及输出 | 操作、数字、提前结束、额外输出、标题分别记录；补充最终Answer与额外Trace边界案例。正式76800个候选和19968条评测均EOS结束，截断0。 |
| 资源与巡检 | .70/.65各4卡正式训练，本机4卡训练+4卡检查点评测。正常训练满1小时进行巡检，记录在[hourly-checks.jsonl](logs/hourly-checks.jsonl)。所有6训练和4评测worker正常退出，结束实测16卡显存占用均0 MiB。 |

## 计时结果

计时源为训练日志、每个评测任务metadata及job_runner进程时长；详细表为[cost-audit.json](analysis/cost-audit.json)。

| 范围 | 测得GPU小时 | 口径 |
|---|---:|---|
| 正式训练STEP三个run | 6.954 | 每run两卡×进程墙钟，含启动/加载/保存/等待 |
| 正式训练NAME三个run | 7.049 | 同上，较STEP约+1.36% |
| 正式训练合计 | 14.003 | 六个进程实际分配GPU墙钟 |
| 评测任务时间 | 1.550 | 280分片的任务墙钟和，含首次模型加载及换checkpoint |
| 其中评测生成 | 1.503 | generate计时和，不另与上行相加 |
| 评测worker完整生命周期 | 5.005 | 含等待训练checkpoint；与评测任务时间是包含关系，不相加 |
| 有完整计时的预检/恢复 | 1.711 | 保留v1、v2及两组恢复测试，非正式训练预算 |

正式训练输出共5,102,584 token；评测输出1,321,074 token。固定100更新下两条件输出token基本相同，时间仍有差异。曲线横轴的采样/更新GPU时间不含加载与保存；报告中整run分配时间包含这些开销。二者不混用，也不把分配GPU时间等同于内核忙碌时间。

两个最初torchrun参数解析失败发生在旧启动器阶段，没有完整退出时长；只保留失败日志，不补造GPU小时。NCCL基础设施探测和CPU数据/分析工作不在上述模型作业计时之内。评测worker等待期间不以无关推理或协议外seed占用GPU。

## 故障保留与范围

首次`--run`参数与torchrun选项冲突，在训练执行前退出；改名`--output-dir`。预检v1出现恢复后的数值差异，权重加载及RNG一致，差异最早出现在反向/更新；v2启用确定性算法后恢复结果逐元素一致，才冻结正式配置。NCCL约225秒初始化曾超过SSH客户端等待时间，已按真实进程状态处理；没有把客户端超时当作训练完成。详情见[infrastructure/DIAGNOSTICS.md](infrastructure/DIAGNOSTICS.md)。

正式训练全部正常，无OOM、NaN或中断。STEP seed301 update58有单rank KL峰值0.680、裁剪前梯度范数3.824；NAME seed302 update91有KL峰值0.309、裁剪前梯度范数1.977。按原配置裁剪继续完成，不将孤立峰值当作终止依据；后续曲线未出现持续崩溃。

离线绘图首次因训练venv缺少matplotlib失败，改用已有项目.analysis-venv（matplotlib3.10.1）完成；不安装或改变冻结训练环境，不重训。原始失败日志与exit标志保留，最终分析完成另记。其他历史实验未修改。

精度为BF16冻结基座、FP32 LoRA分支和优化器状态，无量化；GRPO实现及精度、KL、优势等细节见[METHOD.md](METHOD.md)。完成结论仅覆盖本轮固定L2、STEP/NAME和3配对seed。未加入内部奖励、额外模型/长度/seed，未自动执行Prompt优化或真实任务迁移，未对外发布。
