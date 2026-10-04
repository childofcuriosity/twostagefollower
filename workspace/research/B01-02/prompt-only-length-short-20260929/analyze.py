from pathlib import Path
import sys,json,hashlib,csv,collections,time
R=Path(__file__).resolve().parent;P=R.parent/'prompt-only';sys.path.insert(0,str(P/'src'))
from score import grade
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
rows=[];ends=collections.Counter();count=0;sources={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for model in ['7b','14b']:
 root=R/model
 for L in range(2,10):
  if L in [2,5]:
   p=(P if model=='7b' else P/'fallback14')/f'analysis/scores-explore-L{L}.json';s=json.loads(p.read_text())['results'];sources[str(p)]=sha(p)
   for c in ['STEP','NAME']:rows.append(dict(model=model,condition=c,length=L,n=s[c]['n'],correct=s[c]['correct'],rate=s[c]['rate'],source='historical exploration',finish_reasons=s[c]['finish_reasons']))
   continue
  data=[json.loads(s) for s in (root/f'data/explore-L{L}.jsonl').read_text().splitlines()]
  for c in ['STEP','NAME']:
   folder=root/f'runs/explore-L{L}-{c}';m=json.loads((folder/'complete.json').read_text());p=folder/'predictions.jsonl';assert sha(p)==m['prediction_sha256'];sources[str(p)]=sha(p)
   rr=[json.loads(s) for s in p.read_text().splitlines()];assert len(rr)==32
   assert [(x['id'],x['chain'],x['x']) for x in rr]==[(x['id'],x['chain'],x['x']) for x in data]
   gg=[]
   for x in rr:
    full=grade(x);g={k:full[k] for k in ['id','condition','length','strict','canonical_order','header_compliant','operation_mismatch','numeric_step_error','format_error','finish_reason','generated_tokens','input_tokens','legacy']}
    gg.append(g);ends[x['finish_reason']]+=1;count+=1
   (root/f'analysis/graded-L{L}-{c}.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in gg))
   rows.append(dict(model=model,condition=c,length=L,n=32,correct=sum(x['strict'] for x in gg),rate=sum(x['strict'] for x in gg)/32,source='new short exploration',finish_reasons=dict(collections.Counter(x['finish_reason'] for x in rr)),header_compliant=sum(x['header_compliant'] for x in gg)))
assert count==768
jobs=[Path(p) for p in json.loads((R/'dispatch.json').read_text())['jobs']];meta=[json.loads(p.with_suffix('.json.exit.json').read_text()) for p in jobs];assert len(meta)==16 and all(x['returncode']==0 for x in meta)
(R/'results.json').write_text(json.dumps(dict(rows=rows,new_outputs_verified=count,new_finish_reasons=dict(ends),source_hashes=sources,job_gpu_seconds=sum(x['seconds'] for x in meta),model_jobs_wall_seconds=max(x['finished'] for x in meta)-json.loads((R/'dispatch.json').read_text())['started']),indent=2)+'\n')
with (R/'rates.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['model','condition','length','correct','n','rate','source']);w.writerows([x[k] for k in ['model','condition','length','correct','n','rate','source']] for x in rows)
fig,axes=plt.subplots(1,2,figsize=(11,4.5),sharey=True)
for ax,model in zip(axes,['7b','14b']):
 for c,color,marker,ls in [('STEP','#2864a5','o','-'),('NAME','#cc572f','x','--')]:
  rr=[x for x in rows if x['model']==model and x['condition']==c]
  ax.plot([x['length'] for x in rr],[100*x['rate'] for x in rr],label=c,color=color,marker=marker,ls=ls,lw=2,ms=7,markerfacecolor='white',clip_on=False)
 ax.set(title=f'Qwen2.5-{model.upper()}-Instruct | pure prompt',xlabel='Number of tool calls (L)',xticks=range(2,10),xlim=(1.85,9.15),ylim=(-3,100),yticks=range(0,101,20));ax.grid(alpha=.2);ax.legend()
axes[0].set_ylabel('Strict complete-trajectory success (%)')
fig.suptitle('STEP vs NAME: short exploration at lengths 2–9',fontsize=14)
fig.text(.5,.015,'32 shared questions per length; greedy; no adapters. L2/L5 reused from prior exploration; L3/L4/L6–L9 newly measured.',ha='center',fontsize=9)
fig.tight_layout(rect=(0,.055,1,.96))
for ext in ['png','pdf','svg']:fig.savefig(R/f'accuracy-vs-length-2-9.{ext}',dpi=200)
plt.close(fig)
lines=['# 7B/14B prompt-only short evaluation at lengths 2–9','','Original weights without adapters. STEP/NAME prompts, tool definitions, data rules, chat templates, greedy decoding, and strict scoring are unchanged. Each point uses 32 shared examples. L2/L5 reuse earlier exploration; the other six lengths add 768 new outputs. Neither the old 512-example formal evaluation nor GRPO outputs are included.','','![Accuracy by length](accuracy-vs-length-2-9.png)','','| L | 7B STEP | 7B NAME | 14B STEP | 14B NAME | Source |','|---:|---:|---:|---:|---:|---|']
for L in range(2,10):
 cells=[]
 for m,c in [('7b','STEP'),('7b','NAME'),('14b','STEP'),('14b','NAME')]:
  x=next(x for x in rows if x['model']==m and x['condition']==c and x['length']==L);cells.append(f'{x["correct"]}/32 ({x["rate"]:.1%})')
 lines.append('| '+str(L)+' | '+' | '.join(cells)+' | '+('Reused' if L in [2,5] else 'New')+' |')
lines+=['',f'Termination reasons for new outputs: {dict(ends)}. All 16 jobs exited normally. Raw outputs and token IDs, example-level strict scores, capacity prechecks, configurations, logs, and failure records are retained in the model subdirectories. Header compliance is scored separately. Old auxiliary first-error labels are not treated as reliable omitted/extra-call classifications.','', 'Generation limits follow the existing formula based on correct target length: 256 for L3/L4 and 512 for L6–9, identical across models and conditions at each length. This is an exploratory short evaluation with 32 examples per point. A score of 0/32 does not establish zero population accuracy, and local differences are not independent formal confirmation. These are not post-GRPO length curves.']
(R/'REPORT.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(dict(new_outputs=count,endings=dict(ends),rates=[(x['model'],x['condition'],x['length'],x['correct']) for x in rows]),indent=2))
