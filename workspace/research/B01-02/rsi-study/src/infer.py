from common import *
import statistics
import numpy as np
from scipy.stats import t
rows=[json.loads(l) for l in (ROOT/'analysis/loop-rows.jsonl').read_text().splitlines()]
prows=[json.loads(l) for l in (ROOT/'analysis/loop-proposal-rows.jsonl').read_text().splitlines()]
def interval(values):
 mean=statistics.mean(values);width=float(t.ppf(.975,len(values)-1)*np.std(values,ddof=1)/np.sqrt(len(values)))
 return dict(mean=mean,seed_differences=values,t_interval_95=[mean-width,mean+width])
comparisons={}
for domain in ['digits','strings']:
 comparisons[domain]={}
 for condition in ['frozen','replay','joint','shuffled']:
  if domain=='strings' and condition in ['replay','shuffled']:continue
  result={}
  for metric in ['proposal_compression','short_accuracy','family_accuracy','pressure_accuracy']:
   dif=[]
   for seed in [11,22,33]:
    def get(c):return next(r[metric] for r in rows if r['domain']==domain and r['condition']==c and r['seed']==seed and r['round']==3)
    dif.append(get(condition)-get('shared'))
   result[metric]=interval(dif)
  comparisons[domain][condition+'-shared']=result
rng=np.random.default_rng(939512);indices=rng.integers(0,16,(5000,16));cluster={}
for domain in ['digits','strings']:
 cluster[domain]={}
 for condition in ['frozen','replay','joint','shuffled']:
  if domain=='strings' and condition in ['replay','shuffled']:continue
  dif=[]
  for family in range(16,32):
   a=[r['compression'] for r in prows if r['domain']==domain and r['condition']==condition and r['round']==3 and r['family']==family];b=[r['compression'] for r in prows if r['domain']==domain and r['condition']=='shared' and r['round']==3 and r['family']==family]
   assert len(a)==len(b)==3;dif.append(statistics.mean(a)-statistics.mean(b))
  boot=np.array(dif)[indices].mean(axis=1);cluster[domain][condition+'-shared']=dict(family_differences=dif,family_bootstrap_95=np.quantile(boot,[.025,.975]).tolist())
copy_baseline={}
for domain in ['digits','strings']:
 test=json.loads((ROOT/f'data/loop-eval-{domain}.json').read_text());import loop_data as ld
 copy_baseline[domain]={}
 for split in ['short','family','pressure']:
  rs=[r for r in test if r['split']==split];copy_baseline[domain][split]=statistics.mean(tuple(ld.engine(domain).execute(r['x'],r['ops']))==tuple(r['x']) for r in rs)
# Post-hoc degraded-proposer stress branches, kept separate from preregistered comparisons.
branches=json.loads((ROOT/'analysis/loop-results.json').read_text())['branch_rows'];legacy={}
for domain in ['digits','strings']:
 legacy[domain]={}
 for source in ['base','updated']:
  legacy[domain][source+'-legacy']={}
  for split in ['short','family','pressure']:
   dif=[]
   for seed in [11,22,33]:
    a=next(r for r in branches if r['domain']==domain and r['source']==source and r['seed']==seed)
    b=next(r for r in branches if r['domain']==domain and r['source']=='legacy' and r['seed']==seed)
    assert a['start_sha']==b['start_sha'];dif.append(a[split]-b[split])
   legacy[domain][source+'-legacy'][split]=interval(dif)
(ROOT/'analysis/loop-inference.json').write_text(json.dumps(dict(round3_seed_comparisons=comparisons,proposal_family_intervals=cluster,copy_input_baseline=copy_baseline,posthoc_legacy_comparisons=legacy,interpretation='Paired three-training-seed intervals and conditional family bootstrap are different uncertainty summaries. No multiplicity-adjusted confirmatory claim.'),indent=2))
print(json.dumps(comparisons,indent=2));print('copy baseline',copy_baseline);print('posthoc legacy',json.dumps(legacy,indent=2))
