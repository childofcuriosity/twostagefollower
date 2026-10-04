"""Keep primary scores unchanged; quantify first-difference attribution exceptions."""
import collections,json
from common import R,write,Path

data=json.loads((R/'analysis/results.json').read_text())
jobs={j['id']:j for j in json.loads((R/'analysis/jobs.json').read_text())};lookup={}
for src in data['sources']:
    if src['split']!='independent' or src['step'] not in [256,512]:continue
    job=jobs[src['job']]
    if job['kind']=='curve' and (job['condition']!='joint' or src['mode']!='joint'):continue
    mode='JJ' if job['kind']=='curve' else src['mode']
    if mode not in ['JJ','SJ','JE']:continue
    lookup[job['model'],job['seed'],src['step'],mode]={r['id']:r for r in map(json.loads,Path(src['source']).read_text().splitlines())}
exceptions=json.loads((R/'analysis/attribution.json').read_text())['exceptions']
ids=collections.defaultdict(set)
for row in exceptions:ids[row['model'],row['seed'],row['step'],row['mode']].add(row['id'])
records=[]
for model in ['qwen3b','qwen32b']:
    for step in [256,512]:
        for mode in ['SJ','JE']:
            seeds=[]
            for seed in [11,22,33]:
                current=lookup[model,seed,step,mode];baseline=lookup[model,seed,step,'JJ']
                exceptional=ids[model,seed,step,mode]
                changes={key:int(row['grade']['complete'])-int(baseline[key]['grade']['complete']) for key,row in current.items()}
                seeds.append(dict(seed=seed,n=len(changes),net_gain_all=sum(changes.values()),
                                  attribution_exceptions=len(exceptional),exceptional_net_gain=sum(changes[k] for k in exceptional),
                                  exceptional_gains=sum(changes[k]>0 for k in exceptional),exceptional_losses=sum(changes[k]<0 for k in exceptional)))
            records.append(dict(model=model,step=step,mode=mode,seeds=seeds,
                                primary_net_gain=sum(s['net_gain_all'] for s in seeds),
                                exceptional_rows=sum(s['attribution_exceptions'] for s in seeds),
                                exceptional_net_gain=sum(s['exceptional_net_gain'] for s in seeds)))
write(R/'analysis/exception-sensitivity.json',dict(records=records,note=(
    'Primary scores are unchanged and retain all rows. Exceptions are first differing tokens in the unchanged '
    'adapter role despite identical within-row textual prefixes. Dynamic batch composition/numerics is a '
    'plausible but unproven explanation. This file quantifies their contribution, not corrected accuracy.')))
print([(r['model'],r['step'],r['mode'],r['primary_net_gain'],r['exceptional_rows'],r['exceptional_net_gain']) for r in records])
