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
labels={'JJ':'一起训练 / 一起训练','SJ':'只训顺序 / 一起训练','JE':'一起训练 / 只训操作','SE':'只训顺序 / 只训操作'}
lines=['# 一起训练与分开训练，都用相同方式检验乘积预测',
       '以下固定512步，全部为新协议下的匹配对照，不替代第一阶段原名称组基准。顺序与操作两列分别在程序提供正确另一部分的条件下测量；实际列没有正确答案帮助。',
       '先在每个seed、每个长度内计算乘积，再汇总。因而all行的预测值不等于把显示出来的两个总体平均率简单相乘。256步和逐seed记录见JSON。',
       '', '|模型|谁写名称 / 谁写操作|长度|顺序准确率|操作准确率|分层乘积预测|实际成功率|误差pp|',
       '|---|---|---|---:|---:|---:|---:|---:|']
for length in ['all',3,4,5,6,8]:
    for row in records:
        if row['step']!=512 or row['length']!=length:continue
        m=row['mean'];values='|'.join(f'{100*m[k]:.2f}%' for k in ['sequence','operations','product','actual'])
        lines.append(f'|{row["model"]}|{labels[row["route"]]}|{length}|{values}|{100*m["error"]:+.2f}|')
lines += ['', '解释：如果一起训练模型也能被同样的两个子任务分数近似预测，乘积吻合支持的是分解作为性能诊断的合理性；不能单靠它宣称分开训练让模型内部形成了独立模块。学习收益应由同协议训练方式对照、真实组件替换和上下文干预分别判断。']
(R/'ALL_ROUTE_PREDICTIONS.md').write_text('\n'.join(lines)+'\n');print('All-route prediction cells:',len(records))
