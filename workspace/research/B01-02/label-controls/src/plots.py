from common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
D=json.loads((R/'analysis/results.json').read_text())['summary'];(R/'figures').mkdir(exist_ok=True)
fig,axes=plt.subplots(2,2,figsize=(12,9),sharex=True,sharey=True)
colors=['#7b7b7b','#1874b5','#d47b18','#278047'];labels=['Original STEP','Original tool names','Call positions','Fixed tool aliases']
for ax,model in zip(axes.flat,ROOTS):
 for condition,color,label in zip(['flat','macro','position','alias'],colors,labels):
  cells=[next(r for r in D if (r['model'],r['dataset'],r['condition'],r['group'])==(model,'independent',condition,L)) for L in [3,4,5,6,8]]
  for s in range(3):ax.plot([3,4,5,6,8],[100*r['seeds'][s]['rates']['strict_trace'] for r in cells],color=color,alpha=.18,linewidth=1)
  ax.plot([3,4,5,6,8],[100*r['mean']['strict_trace'] for r in cells],'-o',color=color,label=label,linewidth=2)
 ax.set_title(model);ax.set_ylim(-2,102);ax.set_xticks([3,4,5,6,8]);ax.grid(alpha=.2)
for ax in axes[:,0]:ax.set_ylabel('Strict complete trace (%)')
for ax in axes[1]:ax.set_xlabel('Requested tool calls')
handles,leg=axes[0,0].get_legend_handles_labels();fig.legend(handles,leg,loc='lower center',ncol=4)
fig.suptitle('Only two new label conditions; legacy protocol and baselines retained\nFixed step 512; thin lines: three seeds; thick lines: means')
fig.tight_layout(rect=[0,.05,1,.94])
for ext in ['png','pdf','svg']:fig.savefig(R/f'figures/label-controls.{ext}',dpi=180)
