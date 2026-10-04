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
lines=['# 两个子任务的准确率乘积，能否预测实际执行',
       '顺序列来自程序正确执行所选工具的测试；操作列来自程序提供正确名称的测试。最后一列对照的是真正接起来执行，没有程序正确答案帮助。',
       '乘积先按每个seed计算，再平均。误差=实际成功率−乘积。区间按工具组合成簇配对重采样，仅条件于现有三个训练seed；不能据此证明内部机制独立。',
       '', '|模型|训练步数|长度|顺序准确率|操作准确率|两列乘积|实际完整成功|误差pp|误差95%区间pp|',
       '|---|---:|---|---:|---:|---:|---:|---:|---|']
for r in records:
    m=r['mean'];ci=r['error_program_bootstrap95']
    vals='|'.join(f'{100*m[k]:.2f}%' for k in ['sequence','operations','product','actual'])
    lines.append(f'|{r["model"]}|{r["step"]}|{r["length"]}|{vals}|{100*m["error_actual_minus_product"]:+.2f}|[{100*ci[0]:+.2f}, {100*ci[1]:+.2f}]|')
lines += ['', '## 控制任务长度后的整体预测',
          '长题同时影响两个子任务。直接混合不同长度再相乘，会把长度造成的关联混进来。下表先在每个seed、每个长度内相乘，再按本测试各长度相同权重汇总；没有挑选或删除长度。上表all行的直接混合乘积仍保留。',
          '', '|模型|步数|按长度分层的乘积预测|实际完整成功|误差pp|分层程序bootstrap区间pp|',
          '|---|---:|---:|---:|---:|---|']
for r in records:
    if r['length']!='all':continue
    z=r['length_conditioned'];ci=z['error_program_bootstrap95']
    lines.append(f'|{r["model"]}|{r["step"]}|{100*z["product"]:.2f}%|{100*z["actual"]:.2f}%|{100*z["error_actual_minus_product"]:+.2f}|[{100*ci[0]:+.2f}, {100*ci[1]:+.2f}]|')
lines += ['', '解释边界：这些子任务分数测的是各模型沿正确历史执行时的能力。完整无错执行要求两部分沿这一路径都正确；用两个边际正确率相乘，还要求它们在相同长度内的失败关联不大。预测吻合支持这种统计近似的实用性，不能证明模型内部独立学习，也不能排除损失权重或参数容量的影响。']
(R/'ORACLE_PREDICTION_CHECK.md').write_text('\n'.join(lines)+'\n')
print('Oracle prediction cells:',len(records))
for r in records:
    if r['step']==512 and r['length'] in ['all',8]:print(r['model'],r['length'],r['mean'],r['error_program_bootstrap95'])
