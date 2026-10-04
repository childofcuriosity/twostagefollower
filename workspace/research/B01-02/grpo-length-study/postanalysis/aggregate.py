import json,statistics,csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]
TASKS=['7b-L3','7b-L4','7b-L5','14b-L5','14b-L6','14b-L7']
all_data={t:json.loads((R/t/'analysis/results.json').read_text()) for t in TASKS}
assert sum(x['formal_candidates_verified'] for x in all_data.values())==460800
assert sum(x['independent_eval_outputs_verified'] for x in all_data.values())==119808
assert sum(x['fixed_checkpoints_verified'] for x in all_data.values())==396
summary=[]
for task,d in all_data.items():
 val={c:statistics.mean(x['points'][-1]['rate'] for x in d['curves'] if x['condition']==c) for c in ['STEP','NAME']}
 auc={c:statistics.mean(x['mean_validation_curve_area'] for x in d['curves'] if x['condition']==c) for c in ['STEP','NAME']}
 summary.append(dict(task=task,summary=d['summary'],paired=d['paired'],validation_step100_mean=val,validation_curve_area_mean=auc,STEP_validation_candidate_20_to_90=(.2<=val['STEP']<=.9),training_candidates=sum(x['candidates'] for x in d['training']),training_output_tokens=sum(x['output_tokens'] for x in d['training']),training_gpu_hours=sum(x['allocated_gpu_seconds'] for x in d['training'])/3600))
(R/'analysis/summary.json').write_text(json.dumps(summary,indent=2)+'\n')
(R/'figures').mkdir(exist_ok=True);colors={'STEP':'#2864a5','NAME':'#cc572f'}
fig,axes=plt.subplots(2,3,figsize=(14,8),sharex=True,sharey=True)
for ax,task in zip(axes.flat,TASKS):
 d=all_data[task]
 for c in ['STEP','NAME']:
  curves=[x for x in d['curves'] if x['condition']==c];xs=[p['step'] for p in curves[0]['points']]
  for x in curves:ax.plot(xs,[100*p['rate'] for p in x['points']],color=colors[c],alpha=.25,lw=.8)
  means=[statistics.mean(x['points'][i]['rate'] for x in curves)*100 for i in range(11)];sd=[statistics.stdev(x['points'][i]['rate'] for x in curves)*100 for i in range(11)]
  ax.plot(xs,means,color=colors[c],marker='.',label=c,lw=2);ax.fill_between(xs,[m-s for m,s in zip(means,sd)],[m+s for m,s in zip(means,sd)],color=colors[c],alpha=.12)
 ax.set(title=task.upper(),xlim=(0,100),ylim=(0,100));ax.grid(alpha=.15);ax.legend(fontsize=8)
for ax in axes[-1]:ax.set_xlabel('GRPO optimizer updates')
for ax in axes[:,0]:ax.set_ylabel('Strict validation success (%)')
fig.suptitle('All fixed validation curves: mean and seed SD (n=3)');fig.tight_layout()
for ext in ['png','pdf','svg']:fig.savefig(R/f'figures/all-learning-curves.{ext}',dpi=180)
plt.close(fig)
fig,axes=plt.subplots(1,2,figsize=(11,4.5),sharey=True)
for ax,model in zip(axes,['7b','14b']):
 tasks=[t for t in TASKS if t.startswith(model)];lengths=[int(t.split('L')[1]) for t in tasks]
 for c in ['STEP','NAME']:
  ys=[100*all_data[t]['summary'][c]['step100_mean'] for t in tasks];sd=[100*all_data[t]['summary'][c]['step100_sample_sd'] for t in tasks]
  ax.errorbar(lengths,ys,yerr=sd,marker='o',color=colors[c],capsize=4,label=c+' step100')
  ax.plot(lengths,[100*all_data[t]['summary'][c]['step0'] for t in tasks],marker='x',ls=':',color=colors[c],alpha=.7,label=c+' original')
 ax.set(title='Qwen2.5-'+model.upper()+'-Instruct',xlabel='Tool-call length',xticks=lengths,ylim=(0,100));ax.grid(alpha=.2);ax.legend(fontsize=8)
axes[0].set_ylabel('Strict test success (%)');fig.tight_layout()
for ext in ['png','pdf','svg']:fig.savefig(R/f'figures/test-success-vs-length.{ext}',dpi=180)
plt.close(fig)
lines=['# 二值GRPO：模型×长度扩展完整结果','','所有6组合均完成STEP/NAME×3配对seed，每run100更新。主指标严格完整轨迹成功率。下列均为新测试集512题的预定端点；误差为seed样本SD，不是题目抽样置信区间。','','| 组合 | STEP step0→100均值±SD | NAME step0→100均值±SD | 配对NAME−STEP均值±SD(pp) | 正/负/平seed | STEP验证终点 | 20%–90%候选窗口 |','|---|---:|---:|---:|---|---:|---|']
for x in summary:
 s=x['summary']['STEP'];n=x['summary']['NAME'];p=x['summary']['paired'];pairs=x['paired'];counts=[sum(y['NAME_minus_STEP']>0 for y in pairs),sum(y['NAME_minus_STEP']<0 for y in pairs),sum(y['NAME_minus_STEP']==0 for y in pairs)]
 lines.append(f'| {x["task"]} | {s["step0"]:.2%}→{s["step100_mean"]:.2%} ±{s["step100_sample_sd"]*100:.2f}pp | {n["step0"]:.2%}→{n["step100_mean"]:.2%} ±{n["step100_sample_sd"]*100:.2f}pp | {p["mean"]*100:+.2f} ±{p["sample_sd"]*100:.2f} | {counts[0]}/{counts[1]}/{counts[2]} | {x["validation_step100_mean"]["STEP"]:.2%} | {"是" if x["STEP_validation_candidate_20_to_90"] else "否"} |')
lines+=['','候选窗口按运行前登记的STEP固定验证集step100三seed均值20%–90%判断，不按NAME差值大小挑组，不据测试挑checkpoint。全部连续值及seed波动保留，候选仍须独立确认。每个组合的原始step0按条件评测一次供3seed共享，不算3次独立模型证据。','','![训练前后长度曲线](figures/test-success-vs-length.png)','','![全部学习曲线](figures/all-learning-curves.png)','','## 全部预定门槛','','| 组合 | 条件 | seed | 60% | 70% | 80% | 90% |','|---|---|---:|---:|---:|---:|---:|']
for task,d in all_data.items():
 for curve in d['curves']:
  vals=[str(curve['thresholds'][str(v)]['step']) if curve['thresholds'][str(v)] is not None else '未达到' for v in [.6,.7,.8,.9]]
  lines.append('| '+task+' | '+curve['condition']+' | '+str(curve['seed'])+' | '+' | '.join(vals)+' |')
lines+=['','阈值仅在step0/10/.../100固定评测点判断；所有门槛与全部曲线共同解释，未达到不补任意更新数。训练GPU时间和输出token轴的曲线见各组合报告，不把等更新视为等计算。','','## 每组证据','']
for task in TASKS:lines.append(f'- [{task}完整报告]({task}/REPORT.md)：逐seed端点、基准提升、配对差、曲线、采样/成本/错误及标题。')
lines+=['','整体判断、故障和资源验收见CONCLUSIONS.md与COMPLETION_AUDIT.md。固定L5两模型共享底层数据；整个六组合是探索性组合筛查，不是六次独立正式确认。']
(R/'REPORT.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(summary,indent=2))
