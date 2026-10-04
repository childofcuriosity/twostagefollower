# 阶段1/4：模型固定与环境准备

Goal active。用户已批准Agent早停研究并要求优先几十B规模验证；用户建议每次进度更新先说明阶段，已采用。

阶段1：下载固定版本32B及7B，文件SHA校验。
阶段2：每个模型独立前后向/显存校准，microbatch 16→8→4→2→1，仅OOM或显存余量不足时降低。
阶段3：flat/macro×seed11/22/33，共12正式训练，保存固定检查点；32B使用GPU0–2，7B使用GPU4–6。
阶段4：全量测试归因、规模比较与研究报告。达到文件marker不等于已审核交付。

下载日志根目录logs/training/scale-download-*.log，训练启动器最新日志scale-launch-*-v2.log。首个Python TLS失败已保留，改curl取得元数据。所有环境与缓存限定项目目录；长任务低频按阶段检查。

训练程序继承原始数据、优化器和标签对照；仅做小microbatch拆分及激活检查点，按原16例逻辑batch目标token数加权保持原损失归一化，BF16。注册记录analysis/registration.json。没有量化、没有测试挑最好轮次。


## 实际运行记录

本轮由Codex直接编写并运行Python脚本，未通过EvoScientist聊天界面驱动；不能将结果表述为Evo自动研究效果。用户已询问并已明确说明。

32B固定revision 1818d35814b8319459f4bd55ed1ac8709630f003；7B固定revision d149729398750b98c0af14eb82c78cfe92750796。下载curl经过公司代理，发生过大文件中断，curl自动重试/续传。监控应看文件逻辑长度，远程FS的du分配块大小不能代表下载进度。下载完整才写download-manifest.json并触发校准。

原microbatch16拆成4的BF16梯度一致性检查未通过自定3%容差（4.35%），记录未删除；保留16、只启用梯度检查点时损失与梯度一致，analysis/checkpointing-check.json passed。注册v2启用评估KV缓存，v3改为优先原microbatch16，修改均在任何正式训练之前。小microbatch回退不宣称逐位等价，需报告实现差异。

已运行等待队列：launch.py各模型一份，下载完成→校准→三GPU各顺序flat/macro两组（共6作业/模型）。checkpoints.py各模型一份，等待本模型六作业成功后测试0/16/64/128/256检查点，最终512测试由train.py完成。finish.py等待两模型检查点全部成功→全量分析，不自动标goal完成。

测试/审计入口src/analyze.py已在原1.5/3B的6,720条测试输出上执行通过，新模型缺失会明确列出。ANALYSIS_COMPLETE只表示自动核验结束，仍需手工报告、尺度比较、统计区间、图表、失败说明及更新Goal。

活跃统一终端sessions（需要时再使用，不频繁轮询）：下载32B=80588、7B=18257；启动器32B=63290、7B=2777；检查点评测等待32B=87821、7B=35465；最终分析等待=91372。无需重启正常等待进程。旧启动器已仅在等待状态终止，v2是当前版本。

后续：先检查下载/校准阶段标记，诊断真实失败；保留32B主对照和7B规模参照，按Goal交付结果。低学习率对称敏感性及32B-Instruct桥接尚未启动，不能在报告里声称完成。新确认集更长调用也尚未生成。不要以原配方尺度结果直接证明先验机制。


## 最近推进（规模目标继续）

7B下载及SHA清单完成。启动器首次校准因--tag后参数以减号开头触发argparse错误，未加载模型即结束；已改--tag=value，保留失败日志。registration-v4登记。最新启动器日志scale-launch-qwen7b-v3.log、scale-launch-qwen32b-v3.log；新sessions分别60633、99713，旧v2均已终止且未中断训练。

7B校准microbatch16成功，峰值21,976,851,456 bytes（20.47GiB），两优化步3.148秒；三seed正式flat作业已启动，先做step0开发集有/无定义评测，之后512步并逐检查点评测；各seed完成flat后自动macro。qwen7b-token-audit.json确认所有训练token IDs与旧1.5B相同，flat/macro逐题监督token长度匹配。

新增独立确认集已锁定：data/extended-test.jsonl，480条、120个不同函数，3/4/5/6/8调用各24程序×4输入，功能与历史train/dev/test全不重叠；登记analysis/extended-data-registration.json。max_new_tokens512避免8调用被256截断。四模型都评；frozen基线给定义，训练后测试不给定义，必须分开解释。extended.py正在GPU3/7分别先评原1.5/3B；两lane随后在对应32B/7B主训练完成后评新模型。sessions lane0=94314、lane1=35533。原始log在runs/extended-*.log。冻结输出可能长，按阶段低频检查，不因没有立即输出就重启。

主analyze.py已提取audit.py独立逐题核验。inference.py输出按程序聚类配对bootstrap与三训练seed t区间，以及新480题全量审计；不把不同seed同题当独立样本。finalize.py(session29935)等待主ANALYSIS_COMPLETE及四模型extended完成，重分析后生成REPORT草稿与REVIEW_READY；prepare_review.py(session9825)接续检查12训练/84checkpoint哈希并绘图。二者日志scale-finalize.log、scale-prepare-review.log。所有完成marker仍需科学审核和CONCLUSIONS，不自动标goal完成。

有用的未决事项：32B权重仍在下载；无需重复下载/启动。检查32B/7B实际训练异常。检查新代码最终统计和图是否覆盖目标；补32B token一致性审计。必要的低LR对称敏感性、32B-Instruct等更深桥接尚未执行，不能说已经排除这些因素。主尺度比较结束后根据证据决定和明确报告边界。


## 第三次推进：32B完整下载与补充控制排队

32B Base下载已完成，共26文件65.54GB；17个权重分片的本地SHA256全部与固定revision的Hub LFS SHA256匹配，analysis/qwen32b-remote-hash-audit.json。32B token审计也完成，与原1.5B训练token IDs逐项一致。32B启动器已进入microbatch16两步校准，尚需查看校准结果。

7B三个flat作业已完成训练前开发基线，实际参数更新和中间检查点评测进行中。不能据初始基线的等待误判为没有训练。旧模型的独立确认评测也正常进行。

为兑现修订方案中的剂量/指令版本控制，已在新模型最终分数不可见时登记补充实验（analysis/supplement-registration.json）：Qwen3B Base与32B Base对称lr=1e-4，各flat/macro×3seed；32B-Instruct lr=3e-4，同样6训练+一次冻结基线。每组固定512步，保留中途adapter但不在线重复评测；原始全量560题有/无工具定义两套最终评测。不据最终分数选最好设置。Instruct使用官方chat模板，训练测试一致，与Base分表。

32B-Instruct下载在32B Base完全下载之后才启动，session18865，日志scale-download-instruct.log。低LR lane（session73137）等待7B主检查点评测完成，然后用GPU4–6依次跑3B和32B低LR；Instruct lane（session2998）等待32B主检查点评测完成和Instruct下载，再GPU0–2先校准/冻结基线后6训练。因此不占用主尺度实验的GPU。32B extended仍占GPU3，7B extended GPU7，不冲突。

补充分析analyze_supplement.py（session77592）等待两补充lane和主ARTIFACTS_READY，审计18训练、126适配器哈希、21,280原始执行记录（18×2×560+冻结2×560），生成SUPPLEMENT.md和SUPPLEMENT_READY。source脚本train_supplement.py单独保存，不修改正在运行的主train.py。主REPORT草稿的“未运行补充”段需要人工最后根据实际完成结果更新。

Goal完成要求现在包含这些已排队的批准方案对照，不能在仅主ARTIFACTS_READY时宣布全部完成；须同时核验SUPPLEMENT_READY、解释低LR/指令结果、补总成本、最终结论和图表。尚无规模研究结论。


## 当前核实：正式训练运行中

32B microbatch16校准成功，无需回退；峰值74,882,093,056 bytes（69.74GiB），两步10.8835秒。GPU0–2正式flat三seed正在训练前基线评测；7B三seed运行中，seed11已过256步。八GPU均有实际负载，未重启任何正常作业。补充verify.py对每一步loss/lr/grad_norm/elapsed的有限值、连续512步及有效batch32的检查，登记verification-amendment.json。此项是交付核验增强，不修改训练或测试配置。


## 同提示条件的训练前后比较已接入交付核验

新增src/matched_context.py，由尚在等待的prepare_review后续调用verify.py时执行。逐题比较7B/32B冻结step0与最终step512：有定义对有定义、无定义对无定义，分别报告答案、严格轨迹、两工具后结束、前缀早停和预算命中的变化与0→1/1→0数量；核对id/chain/x/expected/split及冻结输出重复性。共检查26,880条记录（含重复冻结测量，不作为独立样本），不增加模型运行。analysis/matched-context-registration.json登记。语法检查通过，完整运行必须等所需评测完成，尚不能宣称结果已验证。此输出用于避免把提示信息差异误归因于训练后能力变化。


## 停止证据口径核查

原生成脚本保存非EOS token计数（PAD=EOS），没有保存生成token IDs。不能追溯声称直接记录了停止原因。audit.py新增stop_evidence：非EOS数>=上限为length_limit_reached；=上限-1为边界不确定；<上限-1依据仅EOS/长度停止的配置推断在上限前EOS。REPORT模板明确该局限，analyze.py按模型/条件/测试分组计数。已经在旧模型6,720条全量记录重新执行通过，新7/32B仍明确缺失。未修改任何训练/生成程序。登记stop-evidence-registration.json。


## 全量局部错误指标补齐

audit.py新增已输出操作首次偏离位置、操作选错、数值步骤错误、额外格式行、缺失/多个Answer。指标允许重叠，不宣称互斥因果归因；单纯漏后缀不算操作选错。analyze.py与REPORT模板包含对应长组合汇总，旧6,720条重新核验通过。登记local-error-registration.json。1.5B独立确认集完整7轮3,360条及哈希已核验，分析存qwen1.5b-confirmation-audit.json；3/5/8调用macro严格轨迹正确率52.43/5.90/1.04%，flat均0，尚不支持规模结论。


## 指令模型下载与模板核验完成

Qwen2.5-32B-Instruct固定revision 5ede1c97bbab6ce5cda5812749b4c0bdf79b18dd下载完成，原下载会话退出码0。对全部4,096训练题实测：训练/测试提示编码相同，flat/macro逐题目标长度相同，最大含目标序列189 tokens，未触及320防截断上限；EOS为151645 im_end。证据analysis/qwen32b-instruct-token-audit.json。这只证明格式一致，不证明指令模型训练已完成或能力更强。仍依原队列等待主32B检查点评测完成再启动补充训练。3B独立确认集3,360条及哈希已审计，qwen3b-confirmation-audit.json；macro严格轨迹3/5/8调用83.68/28.47/2.08%，flat均0。


## 用户提供远程资源：前两台已运行

REDACTED_HOST:31585有8×5090 32GB，共享同路径与venv已验证；remote_3b.py(PID12935)校准成功后在GPU0–5并行六个3B低LR作业，实际GPU有负载。local原lr等待器PID1537599在无子进程时终止，新增仅等待器session35730(PID1721395)，后续采用远程3B完成记录，再在本机GPU4–6运行32B低LR；避免重复3B任务。launcher新增remote claim采用逻辑，训练源码未变。

REDACTED_HOST:30929有4×PRO6000 Blackwell 96GB，共享路径和CUDA验证成功；local原Instruct等待器PID1537647在无子进程时终止。远程launcher PID11796 --lane instruct --remote-ready，先校准（已通过）和冻结基线（实际运行），再GPU0–2三seed配对训练。不再等主实验，资源独立；正式train_supplement.py保持注册哈希。日志scale-remote-qwen3b.log、scale-remote-instruct.log。SSH复用socket位于项目目录，未保存密码。



## 最新远程分工：补充训练与主检查点评测并行

第一台5090六个3B低LR作业全部成功，训练与6,720条输出已核验（remote-qwen3b-completion-audit.json）。现无后续任务分配。新服务器172.169.20.70:31432具有4×PRO6000 Blackwell96GB，共享路径与相同torch/CUDA验证通过。原local lr等待器PID1721395在无子进程时终止；remote lr PID444706采用已完成3B结果并在GPU0–2运行32B低LR，不再等待7B检查点。source train_supplement.py保持未变。

两台PRO6000的GPU3提前处理已保存且开发评测落盘的32B flat固定检查点：.65服务器PID31809按seed11→33；.70服务器PID449696处理seed22。直接使用原checkpoints.py条件评测分支，生成原定输出路径，无参数/采样修改。原32B checkpoint父等待器PID1499385无子进程时被终止，新session79658等待主训练后采用远程flat完成记录、在本机GPU0–2跑macro检查点。src/checkpoints.py仅增加父调度采用远程结果的分支，condition评测不变；登记remote-checkpoints-claim.json。主训练未被中断。

远程日志：scale-remote-lr.log、scale-remote-instruct.log、scale-remote-checkpoints-11-33.log、scale-remote-checkpoints-22.log。不要再启动旧local lr/Instruct等待器或重复flat检查点评测。常规进度检查约15分钟；配置新资源后的启动确认可及时进行。


## 7B检查点完成，空闲卡用于32B macro提前评测

7B六组固定检查点评测已全部成功，32B flat三个正式作业成功退出，macro三seed已在GPU0–2运行。核实本机GPU4–6显存为空后，early_macro_checkpoints.py(session29564)在4–6并行评测macro的0/16/64/128/256检查点；每个检查点等待对应开发输出落盘，以保证权重已完整保存，生成方式不变。当前step0权重均存在。

32B检查点汇总父等待器PID1782127无子进程时被替换，新日志scale-checkpoints-qwen32b-v3.log。新的父等待器在主训练完成后采用远程flat和本机early macro结果，不重复评测。登记early-macro-checkpoints-claim.json。early宏检查点墙钟可能包含等待权重的时间，最终成本应区分保留GPU时间与实际评测时间，勿当作纯GPU核计算。


## 5090服务器已交还用户

用户要求利用空闲5090服务器，若不适合则退回。对172.169.20.32:31585做四卡32B BF16、batch4、greedy原配置短测（仅8条旧dev，未启动长实验）：36.30秒，56.06非EOS token/s，峰值每卡约14–17GiB，无CPU/磁盘offload；但仅3/8 raw输出与原单卡PRO6000对照逐字一致，一致性门未通过。证据analysis/sharded32-probe.json和日志scale-sharded32-probe.log保留；不把该差异未经验证归因于多卡或硬件某一个因素，也不混入主研究结果。确认8卡显存全部0MiB且无compute进程后交还用户，remote-resources.json设returned_to_user_do_not_schedule。无新分配授权不再使用；原3B低LR结果仍保留，其5090硬件差异在最终报告如实注明。


## 32B独立确认评测改为本机同型号多任务并行

原extended32等待子进程PID1563753及lane0父进程PID1512033尚未加载模型、原32B extended输出目录不存在时被终止；未中断实际评测。新extended32_parallel.py(session1954)仍等待主六作业全部成功，随后用本机GPU0/1/2/3/7按队列并行完成原七轮确认评测。各单轮采用extended32_worker.py，其evaluate函数从原extended.py原样复制；每个模型仍独占单卡PRO6000，batch4/max512/BF16/greedy及480题不变。每轮独立载入相同base+指定adapter，原输出路径、7个meta和completed.json格式保持。登记parallel-extended32-registration.json；日志scale-extended32-parallel.log。旧lane0不会再生成完成marker，以新parallel-extended32-completed.json替代调度证据；研究结果finalizer依然使用extended/qwen32b/completed.json。

## 分析收尾更新

全部主最终测试、独立确认与补充学习率/Instruct结果已经落盘。SUPPLEMENT_READY已生成。32B flat seed33固定检查点评测仍存活：远程.65 PID134272，GPU显存64986MiB；其余主检查点已完成。不要重启该作业或使用已交还的5090服务器。

新增outcome_diagnostics.py已成功逐条核验48,160条主/独立/补充原始输出，分类指定轨迹正确、全函数等价、当前输入偶然正确与无有效支持轨迹，核验24个主训练的LoRA参数量。新增mastery_diagnostics.py读取全部72个固定开发检查点；登记未规定数字掌握阈值，因此90/95/99%仅作透明标注的事后敏感性，不能冒充预注册。等待最后测试完成后再连接对应测试结果。

CONCLUSIONS.md已有实测结论和边界，仍明确为阶段报告。plots.py补入正确前缀早停第一终点，以及IID掌握、OOD准确率/完整轨迹/早停的固定曲线；等待最终数据后由原prepare_review生成，尚未渲染验收。仍需完成固定检查点、审核verify覆盖范围、生成/目视核验图、修订report.py旧补充未运行表述、完成协议和资源收尾审计。goal仍active。


最终验收加强：verify.py现在必须核对174个预定原始输出文件共95,200条的完整题目ID、输入、split和逐条解释器检查，包含84个额外检查点/定义文件，不再仅凭统计总条数。report.py已纳入补充训练与成本口径；mastery_diagnostics.py会按开发集选择加入对应测试结果，全部90/95/99%阈值均标为事后探索。修改登记final-audit-amendment.json。约15分钟间隔检查确认remote .65 PID134272仍存活，seed33已完成step16、正在step64；最后测试仍未完成，未启动重复工作。


## 第一阶段已全部完成

所有预定作业成功退出；最后32B flat seed33检查点已完成。verification通过174文件/95,200原始输出、84主适配器；补充18训练与126适配器也已核验。72开发检查点掌握敏感性测试全部齐全；三组图已目视检查。报告、明确协议偏差和逐项验收见CONCLUSIONS.md与COMPLETION_AUDIT.md，交付清单analysis/DELIVERY_COMPLETE.json。本机和两台PRO6000服务器无剩余研究计算进程。等待用户统一结果审核；不擅自启动真实Agent第二阶段。上述状态替代此前进行中段落。
