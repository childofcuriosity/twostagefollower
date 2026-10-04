"""Descriptive error flags across every fixed validation checkpoint; no new inference."""
import json,statistics
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];D=json.loads((R/'analysis/results.json').read_text())
keys=['operation_mismatch','numeric_error','early_end','extra_output','extra_ops','missing_ops']
rows=[]
for step in range(0,101,10):
 for c in ['STEP','NAME']:
  points=[curve['points'][step//10] for curve in D['curves'] if curve['condition']==c]
  base=D['base'][c]['validation']
  errors={k:statistics.mean((base if step==0 else p)['errors'][k] for p in points) for k in keys}
  rows.append(dict(condition=c,step=step,mean_error_counts_per_256=errors,mean_header_rate=statistics.mean(base['header_rate'] if step==0 else p['header_rate'] for p in points)))
(R/'analysis/error-curves.json').write_text(json.dumps(rows,indent=2)+'\n')
fig,axes=plt.subplots(1,2,figsize=(10,4),sharey=True)
for ax,k,label in zip(axes,keys[:2],['Operation-sequence mismatch','Local numeric error']):
 for c,color in [('STEP','#345fa5'),('NAME','#ca582d')]:
  rr=[x for x in rows if x['condition']==c]
  ax.plot([x['step'] for x in rr],[100*x['mean_error_counts_per_256'][k]/256 for x in rr],marker='.',label=c,color=color)
 ax.set(title=label,xlabel='GRPO optimizer updates',xlim=(0,100));ax.grid(alpha=.2);ax.legend()
axes[0].set_ylabel('Validation outputs with error flag (%)')
fig.tight_layout()
for ext in ['png','pdf','svg']:fig.savefig(R/f'figures/validation-error-curves.{ext}',dpi=180)
plt.close(fig)
lines=['','## Error changes throughout training (fixed validation set)','','The figure covers every prespecified checkpoint. Curves show the mean error-flag fractions over 3 seeds. Flags can overlap. A numerical error means that the current raw operation is computed incorrectly given the preceding output state. Numerical errors and tool-expansion/order errors are counted separately and must not be added into a total error rate.','','![Complete error curves](figures/validation-error-curves.png)','','| Update | STEP expansion errors/256 | NAME expansion errors/256 | STEP numerical errors/256 | NAME numerical errors/256 | STEP heading compliance | NAME heading compliance |','|---:|---:|---:|---:|---:|---:|---:|']
for step in range(0,101,10):
 s,n=[next(x for x in rows if x['condition']==c and x['step']==step) for c in ['STEP','NAME']]
 lines.append(f'| {step} | {s["mean_error_counts_per_256"]["operation_mismatch"]:.2f} | {n["mean_error_counts_per_256"]["operation_mismatch"]:.2f} | {s["mean_error_counts_per_256"]["numeric_error"]:.2f} | {n["mean_error_counts_per_256"]["numeric_error"]:.2f} | {s["mean_header_rate"]:.2%} | {n["mean_header_rate"]:.2%} |')
lines+=['','All error flags, EOS/truncation information, and per-seed raw data are in analysis/results.json, analysis/error-curves.json, and eval/outputs.']
with (R/'REPORT.md').open('a') as f:f.write('\n'.join(lines)+'\n')
print('Full validation error curves generated.')
