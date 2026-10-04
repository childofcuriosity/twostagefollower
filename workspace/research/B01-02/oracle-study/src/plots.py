import collections,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'analysis/results-audit.json').read_text());g=collections.defaultdict(collections.Counter);seed_values=collections.defaultdict(list)
for r in d['results']:
 if r['split'].startswith('length'):
  key=(r['model'],r['condition'],r['mode'],r['length']);g[key].update(r['counts']);seed_values[key].append(100*r['counts']['complete']/r['counts']['n'])
fig,axes=plt.subplots(2,4,figsize=(15,7),sharex=True,sharey=True)
for col,model in enumerate(['qwen1.5b','qwen3b','qwen7b','qwen32b']):
 for row,mode in enumerate(['order_oracle','operation_oracle']):
  ax=axes[row,col]
  for cond,env,label,color,style in [('joint','joint','Joint: autonomous','#555555','--'),('joint',mode,'Joint: oracle supplied','#2471a3','-'),(mode,mode,'Specialist: oracle supplied','#d35400','-')]:
   xs=[];ys=[];lo=[];hi=[]
   for L in [3,4,5,6,8]:
    c=g.get((model,cond,env,L))
    if c and c['n']==288:
     xs.append(L);ys.append(100*c['complete']/c['n']);values=seed_values[model,cond,env,L];lo.append(min(values));hi.append(max(values))
   ax.plot(xs,ys,marker='o',label=label,color=color,linestyle=style)
   if env!='joint':ax.fill_between(xs,lo,hi,color=color,alpha=.10,linewidth=0)
  ax.set_title(model.replace('qwen','')+' | '+('Correct order supplied' if row==0 else 'Correct execution supplied'));ax.set_xticks([3,4,5,6,8]);ax.set_ylim(-2,102);ax.grid(alpha=.2)
  if col==0:ax.set_ylabel('Complete task accuracy (%)')
  if row==1:ax.set_xlabel('Requested tool calls')
handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',ncol=3);fig.suptitle('Oracle ablations: independent program set\nLines: mean of 3 seeds; shaded oracle bands: seed min-max (not confidence intervals)');fig.tight_layout(rect=[0,.07,1,.93]);out=R/'figures';out.mkdir(exist_ok=True)
for ext in ['png','svg','pdf']:fig.savefig(out/f'oracle-comparison.{ext}',dpi=180)
print('Saved oracle comparison figures; only complete length cells shown')
