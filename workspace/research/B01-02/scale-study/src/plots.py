from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];out=R/'figures';out.mkdir(exist_ok=True)
d=json.loads((R/'analysis/results.json').read_text());e=json.loads((R/'analysis/extended-results.json').read_text());models=['qwen1.5b','qwen3b','qwen7b','qwen32b'];labels=['1.5B','3B','7B','32B'];colors={'flat':'#3268a8','macro':'#dd7a22'}
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'savefig.bbox':'tight'})
def save(fig,name):
 for ext in ['png','svg','pdf']:fig.savefig(out/f'{name}.{ext}',dpi=180)
 plt.close(fig)
fig,axs=plt.subplots(2,2,figsize=(12,8))
for ax,metric,title in zip(axs.flat,['accuracy','strict_trace','correct_prefix_early_answer','exact_two_tools_early_answer'],['Final answer accuracy','Exact execution trace accuracy','Correct prefix, then early answer','Correct first two tools, then stop']):
 for c in ['flat','macro']:
  values=[]
  for i,model in enumerate(models):
   r=next(r for r in d['summary'] if (r['model'],r['condition'],r['split'])==(model,c,'ood'));values.append(100*r['means'][metric]);ax.scatter([i]*3,[100*x[metric] for x in r['seeds'].values()],color=colors[c],alpha=.4,s=18)
  ax.plot(range(4),values,'o-',label=c,color=colors[c])
 ax.set(xticks=range(4),xticklabels=labels,ylim=(-3,103),title=title,xlabel='Qwen2.5 Base model size',ylabel='Percent');ax.grid(alpha=.15)
axs[0,0].legend();fig.suptitle('Original held-out 3–5-call tasks: lines = means, dots = 3 training seeds');fig.tight_layout();save(fig,'scale-comparison')
fig,axs=plt.subplots(2,2,figsize=(11,8),sharex=True)
for ax,model in zip(axs.flat,models):
 for c in ['flat','macro','frozen']:
  rs=sorted([r for r in e['summary'] if r['model']==model and r['condition']==c],key=lambda r:int(r['split'][6:]));xs=[int(r['split'][6:]) for r in rs];ys=[100*r['strict_trace'] for r in rs]
  ax.plot(xs,ys,'o--' if c=='frozen' else 'o-',color='#777777' if c=='frozen' else colors[c],label='frozen + definitions' if c=='frozen' else c)
 ax.set(title=model,xticks=[3,4,5,6,8],ylim=(-3,103),xlabel='Required tool calls',ylabel='Exact trace accuracy (%)');ax.grid(alpha=.15)
axs[0,0].legend();fig.suptitle('Independent unseen functions; frozen receives definitions, trained models do not');fig.tight_layout();save(fig,'independent-lengths')
fig,axs=plt.subplots(2,4,figsize=(19,8))
measures=[('iid','accuracy','short-task accuracy'),('ood','accuracy','long-task accuracy'),('ood','strict_trace','long-task exact trace'),('ood','correct_prefix_early_answer','correct prefix, early answer')]
for j,model in enumerate(['qwen7b','qwen32b']):
 for k,(split,metric,title) in enumerate(measures):
  ax=axs[j,k]
  for c in ['flat','macro']:
   xs=[0,16,64,128,256,512];ys=[]
   for step in xs:
    if step==512:
     r=next(r for r in d['summary'] if (r['model'],r['condition'],r['split'])==(model,c,split));ys.append(100*r['means'][metric])
    else:
     rs=[r for r in d['curves'] if (r['model'],r['condition'],r['split'],r['step'])==(model,c,split,step)];assert len(rs)==3;ys.append(100*np.mean([r[metric] for r in rs]))
   ax.plot(xs,ys,'o-',label=c,color=colors[c])
  ax.set(title=f'{model}: {title}',xlabel='Optimizer step',ylabel='Percent',ylim=(-3,103));ax.grid(alpha=.15)
axs[0,0].legend();fig.suptitle('Fixed checkpoint curves; all registered checkpoints, no test-selected stopping');fig.tight_layout();save(fig,'learning-curves')
print('Saved 3 plot groups in PNG/SVG/PDF',flush=True)
