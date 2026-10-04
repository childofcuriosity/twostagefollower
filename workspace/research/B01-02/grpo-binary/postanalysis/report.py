import json,statistics
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];D=json.loads((R/'analysis/results.json').read_text())
figs=R/'figures';figs.mkdir(exist_ok=True)
colors={'STEP':'#345fa5','NAME':'#ca582d'}
fig,ax=plt.subplots(figsize=(8,5))
for c in ['STEP','NAME']:
 curves=[x for x in D['curves'] if x['condition']==c];xs=[x['step'] for x in curves[0]['points']]
 for x in curves:ax.plot(xs,[100*p['rate'] for p in x['points']],color=colors[c],alpha=.35,lw=1)
 means=[statistics.mean(x['points'][i]['rate'] for x in curves)*100 for i in range(11)];sd=[statistics.stdev(x['points'][i]['rate'] for x in curves)*100 for i in range(11)]
 ax.plot(xs,means,color=colors[c],lw=2.3,marker='o',label=c+' mean; band = seed SD (n=3)')
 ax.fill_between(xs,[m-s for m,s in zip(means,sd)],[m+s for m,s in zip(means,sd)],color=colors[c],alpha=.12)
for y in [60,70,80,90]:ax.axhline(y,color='gray',lw=.7,ls=':')
ax.set(xlabel='GRPO optimizer updates',ylabel='Strict validation success (%)',ylim=(0,100),xlim=(0,100));ax.legend(fontsize=9);ax.grid(alpha=.15);fig.tight_layout()
for ext in ['png','pdf','svg']:fig.savefig(figs/f'validation-vs-updates.{ext}',dpi=180)
plt.close(fig)
fig,ax=plt.subplots(figsize=(8,5))
for c in ['STEP','NAME']:
 for curve in [x for x in D['curves'] if x['condition']==c]:ax.plot([x['training_gpu_seconds']/3600 for x in curve['points']],[100*x['rate'] for x in curve['points']],marker='.',color=colors[c],alpha=.75,label=f'{c} seed {curve["seed"]}')
for y in [60,70,80,90]:ax.axhline(y,color='gray',lw=.7,ls=':')
ax.set(xlabel='Cumulative two-rank rollout + update GPU-hours',ylabel='Strict validation success (%)',ylim=(0,100));ax.legend(fontsize=8);ax.grid(alpha=.15);fig.tight_layout()
for ext in ['png','pdf','svg']:fig.savefig(figs/f'validation-vs-compute.{ext}',dpi=180)
plt.close(fig)
lines=['# B01-02：二值奖励GRPO标签学习对照','', 'Qwen2.5-14B-Instruct原始revision、固定L2、九工具及STEP/NAME Prompt与前轮一致；BF16基座+LoRA，无额外SFT。奖励仅严格完整轨迹0/1，标题不计奖励。6run各100更新，每更新16题×8候选。','', '## 新测试集端点（512题）','', '| seed | STEP step0→100 | STEP提升 | NAME step0→100 | NAME提升 | NAME−STEP端点差 |','|---:|---:|---:|---:|---:|---:|']
for seed in [301,302,303]:
 s=next(x for x in D['endpoints'] if x['seed']==seed and x['condition']=='STEP');n=next(x for x in D['endpoints'] if x['seed']==seed and x['condition']=='NAME')
 lines.append(f'| {seed} | {s["step0"]:.2%}→{s["step100"]:.2%} | {s["improvement"]*100:+.2f} pp | {n["step0"]:.2%}→{n["step100"]:.2%} | {n["improvement"]*100:+.2f} pp | {(n["step100"]-s["step100"])*100:+.2f} pp |')
for c in ['STEP','NAME']:
 x=D['summary'][c];lines.append(f'\n{c}：step100为{100*x["step100_mean"]:.2f}% ± {100*x["step100_sample_sd"]:.2f}%（3seed均值±样本SD）；相对本组step0平均提升{100*x["improvement_mean"]:+.2f}个百分点。')
p=D['summary']['paired'];lines+=['',f'配对NAME−STEP端点差均值{100*p["mean"]:+.2f} ± {100*p["sample_sd"]:.2f}个百分点；{p["positive_seeds"]}/3 seed为正。两组提升幅度之差均值{100*p["difference_of_improvements_mean"]:+.2f}个百分点。三个seed仅初步重复，不把seed×题数合并成大量独立模型重复。', '', 'step0为同一原始策略，每条件各算一次新验证/测试并由三个seed明确引用；各run单独保留其配对LoRA初始化checkpoint。新测试集只在预定step0和100评分，没有挑最好checkpoint。','', '## 验证门槛与完整学习曲线','', '| 条件 | seed | 首次60% | 首次70% | 首次80% | 首次90% | 曲线平均成功率（梯形面积/100） |','|---|---:|---:|---:|---:|---:|---:|']
for x in D['curves']:
 cells=[str(x['thresholds'][str(t)]['step']) if x['thresholds'][str(t)] is not None else '未达到' for t in [.6,.7,.8,.9]]
 lines.append('| '+x['condition']+' | '+str(x['seed'])+' | '+' | '.join(cells)+f' | {x["mean_validation_curve_area"]:.2%} |')
lines+=['', '门槛按step0/10/…/100固定评测点首次达到；不推断两检查点之间的精确跨越时刻，也不将未达到按任意更新数补值。完整逐seed曲线及每点实际训练token/GPU时间在analysis/results.json。','', '![验证成功率随更新](figures/validation-vs-updates.png)','', '![验证成功率随实际计算](figures/validation-vs-compute.png)','', '## 采样、优化与成本','', '| 条件 | seed | 候选数 | 输出token | 组内奖励有区分度比例 | 候选重复比例 | 最大KL | 训练分配GPU小时 |','|---|---:|---:|---:|---:|---:|---:|---:|']
for x in D['training']:lines.append(f'| {x["condition"]} | {x["seed"]} | {x["candidates"]} | {x["output_tokens"]} | {x["mixed_group_fraction"]:.2%} | {x["duplicate_fraction"]:.2%} | {x["max_kl"]:.5f} | {x["allocated_gpu_seconds"]/3600:.3f} |')
lines+=['', '候选重复比例在同一道题的8个输出内部统计。全0/全1组保留，任务优势为0，仍可能存在KL梯度。相同更新预算不等于相同计算量；compute曲线累计两rank采样和更新墙钟，训练分配GPU时间另含加载、保存及等待，不是GPU内核活动时间。评测开销与预检/恢复开销须在完成审计中单列。','', '## 标题、错误及结束原因（step100新测试）','', '| 条件 | seed | 标题全合规 | 操作序列不符 | 数字错误 | 前缀提前停止 | 额外原始操作 | 格式额外行 | 截断 |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for x in D['endpoints']:
 v=x['details'];e=v['errors'];lines.append(f'| {x["condition"]} | {x["seed"]} | {v["header_rate"]:.2%} | {e["operation_mismatch"]} | {e["numeric_error"]} | {e["early_end"]} | {e["extra_ops"]} | {e["extra_output"]} | {v["endings"].get("length",0)} |')
lines+=['', '错误标志非互斥；数字错误按输出前一步状态核验，展开不符包括额外/缺失操作。额外原始操作不直接称作额外工具调用；合法标题的合规另列，不纳入二值奖励。逐题原始输出、token IDs、EOS/上限证据保留在eval/outputs/。','', '## 证据与解释边界','', '冻结配置config/frozen.json及freeze-manifest.json；数据data/manifest.json；预检analysis/precheck-complete.json；固定checkpoint与候选runs/v1-*；完整曲线/配对/成本analysis/results.json；实现口径METHOD.md。最终研究判断及异常/资源审计见完成后补充的CONCLUSIONS.md和COMPLETION_AUDIT.md。','', '本轮只比较给定计划下的标签结构是否帮助训练执行。未加入内部/局部奖励，未验证真实数学或Agent迁移、跨模型泛化或创新性，不将方法收益与内部机制假设混为一谈。']
(R/'REPORT.md').write_text('\n'.join(lines)+'\n')
print('Report and standalone figures generated; final interpretation/audit still required.')
