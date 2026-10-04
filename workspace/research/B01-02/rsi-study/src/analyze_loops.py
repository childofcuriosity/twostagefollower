import statistics
import numpy as np
from scipy.stats import t
from common import *
rows=[];proposals=[]
for run in sorted((ROOT/'runs').glob('loop-*')):
 if not run.is_dir():continue
 parts=run.name.split('-');domain,c,seed=parts[1],parts[2],int(parts[3][1:])
 for p in sorted(run.glob('round*/summary.json')):
  v=json.loads(p.read_text());row=dict(domain=domain,condition=c,seed=seed,round=v['round'],proposal_compression=statistics.mean(r['compression'] for r in v['proposal']),proposal_diversity=statistics.mean(r['unique_semantics'] for r in v['proposal']))
  for key,value in v['execution'].items():row[key+'_accuracy']=value['accuracy'];row[key+'_program_accuracy']=value['program_accuracy']
  if 'training' in v:row.update(v['training']['counts'])
  rows.append(row)
  for r in v['proposal']:proposals.append(dict(domain=domain,condition=c,seed=seed,round=v['round'],**r))
(ROOT/'analysis/loop-rows.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows));(ROOT/'analysis/loop-proposal-rows.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in proposals))
summary={}
for domain in ['digits','strings']:
 summary[domain]={}
 for c in sorted({r['condition'] for r in rows if r['domain']==domain}):
  summary[domain][c]={}
  for rnd in range(4):
   rs=[r for r in rows if r['domain']==domain and r['condition']==c and r['round']==rnd]
   if len(rs)==3:summary[domain][c][str(rnd)]={k:statistics.mean(r[k] for r in rs) for k in ['short_accuracy','family_accuracy','pressure_accuracy','family_program_accuracy','proposal_compression','proposal_diversity']}
branches=[]
for p in (ROOT/'runs').glob('branch-*/summary.json'):
 v=json.loads(p.read_text());a=v['args'];row=dict(domain=a['domain'],source=a['source'],seed=a['seed'],start_sha=v['source_adapter_sha256'])
 for split in ['short','family','pressure']:row[split]=v['execution'][split]['accuracy'];row[split+'_gain']=row[split]-v['before'][split]['accuracy']
 branches.append(row)
comparisons={}
for domain in ['digits','strings']:
 comparisons[domain]={}
 for split in ['short','family','pressure']:
  dif=[]
  for seed in [11,22,33]:
   a=[r for r in branches if r['domain']==domain and r['seed']==seed and r['source']=='base'];b=[r for r in branches if r['domain']==domain and r['seed']==seed and r['source']=='updated']
   if a and b:assert a[0]['start_sha']==b[0]['start_sha'];dif.append(a[0][split]-b[0][split])
  if len(dif)==3:
   mean=statistics.mean(dif);width=float(t.ppf(.975,2)*np.std(dif,ddof=1)/np.sqrt(3));comparisons[domain][split]=dict(base_source_minus_updated=mean,seed_differences=dif,t_interval_95=[mean-width,mean+width])
result=dict(completed_loops=len(list((ROOT/'runs').glob('loop-*/summary.json'))),expected_loops=24,summary=summary,branch_rows=branches,branch_comparisons=comparisons)
(ROOT/'analysis/loop-results.json').write_text(json.dumps(result,indent=2));print('Loops',result['completed_loops'],'of 24; branches',len(branches),'of 12');print(json.dumps(summary,indent=2));print(json.dumps(comparisons,indent=2))
