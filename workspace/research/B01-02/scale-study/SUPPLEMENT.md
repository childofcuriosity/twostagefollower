# 低学习率与指令版本补充

这组在新模型正式最终分数尚不可见时登记：3B/32B对称采用1e-4，原主配方3e-4；32B-Instruct采用3e-4和官方chat模板，每组flat/macro三个seed，512步、batch32。没有按测试调学习率或停止步。中间适配器保留，本组固定最终测试。

| 模型 | 条件 | 是否提供工具定义 | 长组合答案正确 | 完整轨迹正确 | 正确两工具后结束 |
|---|---|---|---:|---:|---:|
| qwen3b | flat | no_definitions | 0.09% | 0.00% | 73.26% |
| qwen3b | flat | definitions | 1.13% | 0.00% | 5.47% |
| qwen3b | macro | no_definitions | 13.72% | 12.33% | 0.17% |
| qwen3b | macro | definitions | 8.16% | 7.03% | 1.30% |
| qwen32b | flat | no_definitions | 30.38% | 30.03% | 0.17% |
| qwen32b | flat | definitions | 87.50% | 87.15% | 0.00% |
| qwen32b | macro | no_definitions | 55.56% | 53.65% | 0.00% |
| qwen32b | macro | definitions | 79.17% | 78.47% | 0.00% |
| qwen32b-instruct | flat | no_definitions | 34.64% | 34.55% | 7.47% |
| qwen32b-instruct | flat | definitions | 57.47% | 57.38% | 2.78% |
| qwen32b-instruct | macro | no_definitions | 65.19% | 64.76% | 0.00% |
| qwen32b-instruct | macro | definitions | 59.11% | 58.59% | 0.35% |
| qwen32b-instruct | frozen | no_definitions | 0.00% | 0.00% | 0.00% |
| qwen32b-instruct | frozen | definitions | 0.00% | 0.00% | 0.00% |

frozen基线只有一次确定性评测，不冒充三个训练seed。无定义基座不知道人为颜色映射，不能将其低分当作能力低；给定义与不给定义属于不同条件。Base/Instruct的模板和后训练均不同，不能把所有差异归因于参数规模或先验稳定性。3B低学习率组使用5090，而原3B使用PRO6000；此硬件差异也限制其纯学习率因果解释。32B两档学习率均为PRO6000。

完整逐seed差与95% t区间、逐题核验、训练计数和126个检查点哈希见[补充统计](analysis/supplement-results.json)。本文件仅汇总，科学结论须结合主报告和CONCLUSIONS.md。
