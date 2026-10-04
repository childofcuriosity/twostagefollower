"""Paired actual-composition effects and complete checkpoint trajectories."""
import collections,json
import numpy as np
from common import *

def main():
    d=json.loads((R/'analysis/results.json').read_text());lookup={};out=[];rng=np.random.default_rng(20260925)
    jobs={j['id']:j for j in json.loads((R/'analysis/jobs.json').read_text())}
    for src in d['sources']:
        if src['split']!='independent':continue
        j=jobs[src['job']]
        if j['kind']=='curve' and (j['condition']!='joint' or src['mode']!='joint'):continue
        label='JJ' if j['kind']=='curve' else src['mode']
        lookup[j['model'],j['seed'],src['step'],label]=list(map(json.loads,Path(src['source']).read_text().splitlines()))
    comparisons=[(step,mode,step) for step in [256,512] for mode in ['SE','SJ','JE']]+[(256,'SE',512)]
    for model in ['qwen3b','qwen32b']:
        for step,mode,baseline_step in comparisons:
            for length in ['all',3,4,5,6,8]:
                groups=collections.defaultdict(list);seeds=[]
                for seed in [11,22,33]:
                    aa=lookup.get((model,seed,step,mode));bb=lookup.get((model,seed,baseline_step,'JJ'))
                    if aa is None or bb is None:continue
                    base={r['id']:r for r in bb};pairs=[]
                    for r in aa:
                        if length!='all' and len(r['chain'])!=length:continue
                        ref=base[r['id']];assert (r['x'],r['chain'])==(ref['x'],ref['chain'])
                        a=int(r['grade']['complete']);b=int(ref['grade']['complete']);pairs.append((a,b));groups[tuple(r['chain'])].append(a-b)
                    seeds.append(dict(seed=seed,n=len(pairs),composition=sum(a for a,b in pairs)/len(pairs),baseline=sum(b for a,b in pairs)/len(pairs),delta=sum(a-b for a,b in pairs)/len(pairs),gain=sum(a and not b for a,b in pairs),loss=sum(b and not a for a,b in pairs)))
                if len(seeds)!=3:continue
                vals=np.array([sum(v) for v in groups.values()]);ns=np.array([len(v) for v in groups.values()]);ix=rng.integers(len(ns),size=(2000,len(ns)));boot=vals[ix].sum(axis=1)/ns[ix].sum(axis=1)
                out.append(dict(model=model,mode=mode,step=step,baseline_step=baseline_step,length=length,seeds=seeds,mean_delta=float(vals.sum()/ns.sum()),program_bootstrap95=np.quantile(boot,[.025,.975]).tolist(),all_three_seeds_improve=all(s['delta']>0 for s in seeds),worst_seed_delta=min(s['delta'] for s in seeds)))
    write(R/'analysis/paired-comparisons.json',dict(results=out,note='No oracle in either arm. Program bootstrap conditional on 3 seeds, descriptive not multiplicity corrected. SE256 vs JJ512 approximately matches summed training examples/steps; same-step two-specialist SE costs twice a single trained adapter.'))
    lines=['# 实际完整执行：配对比较','J=一起训练，S=只训练顺序，E=只训练操作。S/E表示S写名称、E写操作。全部结果无程序正确答案帮助。差值单位百分点；括号是三个seed各自差值。下表汇总五种长度共480题，逐长度见JSON及主报告。','|模型|执行模型|各adapter步数|一起训练基准步数|平均差值|三个seed差值|最差seed差值|','|---|---|---:|---:|---:|---|---:|']
    for x in out:
        if x['length']=='all':lines.append(f'|{x["model"]}|{x["mode"]}|{x["step"]}|{x["baseline_step"]}|{100*x["mean_delta"]:+.2f}|'+ ' / '.join(f'{100*s["delta"]:+.2f}' for s in x['seeds'])+f'|{100*x["worst_seed_delta"]:+.2f}|')
    (R/'COMPOSITION_EFFECTS.md').write_text('\n'.join(lines)+'\n')
    # Curve changes, no selected test optimum.
    g=collections.defaultdict(collections.Counter)
    for x in d['results']:
        if x['kind']!='curve':continue
        group='short_dev' if x['split']=='dev' else 'independent' if x['split'].startswith('length') else 'long_dev'
        g[x['model'],x['condition'],x['seed'],x['step'],x['mode'],group].update(x['counts'])
    curves=[]
    for model in ['qwen3b','qwen32b']:
        for c,m in [('joint','joint'),('joint','order_oracle'),('order_oracle','order_oracle'),('joint','operation_oracle'),('operation_oracle','operation_oracle')]:
            for seed in [11,22,33]:
                points=[]
                for step in [64,128,256,512]:
                    z={group:g.get((model,c,seed,step,m,group)) for group in ['short_dev','long_dev','independent']}
                    if any(not v for v in z.values()):continue
                    points.append(dict(step=step,**{k:v['complete']/v['n'] for k,v in z.items()}))
                if len(points)!=4:continue
                curves.append(dict(model=model,condition=c,mode=m,seed=seed,points=points,first_observed_short_dev_99=next((p['step'] for p in points if p['short_dev']>=.99),None),long_change_64_to_512=points[-1]['independent']-points[0]['independent'],long_adjacent_changes=[points[i]['independent']-points[i-1]['independent'] for i in range(1,4)]))
    write(R/'analysis/checkpoint-curves.json',dict(curves=curves,note='99% short-dev mastery is descriptive first observed checkpoint, not actual crossing time. No checkpoint selected using independent test performance.'))
    print('Paired composition contrasts',len(out),'complete curves',len(curves))
if __name__=='__main__':main()
