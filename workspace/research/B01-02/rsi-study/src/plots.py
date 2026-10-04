from pathlib import Path
import json,statistics,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':150,'savefig.bbox':'tight','pdf.fonttype':42})
colors={'base':'#222222','flat':'#D55E00','macro':'#0072B2','shared':'#D55E00','frozen':'#0072B2','replay':'#009E73','joint':'#CC79A7','shuffled':'#E69F00'}
def save(fig,name):
 for ext in ['png','svg','pdf']:fig.savefig(OUT/f'{name}.{ext}')
 plt.close(fig)
rob=json.loads((ROOT/'analysis/robust-results.json').read_text());models=list(rob['summary'])
fig,axes=plt.subplots(1,len(models),figsize=(4.1*len(models),3.8),squeeze=False)
for ax,m in zip(axes[0],models):
 for c in ['base','flat','macro']:
  ys=[rob['summary'][m][f'instruction-t1.0-k{k}'].get(c,{}).get('compression',np.nan)*100 for k in [4,16,64]]
  ax.plot([4,16,64],ys,'o-',label=c,color=colors[c])
 ax.set_xscale('log',base=4);ax.set_xticks([4,16,64],['4','16','64']);ax.set_title(m);ax.set_xlabel('Proposal budget');ax.set_ylim(0,65);ax.grid(alpha=.15)
axes[0,0].set_ylabel('Held-out net compression (%)');axes[0,-1].legend();fig.suptitle('Execution fine-tuning and proposal utility: fixed instruction prompt');fig.tight_layout();save(fig,'proposal-budget')
# All prompt settings, to avoid selecting a favorable one.
fig,axes=plt.subplots(1,len(models),figsize=(4.1*len(models),3.8),squeeze=False)
settings=[('instruction',1.),('concise',1.),('fewshot',1.),('instruction',1.5)]
for ax,m in zip(axes[0],models):
 for i,c in enumerate(['base','flat','macro']):
  ys=[rob['summary'][m][f'{s}-t{t}-k16'].get(c,{}).get('compression',np.nan)*100 for s,t in settings];ax.plot(range(4),ys,'o-',label=c,color=colors[c])
 ax.set_xticks(range(4),['instruction','concise','few-shot','T=1.5'],rotation=25);ax.set_title(m);ax.set_ylim(0,65);ax.grid(alpha=.15)
axes[0,0].set_ylabel('Held-out net compression (%)');axes[0,-1].legend();fig.suptitle('Prompt and temperature sensitivity, K=16');fig.tight_layout();save(fig,'prompt-robustness')
if '--robust-only' in sys.argv:sys.exit(0)
lr=json.loads((ROOT/'analysis/loop-results.json').read_text());raw=[json.loads(l) for l in (ROOT/'analysis/loop-rows.jsonl').read_text().splitlines()]
fig,axes=plt.subplots(2,3,figsize=(12,7))
for ri,d in enumerate(['digits','strings']):
 for ci,(field,label) in enumerate([('proposal_compression','Proposal compression'),('short_accuracy','Short execution accuracy'),('family_accuracy','Held-out family execution')]):
  ax=axes[ri,ci]
  for c in lr['summary'][d]:
   ys=[]
   for rnd in range(4):ys.append(lr['summary'][d][c].get(str(rnd),{}).get(field,np.nan)*100)
   ax.plot(range(4),ys,'o-',color=colors[c],label=c)
   for seed in [11,22,33]:
    vals=[next((r[field]*100 for r in raw if r['domain']==d and r['condition']==c and r['seed']==seed and r['round']==rnd),np.nan) for rnd in range(4)]
    ax.plot(range(4),vals,color=colors[c],alpha=.18,linewidth=.7)
  ax.set_title(d+': '+label);ax.set_xticks(range(4));ax.set_xlabel('Round');ax.set_ylim(-2,102 if ci else 65);ax.grid(alpha=.15)
axes[0,0].set_ylabel('Percent');axes[1,0].set_ylabel('Percent');axes[0,2].legend(fontsize=8);fig.suptitle('Three-round loops: thick lines = means, thin lines = three seeds');fig.tight_layout();save(fig,'loop-trajectories')
fig,axes=plt.subplots(1,2,figsize=(9,3.8))
for ax,d in zip(axes,['digits','strings']):
 for i,s in enumerate(['short','family','pressure']):
  v=lr['branch_comparisons'][d].get(s)
  if not v:continue
  ax.scatter([i-.08,i,i+.08],np.array(v['seed_differences'])*100,color='#0072B2',s=25)
  mean=v['base_source_minus_updated']*100;lo,hi=np.array(v['t_interval_95'])*100
  ax.errorbar(i,mean,yerr=[[mean-lo],[hi-mean]],fmt='s',color='#222222',capsize=5)
 ax.axhline(0,color='gray',lw=1);ax.set_xticks(range(3),['short','family','pressure']);ax.set_title(d);ax.grid(axis='y',alpha=.15)
axes[0].set_ylabel('Base-source minus updated-source accuracy (pp)');fig.suptitle('Same learner start: proposal-source intervention (3 seeds; t intervals)');fig.tight_layout();save(fig,'causal-branches')
grad=[]
for p in (ROOT/'runs').glob('gradient-*/results.json'):
 v=json.loads(p.read_text())
 for r in v['records']:grad.append({**v['args'],**r})
if grad:
 fig,ax=plt.subplots(figsize=(6,3.8))
 for c in ['shared','joint']:
  ys=[statistics.mean(r['cosine'] for r in grad if r['condition']==c and r['round']==rnd) for rnd in range(4)]
  ax.plot(range(4),ys,'o-',label=c,color=colors[c])
 ax.axhline(0,color='gray',lw=1);ax.set_xticks(range(4));ax.set_xlabel('Round');ax.set_ylabel('Gradient cosine');ax.set_title('Execution loss vs proposal NLL surrogate');ax.legend();fig.tight_layout();save(fig,'gradient-alignment')
print('Figures written',OUT)

# Original-recipe timecourse is a post-hoc replay, not an early-stopping sweep.
curve=json.loads((ROOT/'analysis/timecourse-results.json').read_text())
fig,axes=plt.subplots(1,2,figsize=(9.5,3.8))
steps=[0,16,64,128,256,512]
for field,label,color in [('iid_accuracy','IID execution','#009E73'),('ood_accuracy','Unseen composition','#0072B2')]:
 axes[0].plot(steps,[curve['summary'][str(n)][field]*100 for n in steps],'o-',label=label,color=color)
 for seed in [11,22,33]:axes[0].plot(steps,[next(r[field]*100 for r in curve['rows'] if r['seed']==seed and r['step']==n) for n in steps],color=color,alpha=.18,lw=.7)
axes[1].plot(steps,[curve['summary'][str(n)]['proposal_compression']*100 for n in steps],'o-',color='#D55E00')
for seed in [11,22,33]:axes[1].plot(steps,[next(r['proposal_compression']*100 for r in curve['rows'] if r['seed']==seed and r['step']==n) for n in steps],color='#D55E00',alpha=.25,lw=.8)
axes[0].set_ylabel('Execution accuracy (%)');axes[1].set_ylabel('Held-out proposal compression (%)');axes[0].legend()
for ax in axes:ax.set_xlabel('Optimizer step');ax.set_xticks([0,64,128,256,512]);ax.grid(alpha=.15)
fig.suptitle('Original macro recipe: all recorded checkpoints, no test-selected stopping');fig.tight_layout();save(fig,'training-timecourse')
