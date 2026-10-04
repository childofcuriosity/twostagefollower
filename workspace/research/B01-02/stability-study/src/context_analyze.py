"""Pair every fixed local-context result with the full-context counterpart."""
import collections,json
import numpy as np
from common import R,write,Path

C=R/'context-intervention'


def main():
    original=json.loads((R/'analysis/results.json').read_text())
    jobs={j['id']:j for j in json.loads((R/'analysis/jobs.json').read_text())};full={};local={}
    for src in original['sources']:
        if src['step']!=512:continue
        j=jobs[src['job']]
        if j['kind']=='curve' and (j['condition']!='joint' or src['mode']!='joint'):continue
        route='JJ' if j['kind']=='curve' else src['mode']
        full[j['model'],j['seed'],route,src['split']]=list(map(json.loads,Path(src['source']).read_text().splitlines()))
    for p in sorted((C/'runs').glob('*/complete.json')):
        d=json.loads(p.read_text());j=d['job']
        if j['kind']=='control':continue
        for src in d['summary']:
            local[j['model'],j['seed'],src['route'],src['split']]=list(map(json.loads,Path(src['source']).read_text().splitlines()))
    records=[];rng=np.random.default_rng(20260925)
    contrasts=[(route,'local',route,'full') for route in ['JJ','SJ','JE','SE']]
    contrasts += [(route,'local','JJ','local') for route in ['SJ','JE','SE']]
    for model in ['qwen3b','qwen32b']:
        for ar,ac,br,bc in contrasts:
            for length in ['all',3,4,5,6,8]:
                seeds=[];clusters=collections.defaultdict(list)
                for seed in [11,22,33]:
                    a=(local if ac=='local' else full).get((model,seed,ar,'independent'))
                    b=(local if bc=='local' else full).get((model,seed,br,'independent'))
                    if a is None or b is None:continue
                    ref={r['id']:r for r in b};pairs=[]
                    for r in a:
                        if length!='all' and len(r['chain'])!=length:continue
                        q=ref[r['id']];assert (r['x'],r['chain'])==(q['x'],q['chain'])
                        pairs.append((r,q));clusters[tuple(r['chain'])].append(int(r['grade']['complete'])-int(q['grade']['complete']))
                    metrics={}
                    for key in ['sequence_correct','all_expansions_correct','complete']:
                        metrics[key]=dict(a=sum(r['grade'][key] for r,q in pairs)/len(pairs),b=sum(q['grade'][key] for r,q in pairs)/len(pairs))
                    seeds.append(dict(seed=seed,n=len(pairs),metrics=metrics,
                                      delta=metrics['complete']['a']-metrics['complete']['b'],
                                      gain=sum(r['grade']['complete'] and not q['grade']['complete'] for r,q in pairs),
                                      loss=sum(q['grade']['complete'] and not r['grade']['complete'] for r,q in pairs)))
                if len(seeds)!=3:continue
                values=np.array([sum(v) for v in clusters.values()]);sizes=np.array([len(v) for v in clusters.values()])
                ix=rng.integers(len(sizes),size=(2000,len(sizes)));boot=values[ix].sum(1)/sizes[ix].sum(1)
                records.append(dict(model=model,a_route=ar,a_context=ac,b_route=br,b_context=bc,length=length,seeds=seeds,
                                    mean_delta=sum(s['delta'] for s in seeds)/3,
                                    all_three_seeds_improve=all(s['delta']>0 for s in seeds),
                                    program_bootstrap95=np.quantile(boot,[.025,.975]).tolist()))
    assert len(records)==84,len(records)
    write(C/'analysis/comparisons.json',dict(records=records,note='Same checkpoints and rows; all operations model-generated from actual state. Program bootstrap conditional on 3 seeds. Local context removes both prior trace and global future-tool list from operation input.'))
    lines=['# Operations see only the current tool and state: actual execution controls',
           'All names and operations remain model-generated, with no program-supplied correct answers. Local context changes only operation inputs; the sequence component retains full history.',
           'J=joint training, S=sequence-only training, E=operation-only training. All checkpoints are fixed at 512 steps. Means do not replace seed-wise differences.',
           '', '|Model|Comparison|Tools|New full-task success|Control full-task success|Difference pp|Three seed differences pp|',
           '|---|---|---|---:|---:|---:|---|']
    for row in records:
        a=sum(s['metrics']['complete']['a'] for s in row['seeds'])/3
        b=sum(s['metrics']['complete']['b'] for s in row['seeds'])/3
        diff=' / '.join(f'{100*s["delta"]:+.2f}' for s in row['seeds'])
        label=f'{row["a_route"]} {row["a_context"]} versus {row["b_route"]} {row["b_context"]}'
        lines.append(f'|{row["model"]}|{label}|{row["length"]}|{100*a:.2f}%|{100*b:.2f}%|{100*row["mean_delta"]:+.2f}|{diff}|')
    lines += ['', 'Both subtask accuracies are listed by seed in analysis/comparisons.json. This intervention changes operation-context scope, not trained weights; changes cannot be attributed solely to token length.']
    (C/'REPORT.md').write_text('\n'.join(lines)+'\n');print('Context paired cells:',len(records))


if __name__=='__main__':main()
