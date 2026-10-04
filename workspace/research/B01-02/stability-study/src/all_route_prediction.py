"""Apply the same marginal-product diagnostic to every training combination."""
import json
from common import R,write

data=json.loads((R/'analysis/results.json').read_text());lookup={}
for row in data['results']:
    if row['split'].startswith('length'):
        lookup[row['model'],row['seed'],row['step'],row['kind'],row['condition'],row['mode'],row['length']]=row['counts']
records=[]
for model in ['qwen3b','qwen32b']:
    for step in [256,512]:
        for route in ['JJ','SJ','JE','SE']:
            per_length=[]
            for length in [3,4,5,6,8]:
                seeds=[]
                for seed in [11,22,33]:
                    s=lookup[model,seed,step,'curve','joint' if route[0]=='J' else 'operation_oracle','operation_oracle',length]
                    e=lookup[model,seed,step,'curve','joint' if route[1]=='J' else 'order_oracle','order_oracle',length]
                    c=lookup[model,seed,step,'curve' if route=='JJ' else 'compose','joint' if route=='JJ' else None,'joint' if route=='JJ' else route,length]
                    a,b,y=s['complete']/s['n'],e['complete']/e['n'],c['complete']/c['n']
                    seeds.append(dict(seed=seed,n=c['n'],sequence=a,operations=b,product=a*b,actual=y,error=y-a*b))
                per_length.append(dict(model=model,step=step,route=route,length=length,seeds=seeds,
                                       mean={k:sum(s[k] for s in seeds)/3 for k in ['sequence','operations','product','actual','error']}))
            records.extend(per_length)
            seeds=[]
            for seed in [11,22,33]:
                selected=[next(s for s in x['seeds'] if s['seed']==seed) for x in per_length]
                seeds.append(dict(seed=seed,n=sum(s['n'] for s in selected),**{k:sum(s[k] for s in selected)/5 for k in ['sequence','operations','product','actual','error']}))
            records.append(dict(model=model,step=step,route=route,length='all',seeds=seeds,
                                mean={k:sum(s[k] for s in seeds)/3 for k in ['sequence','operations','product','actual','error']}))
write(R/'analysis/all-route-predictions.json',dict(records=records,note=(
    'Identical diagnostic for JJ/SJ/JE/SE. Marginals come from matched correct-other-component tests, '
    'actual comes from no-oracle execution. Products are calculated within each seed and length before averaging; '
    'all-length row is the average of length-specific products. Similar accuracy of this diagnostic for JJ '
    'means product agreement is not evidence specific to separate training.')))
labels={'JJ':'Joint / joint','SJ':'Sequence specialist / joint','JE':'Joint / operation specialist','SE':'Sequence specialist / operation specialist'}
lines=['# Testing product predictions consistently for joint and separate training',
       'All results below use fixed 512-step matched controls under the new protocol, not replacements for the original first-stage NAME baseline. Sequence and operation accuracies are measured with the program supplying the correct other component; actual execution receives no reference-answer assistance.',
       'Compute products within each seed and length, then aggregate. The all-row prediction therefore need not equal the product of the two displayed overall mean rates. See JSON for 256-step and per-seed records.',
       '', '|Model|Name writer / operation writer|Length|Sequence accuracy|Operation accuracy|Stratified product prediction|Actual success|Error pp|',
       '|---|---|---|---:|---:|---:|---:|---:|']
for length in ['all',3,4,5,6,8]:
    for row in records:
        if row['step']!=512 or row['length']!=length:continue
        m=row['mean'];values='|'.join(f'{100*m[k]:.2f}%' for k in ['sequence','operations','product','actual'])
        lines.append(f'|{row["model"]}|{labels[row["route"]]}|{length}|{values}|{100*m["error"]:+.2f}|')
lines += ['', 'If the same two subtask scores also approximately predict jointly trained models, product agreement supports decomposition as a performance diagnostic. It alone does not establish that separate training creates independent internal modules. Learning gains require separate assessment through same-protocol training controls, actual component replacement, and context interventions.']
(R/'ALL_ROUTE_PREDICTIONS.md').write_text('\n'.join(lines)+'\n');print('All-route prediction cells:',len(records))
