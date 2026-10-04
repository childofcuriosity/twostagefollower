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
lines=['# Binary GRPO: full model-by-length results','','All 6 settings completed STEP/NAME × 3 paired seeds, with 100 updates per run. The primary metric is strict full-trajectory success. Values below are the scheduled endpoints on 512 fresh test examples; uncertainty is the sample SD across seeds, not an example-sampling confidence interval.','','| Setting | STEP step0→100 mean±SD | NAME step0→100 mean±SD | Paired NAME−STEP mean±SD(pp) | Positive/negative/tied seeds | STEP validation endpoint | 20%–90% candidate window |','|---|---:|---:|---:|---|---:|---|']
for x in summary:
 s=x['summary']['STEP'];n=x['summary']['NAME'];p=x['summary']['paired'];pairs=x['paired'];counts=[sum(y['NAME_minus_STEP']>0 for y in pairs),sum(y['NAME_minus_STEP']<0 for y in pairs),sum(y['NAME_minus_STEP']==0 for y in pairs)]
 lines.append(f'| {x["task"]} | {s["step0"]:.2%}→{s["step100_mean"]:.2%} ±{s["step100_sample_sd"]*100:.2f}pp | {n["step0"]:.2%}→{n["step100_mean"]:.2%} ±{n["step100_sample_sd"]*100:.2f}pp | {p["mean"]*100:+.2f} ±{p["sample_sd"]*100:.2f} | {counts[0]}/{counts[1]}/{counts[2]} | {x["validation_step100_mean"]["STEP"]:.2%} | {"Yes" if x["STEP_validation_candidate_20_to_90"] else "No"} |')
lines+=['','The candidate window uses the preregistered 20%–90% range for three-seed mean STEP success on the fixed validation set at step100. Settings are not selected by the NAME difference, nor checkpoints by test results. All continuous values and seed variation are retained; candidates still require independent confirmation. Original step0 is evaluated once per condition in each setting and shared across 3 seeds, rather than counted as 3 independent model evaluations.','','![Length curves before and after training](figures/test-success-vs-length.png)','','![All learning curves](figures/all-learning-curves.png)','','## All prespecified thresholds','','| Setting | Condition | seed | 60% | 70% | 80% | 90% |','|---|---|---:|---:|---:|---:|---:|']
for task,d in all_data.items():
 for curve in d['curves']:
  vals=[str(curve['thresholds'][str(v)]['step']) if curve['thresholds'][str(v)] is not None else 'Not reached' for v in [.6,.7,.8,.9]]
  lines.append('| '+task+' | '+curve['condition']+' | '+str(curve['seed'])+' | '+' | '.join(vals)+' |')
lines+=['','Thresholds are checked only at fixed evaluation points step0/10/.../100. Interpret all thresholds together with the complete curves; unreached thresholds are not assigned arbitrary update counts. Each setting report also plots curves against training GPU time and output tokens. Equal update counts are not treated as equal compute.','','## Evidence for each setting','']
for task in TASKS:lines.append(f'- [{task} full report]({task}/REPORT.md): per-seed endpoints, gains over baseline, paired differences, curves, sampling, costs, errors, and headings.')
lines+=['','See CONCLUSIONS.md and COMPLETION_AUDIT.md for overall interpretation, failures, and resource checks. The two models share underlying data at fixed L5. These six settings form an exploratory screen, not six independent confirmatory experiments.']
(R/'REPORT.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(summary,indent=2))
