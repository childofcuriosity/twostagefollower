# B01-02 prompt-only

独立的纯Prompt四标题对照；无训练或adapter。研究设计见REGISTRATION.md。现有训练实验只读。

入口：先`source training-env.sh`（项目根目录），再运行本目录src下脚本。

- download.py：官方模型固定revision及文件哈希。
- validate.py：DSL全状态验证、正确轨迹和人工错误变体评分核验。
- prepare.py --phase {precheck,explore,formal} --lengths ...：数据、四组Prompt、token预算、冻结清单。
- dispatch.py --phase ... --lengths ... --conditions STEP NAME ...：8卡任务调度；单长度正式实验按每组两份互斥题目分片用满8卡；每小时记录巡检。
- worker.py：BF16、SDPA、greedy，保存原始文本、token IDs、停止原因、成本。OOM自动减半batch并保留记录。
- score.py：旧严格评分与独立实现核验、标题合规、首错及配对bootstrap。
- select.py：只依STEP确定补测或正式长度；--final写选长记录。

原始输出在runs/，评分在analysis/，数据及冻结清单在data/。进程完成标志complete.json；异常日志保留在logs/及各run目录。
