# 真实Agent开发冒烟

用户已授权无人值守执行并设置active goal。项目根目录不变，模型与环境全部复用本项目；本机8×PRO6000空闲，仅计划用GPU0–3，不访问已交还5090。

当前阶段1/4：任务和隔离环境已实现。24主任务（files/data/code，每类4/12要求各4实例）+6单要求能力任务生成，task-manifest与registration锁定。任务是开发生成器，只有三类模板，不能冒充24独立研究题型。代码任务目前是多模块纯函数实现，不能声称已涵盖大型仓库修改或长程依赖。允许Python批量处理，不强制多次工具调用。

隔离：chroot内标准库Python，降权65534、seccomp禁网络/子进程/硬链接等，运行8秒CPU/512MiB/12秒墙钟限制。模型看不到研究验证器或其他任务。因共享文件系统不支持硬链接，运行环境采用复制，每worker复用隔离根、每轨迹重置work；原失败log保留。初次动态链接器执行权限修正后，普通代码、越界/网络/进程/运行环境写入五项实测通过（sandbox-check.json）。

运行句柄：任务验证session71962，PID2418071，logs/task-validation.log。验证正确解、初始未解及每个要求删除后的失败；完成才生成task-validation.json。launcher session58387正在等待上述真实验证进程，logs/launch.log；不要重复启动。其后自动运行calibration GPU0六条，必须6/6通过；不通过写CALIBRATION_FAILED并停止主队列待诊断。通过后按固定随机顺序分4worker×24条运行96轨迹。calibration wall cap1800秒、各主worker5400秒，总预算8GPU小时内。tool/meta协议及全部任务在第一次模型轨迹前锁定。

Agent每轮输出JSON status/tool/args，支持list/read/write/run_python/finish。由模型自主finish；环境不阻止不完整结束、不反馈隐藏验收。原始messages/trajectory包含输入输出token、每轮最终token ID和确切EOS/length-limit证据。结束后复制final-workspace并独立评分。当前未开始SFT或RL。

正常长任务约15分钟检查；下一步检查task-validation和校准实际进展。主队列结束自动analyze，但仍需人工阅读全部失败、复核grader、成本、状态协议遵循、继续/放弃判断及最终报告，goal不会自动标完成。

## 已进入阶段3/4：96条主轨迹运行中

原calibration耗时480.59 GPU秒，4/6通过，data两个失败属于猜错路径/字段、未遵守聚合JSON输出要求后误报完成。未启动v1主队列。保留registration-v1、task-manifest-v1、task-validation-v1及runs/calibration原始轨迹。

registration-v2说明：仅统一澄清data输入CSV路径、字段、输出聚合结构（不提供正确数值）；24主任务加v2后缀保留原fixture；换新single-task seeds2/3，六项全部通过。30任务参考解与每项遗漏检测均再次通过。最新launcher session75776，日志launch-v2.log；validation session44679已成功。当前GPU0–3进程2471030/2471031/2471032/2471043，四个main worker共96轨迹在运行。不要启动原launcher/session58387或旧calibration；初版calibration失败marker是历史证据，不是当前阻塞。

最新注册source/task hash见registration-v2.json；实际四组顺序main-order.json。长任务按15分钟检查。预算须包括旧校准480.59秒、新校准、四个主worker，不能仅统计成功轨迹。模型保持冻结、未做SFT/RL。下一步读运行结果，审核所有失败、真实结束原因和status字段的实际遵循（baseline也可能自然复述任务身份，不能假定处理严格分离）；结束后做固定工作副本的独立重验、阶段性完成后空转诊断和成本汇总，再写结论。

## 阶段3进展与分析准备

一次低频检查已有91/96主轨迹完成，GPU1–3 worker已完成24条，GPU0仍运行最后5条（PID2471030）。不重启正常作业。

analysis-only新增audit.py核对注册执行/任务hash、消息与轨迹一致性、token计数及从final-workspace重验全部96；replay.py按原动作重放，定位首次真实完成与之后动作，不能把完成后验证都叫空转。原analyze.py执行结束后会自动调用这两个CPU审核；修改未触及正在运行的Agent。完整valid JSON多对象输出被单对象解析器拒绝的情况单独做离线执行诊断，绝不当作新真实Agent成功率。

已读两条失败：data-n12-s2 reminder创建12报告但区域/阈值配对错误，仅2项通过；code-n04-s0 identity一次输出4个写文件对象和finish被整体拒绝，随后误称已完成，实际4个文件均未改。不能把这些全归入“长程中途停止”的同一机制，也不能忽略custom JSON协议影响。基线可自行写status任务ID，需要量化处理条件的实际分离。

下一步主队列结束自动审核，可能需处理重放差异；然后阅读全部失败、统计协议因素、生成图/最终报告、核算包括两次校准的GPU预算，并判断是否需要在预算内做执行协议稳健性修复验证。未做SFT/RL。

## 原96已完成并验收；执行兼容性复核启动

全部96原主轨迹完成，52失败；audit和replay均通过，96重放最终文件与原始归档逐字一致，原主线含两次校准总2.7266446927520964 GPU小时。完成率plan9/24、reminder16/24、identity9/24、todo10/24；不支持名称优势。29个多JSON批次离线执行中23个可通过，但这不是新Agent rollout成功率。全部原始数据不修改。

具体执行干扰：单对象parser会拒绝完整多调用；每轮1536上限截断长JSON；Python-I不含cwd导致正常jobs包导入失败。用户授权无人值守修复，当前在独立`../agent-study-v3`开展兼容性复核，不能混合两批。统一支持完整JSON对象序列按顺序执行（整批截断仍拒绝）、agent Python加入/work import路径（隐藏grader仍isolated）、每轮cap3072；累计token/上下文/调用等其他预算不变。四组全部应用相同更改；这三项合并修复不允许各自归因因果效应。

v3复用同24任务，新增3个四要求能力样本（每家族一个），参考解、正常工作目录import、完整batch解析/截断拒绝已实测通过。v3 registration在模型输出前锁定。v3 launcher session90663，logs/launch.log，先GPU0校准3/3，成功后自动4GPU×24；cap校准900秒+main每worker3600秒，连同原2.73小时保守总上限约7.15GPU小时。若校准失败，诊断marker，不盲目继续。原goal保持active，此时不要按原96已完成就关闭目标；需纳入协议复核及最终解释。


## 本goal交付完成

原96主轨迹+12单项校准+3修复后多要求校准共111条均核验。修复校准2/3未通过预设3/3门槛，故第二批96未运行；这是登记的停止分支，不是未结束作业。原主96全部重验/重放、所有52失败逐要求归因、全部25首次完成后动作分类。结论/限制/协议偏差/训练建议见CONCLUSIONS.md，逐项验收COMPLETION_AUDIT.md，交付hash为analysis/delivery-manifest.json。总2.800671GPU小时，GPU无计算任务。未做SFT或RL，等待用户研究结果审核，不把开发冒烟写成方法有效或已解决真实Agent早停。此前进行中状态以本条为准。
