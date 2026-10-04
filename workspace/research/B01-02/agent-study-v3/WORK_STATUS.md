# 执行兼容性复核

原96在../agent-study完整保留、已audit/replay。这里不是替换原结果，是开发阶段发现协议干扰后的复核，四组提示条件不变，统一支持完整JSON多调用、agent工作目录imports和每轮3072上限。累计预算仍8192/16384、工具回合32/64、上下文24576；不训练。三个修复同时改变，不能分别作因果结论。

registration.json、preflight.json锁定；task-manifest与原v2相同24题。src/sandbox.py和tasks.py保证agent可导入/work而grader不添加work到sys.path。tasks目录symlink指向原fixture目录，新cal-v3-files/data/code每项4要求、seed9029；旧任务内容不修改。

运行launcher session90663，logs/launch.log；先GPU0三条校准，3/3才继续96。原预算已用2.72665GPU小时，本批校准cap900秒，四主worker各3600秒，连同watchdog留余量仍低于8。分析脚本仅出描述性汇总，尚需为batch轨迹实现audit/replay，核验消息、token、全部final-workspace与实际终止；不可直接使用原single-action verifier。正常检查15分钟。


## 已按能力失败分支结束

新四要求校准files/code通过，data未建reports目录、代码报错却同批finish，2/3未达3/3门槛，未启动main96。三份归档独立重验，token与hash核对见analysis/calibration-verification.json；约0.074026GPU小时，总项目2.800671GPU小时。没有运行中的GPU任务。总体交付在../agent-study/CONCLUSIONS.md。不要重启主队列。
