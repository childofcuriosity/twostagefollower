from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
R=Path(__file__).resolve().parents[1]
x=json.loads((R/'analysis/results.json').read_text());audit=json.loads((R/'analysis/native-audit.json').read_text());lookup={a['run']:a for a in audit['records']}
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white','axes.titleweight':'bold'})
fig,axs=plt.subplots(2,2,figsize=(15,10));colors=['#637381','#DB9A25','#2475B0','#258D70']
def bars(ax,labels,counts,title):
 vals=[100*k/n for k,n in counts];ax.bar(range(len(vals)),vals,color=colors[:len(vals)],width=.64)
 for i,(v,(k,n)) in enumerate(zip(vals,counts)):ax.text(i,v+2,f'{k}/{n}',ha='center',fontsize=11)
 ax.set_xticks(range(len(vals)),labels);ax.set_ylim(0,114);ax.set_yticks([0,25,50,75,100]);ax.set_ylabel('Fully correct workflows (%)');ax.set_title(title,loc='left',fontsize=12);ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
old=[]
for p in (R.parent/'agent-study/runs').glob('main-*/*/summary.json'):
 s=json.loads(p.read_text())
 if s['condition']=='plan':old.append(s)
counts=[(sum(s['grade']['complete'] for s in old),len(old))]
for mode in ['zero','fewshot']:
 ss=[s for s in x['runs'] if s['tag'].startswith('regression-'+mode)];counts.append((sum(s['grade']['complete'] for s in ss),len(ss)))
bars(axs[0,0],['Archived custom\nprotocol','Native tools','Native tools\n+ example'],counts,'A. Paired engineering regression (24 tasks)')
cs=['plan','reminder','identity','todo'];counts=[(x['groups']['notes-replication-'+c]['complete'],x['groups']['notes-replication-'+c]['n']) for c in cs]
bars(axs[0,1],['Empty note','Generic\nreminder','Task\nidentity','Todo list'],counts,'B. Independent checklist replication (36 tasks)')
policies=[('controlled-v2-main-full','Full history'),('controlled-v2-main-trim','Trim history'),('controlled-v2-main-compact','Trim + summary'),('controlled-v3-main-sanitize','Filter role text')]
tasks=[f'queue-controlled-n24-s{20267001+i}' for i in range(3)]
def get(tag,task):
 ss=[s for s in x['runs'] if s['tag']==tag and s['task']==task];assert len(ss)==1,(tag,task);return ss[0]
ax=axs[1,0];positions=np.arange(3);width=.19
for j,(tag,label) in enumerate(policies):
 vals=[get(tag,t)['grade']['completed_requirements'] for t in tasks];spots=positions+(j-1.5)*width;ax.bar(spots,vals,width,color=colors[j],label=label)
 for pos,v in zip(spots,vals):ax.text(pos,v+.35,str(v),ha='center',fontsize=9)
ax.set_xticks(positions,['Seed 20267001','Seed 20267002','Seed 20267003']);ax.set_ylim(0,33);ax.set_yticks([0,6,12,18,24]);ax.set_ylabel('Correctly delivered tickets / 24');ax.set_title('C. Shared clock, schema, tools and budgets',loc='left',fontsize=12);ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True);ax.legend(fontsize=9,ncol=2,loc='upper right')
ax=axs[1,1]
for j,(tag,label) in enumerate(policies):
 s=get(tag,tasks[0]);a=lookup[s['run']];progress=a['progress'];xx=[0]+[p['turn']+1 for p in progress]+[s['turns']];yy=[0]+[p['correct'] for p in progress]+[s['grade']['completed_requirements']]
 ax.step(xx,yy,where='post',label=label,color=colors[j],linewidth=3.2 if j==2 else (1.8 if j==3 else 2),linestyle='--' if j==2 else (':' if j==3 else '-'));ax.scatter([xx[-1]],[yy[-1]],color=colors[j],s=28)
ax.text(.02,.98,'Identical first 6 turns; blue/green traces overlap.',transform=ax.transAxes,va='top',fontsize=8,color='#555555')
ax.axvline(6,color='#BBBBBB',linestyle=':',linewidth=1);ax.set_xlabel('Model generations');ax.set_ylabel('Independently verified correct deliveries');ax.set_ylim(-.5,25.5);ax.set_yticks([0,6,12,18,24]);ax.set_title('D. Same workflow: seed 20267001',loc='left',fontsize=12);ax.legend(fontsize=9,loc='lower right');ax.grid(alpha=.18)
fig.suptitle('Frozen Qwen2.5-32B-Instruct: execution reliability and controlled repairs',fontsize=16,y=.995)
fig.text(.5,.015,'Different task sets across panels. Three controlled workflows support a mechanism case study, not broad model generalization.',ha='center',fontsize=10,color='#555555')
fig.tight_layout(rect=[0,.045,1,.97]);(R/'figures').mkdir(exist_ok=True)
for ext in ['png','svg','pdf']:fig.savefig(R/'figures'/f'reliability.{ext}',dpi=170,bbox_inches='tight')
print('Saved PNG/SVG/PDF research figures')
