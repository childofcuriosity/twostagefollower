import json,statistics,os
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(os.environ['GRPO_TASK_ROOT']);D=json.loads((R/'analysis/results.json').read_text());TASK=json.loads((R/'task.json').read_text())
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
lines=['# B01-02: label comparison under binary-reward GRPO','', f'Qwen2.5-{TASK["model"].upper()}-Instruct at the original revision, fixed L{TASK["length"]}; the nine tools and STEP/NAME prompts match the previous study; BF16 base + LoRA, with no additional SFT. Reward is strict full-trajectory 0/1, with no heading reward. Each of 6 runs has 100 updates, using 16 examples x 8 candidates per update.','', '## Fresh test endpoints (512 examples)','', '| seed | STEP step0 to 100 | STEP gain | NAME step0 to 100 | NAME gain | NAME-STEP endpoint difference |','|---:|---:|---:|---:|---:|---:|']
for seed in [301,302,303]:
 s=next(x for x in D['endpoints'] if x['seed']==seed and x['condition']=='STEP');n=next(x for x in D['endpoints'] if x['seed']==seed and x['condition']=='NAME')
 lines.append(f'| {seed} | {s["step0"]:.2%}→{s["step100"]:.2%} | {s["improvement"]*100:+.2f} pp | {n["step0"]:.2%}→{n["step100"]:.2%} | {n["improvement"]*100:+.2f} pp | {(n["step100"]-s["step100"])*100:+.2f} pp |')
for c in ['STEP','NAME']:
 x=D['summary'][c];lines.append(f'\n{c}: step100 = {100*x["step100_mean"]:.2f}% ± {100*x["step100_sample_sd"]:.2f}% (3-seed mean +/- sample SD); mean gain over the condition-specific step0 = {100*x["improvement_mean"]:+.2f} percentage points.')
p=D['summary']['paired'];lines+=['',f'Mean paired NAME-STEP endpoint difference: {100*p["mean"]:+.2f} ± {100*p["sample_sd"]:.2f} percentage points; {p["positive_seeds"]}/3 seeds are positive. Mean difference in learning gains: {100*p["difference_of_improvements_mean"]:+.2f} percentage points. Three seeds provide preliminary replication; seed x example counts are not treated as many independent model replications.', '', 'step0 uses the same original policy: fresh validation/test outputs are generated once per condition and explicitly referenced by three seeds. Each run retains its own paired LoRA initialization checkpoint. The fresh test set is scored only at the scheduled step0 and 100, with no best-checkpoint selection.','', '## Validation thresholds and complete learning curves','', '| Condition | seed | First 60% | First 70% | First 80% | First 90% | Mean curve success (trapezoidal area/100) |','|---|---:|---:|---:|---:|---:|---:|']
for x in D['curves']:
 cells=[str(x['thresholds'][str(t)]['step']) if x['thresholds'][str(t)] is not None else 'Not reached' for t in [.6,.7,.8,.9]]
 lines.append('| '+x['condition']+' | '+str(x['seed'])+' | '+' | '.join(cells)+f' | {x["mean_validation_curve_area"]:.2%} |')
lines+=['', 'Thresholds record the first fixed evaluation point at step0/10/.../100 that reaches the target. Exact crossing times between checkpoints are not inferred, and unreached thresholds receive no arbitrary update count. Complete per-seed curves and actual training tokens/GPU time at every point are in analysis/results.json.','', '![Validation success by update](figures/validation-vs-updates.png)','', '![Validation success by actual compute](figures/validation-vs-compute.png)','', '## Sampling, optimization, and costs','', '| Condition | seed | Candidates | Output tokens | Mixed-reward group fraction | Duplicate candidate fraction | Maximum KL | Training-segment GPU-hours |','|---|---:|---:|---:|---:|---:|---:|---:|']
for x in D['training']:lines.append(f'| {x["condition"]} | {x["seed"]} | {x["candidates"]} | {x["output_tokens"]} | {x["mixed_group_fraction"]:.2%} | {x["duplicate_fraction"]:.2%} | {x["max_kl"]:.5f} | {x["allocated_gpu_seconds"]/3600:.3f} |')
lines+=['', 'Duplicate fractions are measured within the 8 outputs for each example. All-0/all-1 groups are retained with zero task advantage, though KL gradients may remain. Equal update budgets do not imply equal compute. Compute curves accumulate sampling and update wall time across both ranks. Training-segment GPU time is run wall time after NCCL initialization x2, including model loading, saving, and waiting, but excluding earlier process/NCCL startup; it is not active GPU-kernel time. Full job occupancy, evaluation, and precheck/recovery costs are listed separately in the combined cost audit. These nested timings must not be added together.','', '## Headings, errors, and stopping reasons (step100 fresh test)','', '| Condition | seed | Fully compliant headings | Operation-sequence mismatch | Numerical error | Early prefix stop | Extra raw operations | Extra format lines | Truncation |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for x in D['endpoints']:
 v=x['details'];e=v['errors'];lines.append(f'| {x["condition"]} | {x["seed"]} | {v["header_rate"]:.2%} | {e["operation_mismatch"]} | {e["numeric_error"]} | {e["early_end"]} | {e["extra_ops"]} | {e["extra_output"]} | {v["endings"].get("length",0)} |')
lines+=['', 'Error flags can overlap. Numerical errors are checked against the preceding output state; expansion mismatches include extra/missing operations. Extra raw operations are not directly counted as extra tool calls. Heading compliance is reported separately and excluded from binary rewards. Per-example raw outputs, token IDs, and EOS/cap evidence are retained in eval/outputs/.','', '## Evidence and scope of interpretation','', 'Frozen configurations: config/frozen.json and freeze-manifest.json; data: data/manifest.json; prechecks: analysis/precheck-complete.json; fixed checkpoints and candidates: runs/v1-*; complete curves/pairing/costs: analysis/results.json. Implementation definitions are in the parent REGISTRATION.md. See the parent REPORT.md and COMPLETION_AUDIT.md for combined interpretation and acceptance checks.','', 'This study compares whether label structure helps train execution under a supplied plan. It adds no internal/local rewards and does not establish transfer to real mathematics or agents, cross-model generalization, or novelty. Method gains are distinguished from hypotheses about internal mechanisms.']
lines += ['', 'See [CASE_REVIEW.md](CASE_REVIEW.md) for supplementary mutually exclusive error categories, heading boundaries, and raw/reference trajectory examples. These categories interpret outputs without changing scores; heading noncompliance is distinct from tool-identity error.']
(R/'REPORT.md').write_text('\n'.join(lines)+'\n')
print('Report and standalone figures generated; final interpretation/audit still required.')
