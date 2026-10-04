import collections,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'analysis/results.json').read_text());g=collections.defaultdict(collections.Counter)
for r in d['results']:
    if r['kind']=='curve' and (r['split']=='dev' or r['split']=='length8'):
        g[r['model'],r['condition'],r['seed'],r['step'],r['mode'],r['split']].update(r['counts'])
fig,axes=plt.subplots(2,4,figsize=(16,7),sharey=True)
specs=[('Short dev: autonomous','dev',[('joint','joint','Together')]),('8 tools: autonomous','length8',[('joint','joint','Together')]),('8 tools: execution test','length8',[('joint','order_oracle','Together'),('order_oracle','order_oracle','Execution only')]),('8 tools: sequence test','length8',[('joint','operation_oracle','Together'),('operation_oracle','operation_oracle','Sequence only')])]
for row,model in enumerate(['qwen3b','qwen32b']):
    for col,(title,split,conditions) in enumerate(specs):
        ax=axes[row,col]
        for ix,(c,m,label) in enumerate(conditions):
            color=['#2471a3','#d35400'][ix];values=[]
            for seed in [11,22,33]:
                a=[g.get((model,c,seed,step,m,split)) for step in [64,128,256,512]]
                if not all(a):continue
                v=[100*z['complete']/z['n'] for z in a];values.append(v);ax.plot([64,128,256,512],v,color=color,alpha=.25,linewidth=1)
            if len(values)==3:ax.plot([64,128,256,512],[sum(x[i] for x in values)/3 for i in range(4)],marker='o',color=color,label=label)
        ax.set_xscale('log',base=2);ax.set_xticks([64,128,256,512],['64','128','256','512']);ax.set_ylim(-2,102);ax.grid(alpha=.2);ax.set_title(model.replace('qwen','')+' | '+title);ax.legend(fontsize=8)
        if row==1:ax.set_xlabel('Training steps')
        if col==0:ax.set_ylabel('Complete task accuracy (%)')
fig.suptitle('Fixed checkpoint trajectories; thin lines = individual seeds, thick lines = mean\nExecution/sequence tests receive the other component from the program; autonomous tests do not');fig.tight_layout(rect=[0,0,1,.90]);out=R/'figures';out.mkdir(exist_ok=True)
for ext in ['png','svg','pdf']:fig.savefig(out/f'checkpoint-curves.{ext}',dpi=180)
print('Checkpoint figures written')
