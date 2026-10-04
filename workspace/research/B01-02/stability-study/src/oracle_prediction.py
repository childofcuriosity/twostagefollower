"""Can separately measured oracle marginals predict actual composed execution?"""
import collections,json
import numpy as np
from common import R,Path,write

data=json.loads((R/'analysis/results.json').read_text());jobs={j['id']:j for j in json.loads((R/'analysis/jobs.json').read_text())};lookup={}
for source in data['sources']:
    if source['split']!='independent' or source['step'] not in [256,512]:continue
    job=jobs[source['job']]
    if job['kind']=='compose' and source['mode']=='SE':label='actual'
    elif job['kind']=='curve' and job['condition']==source['mode']=='operation_oracle':label='sequence'
    elif job['kind']=='curve' and job['condition']==source['mode']=='order_oracle':label='operations'
    else:continue
    lookup[job['model'],job['seed'],source['step'],label]=list(map(json.loads,Path(source['source']).read_text().splitlines()))
rng=np.random.default_rng(20260925);records=[];bootstraps={}
for model in ['qwen3b','qwen32b']:
    for step in [256,512]:
        for length in ['all',3,4,5,6,8]:
            seed_arrays=[];seeds=[];programs=None
            for seed in [11,22,33]:
                groups=collections.defaultdict(list)
                columns=[lookup[model,seed,step,label] for label in ['sequence','operations','actual']]
                for a,b,c in zip(*columns):
                    assert a['id']==b['id']==c['id']
                    if length!='all' and len(a['chain'])!=length:continue
                    groups[tuple(a['chain'])].append([a['grade']['complete'],b['grade']['complete'],c['grade']['complete']])
                keys=sorted(groups)
                if programs is None:programs=keys
                assert programs==keys and all(len(v)==4 for v in groups.values())
                arr=np.array([groups[k] for k in keys],dtype=float).mean(axis=1)
                seed_arrays.append(arr);a,b,c=arr.mean(axis=0)
                seeds.append(dict(seed=seed,n=4*len(keys),sequence=float(a),operations=float(b),product=float(a*b),actual=float(c),error_actual_minus_product=float(c-a*b)))
            values=np.stack(seed_arrays);ix=rng.integers(len(programs),size=(2000,len(programs)))
            marginals=values[:,ix,:].mean(axis=2)  # seed x bootstrap x component
            bootstrap=(marginals[:,:,2]-marginals[:,:,0]*marginals[:,:,1]).mean(axis=0)
            bootstraps[model,step,length]=bootstrap
            means={k:sum(s[k] for s in seeds)/3 for k in ['sequence','operations','product','actual','error_actual_minus_product']}
            records.append(dict(model=model,step=step,length=length,seeds=seeds,mean=means,
                                error_program_bootstrap95=np.quantile(bootstrap,[.025,.975]).tolist()))
for row in records:
    if row['length']!='all':continue
    strata=[r for r in records if r['model']==row['model'] and r['step']==row['step'] and r['length']!='all']
    predicted=sum(r['mean']['product'] for r in strata)/5
    errors=np.stack([bootstraps[row['model'],row['step'],length] for length in [3,4,5,6,8]]).mean(axis=0)
    row['length_conditioned']=dict(product=predicted,actual=row['mean']['actual'],
        error_actual_minus_product=row['mean']['actual']-predicted,
        error_program_bootstrap95=np.quantile(errors,[.025,.975]).tolist(),
        seed_products=[dict(seed=seed,product=sum(next(s['product'] for s in r['seeds'] if s['seed']==seed) for r in strata)/5) for seed in [11,22,33]])
write(R/'analysis/oracle-prediction.json',dict(records=records,note=(
    'Sequence test receives correct execution; operation test receives correct names and covers requested calls. '
    'Product is calculated within each seed and then averaged. Actual is no-oracle S/E composition. '
    'Paired program bootstrap preserves all three marginal outcomes on the same programs; conditional on three trained seeds. '
    'Pooled-length products and length-conditioned products are both reported, never silently substituted. '
    'Prediction agreement is not proof of latent or statistical independence.')))
lines=['# Can the product of two subtask accuracies predict actual execution?',
       'The sequence column comes from tests where a program correctly executes selected tools; the operation column comes from tests where a program supplies correct names. The final comparison is actual connected execution without program-supplied correct answers.',
       'Compute products within each seed, then average. Error=actual success minus product. Intervals use paired resampling clustered by tool composition, conditional on the three observed training seeds; they do not establish independent internal mechanisms.',
       '', '|Model|Training steps|Length|Sequence accuracy|Operation accuracy|Product|Actual full success|Error pp|95% error interval pp|',
       '|---|---:|---|---:|---:|---:|---:|---:|---|']
for r in records:
    m=r['mean'];ci=r['error_program_bootstrap95']
    vals='|'.join(f'{100*m[k]:.2f}%' for k in ['sequence','operations','product','actual'])
    lines.append(f'|{r["model"]}|{r["step"]}|{r["length"]}|{vals}|{100*m["error_actual_minus_product"]:+.2f}|[{100*ci[0]:+.2f}, {100*ci[1]:+.2f}]|')
lines += ['', '## Overall prediction controlling for task length',
          'Long tasks affect both subtasks. Multiplying rates after pooling lengths mixes in length-induced association. The table first multiplies within each seed and length, then aggregates with equal weights across the tested lengths, without selecting or dropping lengths. The directly pooled product in the all row above is retained.',
          '', '|Model|Steps|Length-stratified product prediction|Actual full success|Error pp|Stratified program-bootstrap interval pp|',
          '|---|---:|---:|---:|---:|---|']
for r in records:
    if r['length']!='all':continue
    z=r['length_conditioned'];ci=z['error_program_bootstrap95']
    lines.append(f'|{r["model"]}|{r["step"]}|{100*z["product"]:.2f}%|{100*z["actual"]:.2f}%|{100*z["error_actual_minus_product"]:+.2f}|[{100*ci[0]:+.2f}, {100*ci[1]:+.2f}]|')
lines += ['', 'These subtask scores measure each model along correct histories. Error-free execution requires both components to remain correct on that path. Multiplying marginal accuracies additionally assumes weak failure association within each length. Prediction agreement supports the usefulness of this statistical approximation, not independent internal learning, and does not exclude loss-weighting or parameter-capacity effects.']
(R/'ORACLE_PREDICTION_CHECK.md').write_text('\n'.join(lines)+'\n')
print('Oracle prediction cells:',len(records))
for r in records:
    if r['step']==512 and r['length'] in ['all',8]:print(r['model'],r['length'],r['mean'],r['error_program_bootstrap95'])
