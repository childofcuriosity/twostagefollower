from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
R=Path(__file__).resolve().parents[1];d=json.loads((R/'analysis/results.json').read_text());out=R/'figures';out.mkdir(exist_ok=True)
conditions=['plan','reminder','identity','todo'];labels=['Initial checklist','Generic reminder','Current task identity','Updated checklist']
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axs=plt.subplots(1,3,figsize=(16,4.6))
for ax,metric,title in zip(axs,['complete_rate','premature_finish_rate','mean_generated_tokens'],['Verified full completion (%)','Incomplete voluntary finish (%)','Generated tokens / trajectory']):
 for j,length in enumerate([4,12]):
  values=[]
  for c in conditions:
   item=next(x for x in d['summary'] if x['family']=='all' and x['length']==length and x['condition']==c)
   values.append(item[metric]*(1 if metric=='mean_generated_tokens' else 100))
  ax.bar(np.arange(4)+(j-.5)*.36,values,.36,label=f'{length} requirements')
 ax.set(xticks=np.arange(4),xticklabels=labels,title=title);ax.tick_params(axis='x',labelrotation=25);ax.grid(axis='y',alpha=.2)
 if metric!='mean_generated_tokens':ax.set_ylim(0,105)
axs[0].legend();fig.suptitle('Frozen Qwen2.5-32B-Instruct: 24 development tasks × 4 conditions\nIncomplete finish includes protocol and correctness failures; not all are pure early stopping')
fig.tight_layout()
for ext in ['png','svg','pdf']:fig.savefig(out/f'agent-smoke.{ext}',dpi=180,bbox_inches='tight')
print('Saved descriptive smoke figure; no significance claim')
