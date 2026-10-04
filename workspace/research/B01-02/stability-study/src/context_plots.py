"""Fixed-axis old/fresh program results, including every seed for primary routes."""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

R=Path(__file__).resolve().parents[1]
fig,axes=plt.subplots(2,2,figsize=(12,8),sharex=True,sharey=True)
for col,(directory,label,key) in enumerate([
    ('context-intervention','Previously used programs','metrics'),
    ('fresh-confirmation','Pre-frozen new programs','scores')]):
    records=json.loads((R/directory/'analysis/comparisons.json').read_text())['records']
    for row,model in enumerate(['qwen3b','qwen32b']):
        ax=axes[row,col]
        for route,color in [('JJ','#2267ad'),('SE','#ce6b1b')]:
            selected={r['length']:r for r in records if r['model']==model and r['a_route']==r['b_route']==route and r['a_context']=='local' and r['b_context']=='full' and r['length']!='all'}
            assert set(selected)=={3,4,5,6,8}
            for scope,column,style in [('Full history','b','--'),('Local operation input','a','-')]:
                curves=[[100*selected[length]['seeds'][seed][key]['complete'][column] for length in [3,4,5,6,8]] for seed in range(3)]
                for curve in curves:ax.plot([3,4,5,6,8],curve,color=color,linestyle=style,alpha=.22,linewidth=.8)
                mean=[sum(c[i] for c in curves)/3 for i in range(5)]
                training='Shared training' if route=='JJ' else 'Separate training'
                ax.plot([3,4,5,6,8],mean,color=color,linestyle=style,marker='o',markersize=4,linewidth=2,label=f'{training}: {scope}')
        ax.set_title(f'{model}: {label}');ax.set_ylim(0,102);ax.set_xticks([3,4,5,6,8]);ax.grid(alpha=.2)
        if col==0:ax.set_ylabel('Whole-task success (%)')
        if row==1:ax.set_xlabel('Requested tool calls')
handles,labels=axes[0,0].get_legend_handles_labels()
fig.legend(handles,labels,loc='lower center',ncol=2,bbox_to_anchor=(.5,0),frameon=False)
fig.suptitle('No-oracle execution, fixed step 512; thick: 3-seed mean, thin: individual seeds',fontsize=12)
fig.tight_layout(rect=(0,.08,1,.96))
(R/'figures').mkdir(exist_ok=True)
for ext in ['png','svg','pdf']:fig.savefig(R/'figures'/f'context-and-fresh-confirmation.{ext}',dpi=180)
plt.close(fig)
