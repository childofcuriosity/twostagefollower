"""Audit the frozen fresh set and report every registered paired contrast."""
import collections,hashlib,json
import numpy as np
from common import R,MODELS,write,Path
from context_audit import audit_context
from transformers import AutoTokenizer

F=R/'fresh-confirmation'


def main():
    jobs=json.loads((F/'analysis/jobs.json').read_text());lookup={};files={};total=events=0
    expected=list(map(json.loads,(F/'data/independent.jsonl').read_text().splitlines()))
    for model in ['qwen3b','qwen32b']:
        tok=AutoTokenizer.from_pretrained(MODELS[model],local_files_only=True)
        for job in [j for j in jobs if j['model']==model]:
            root=F/'runs'/job['id'];d=json.loads((root/'complete.json').read_text())
            assert d['job']==job and len(d['summary'])==1
            for source in d['summary']:
                assert (source['route'],source['scope'])==(job['route'],job['scope'])
                path=Path(source['source']);raw=path.read_bytes();files[str(path)]=hashlib.sha256(raw).hexdigest()
                rows=list(map(json.loads,raw.splitlines()));assert len(rows)==len(expected)==source['n']==400
                for row,ref in zip(rows,expected):
                    assert (row['id'],row['x'],row['chain'])==(ref['id'],ref['x'],ref['chain'])
                    assert row['operation_context']==source['scope'];events+=audit_context(row,tok)
                assert sum(r['grade']['complete'] for r in rows)==source['complete']
                lookup[model,job['seed'],source['route'],source['scope']]=rows;total+=len(rows)
    assert total==9600
    for p,h in json.loads((F/'analysis/source-freeze.json').read_text()).items():
        assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
    write(F/'analysis/completion-audit.json',dict(complete=True,trajectories=total,events=events,files=files,
          no_oracle_inputs=True,actual_generation_contexts_reconstructed=True))
    records=[];rng=np.random.default_rng(20260925)
    for model in ['qwen3b','qwen32b']:
        for ar,ac,br,bc in [('JJ','local','JJ','full'),('SE','local','SE','full'),('SE','local','JJ','local'),('SE','full','JJ','full')]:
            for length in ['all',3,4,5,6,8]:
                seeds=[];clusters=collections.defaultdict(list)
                for seed in [11,22,33]:
                    aa=lookup[model,seed,ar,ac];bb=lookup[model,seed,br,bc]
                    pairs=[(a,b) for a,b in zip(aa,bb) if length=='all' or len(a['chain'])==length]
                    scores={}
                    for key in ['sequence_correct','all_expansions_correct','complete']:
                        scores[key]=dict(a=sum(a['grade'][key] for a,b in pairs)/len(pairs),b=sum(b['grade'][key] for a,b in pairs)/len(pairs))
                    for a,b in pairs:
                        assert a['id']==b['id'];clusters[tuple(a['chain'])].append(int(a['grade']['complete'])-int(b['grade']['complete']))
                    seeds.append(dict(seed=seed,n=len(pairs),scores=scores,delta=scores['complete']['a']-scores['complete']['b'],
                                      gain=sum(a['grade']['complete'] and not b['grade']['complete'] for a,b in pairs),
                                      loss=sum(b['grade']['complete'] and not a['grade']['complete'] for a,b in pairs)))
                values=np.array([sum(v) for v in clusters.values()]);sizes=np.array([len(v) for v in clusters.values()])
                ix=rng.integers(len(sizes),size=(2000,len(sizes)));boot=values[ix].sum(1)/sizes[ix].sum(1)
                records.append(dict(model=model,a_route=ar,a_context=ac,b_route=br,b_context=bc,length=length,seeds=seeds,
                                    mean_delta=sum(s['delta'] for s in seeds)/3,all_three_seeds_improve=all(s['delta']>0 for s in seeds),
                                    program_bootstrap95=np.quantile(boot,[.025,.975]).tolist()))
    write(F/'analysis/comparisons.json',dict(records=records,note='Pre-frozen new programs, all routes and seeds retained. Bootstrap resamples programs and is conditional on three trained seeds.'))
    lines=['# 新程序确认结果',
           '数据在任何局部上下文真实模型推理前冻结，100个新工具组合×4个输入。不是新工具学习，也不是现实Agent任务。全部模型固定512步。',
           'J/J表示一起训练模型负责两部分；S/E表示名称和操作由各自专用模型负责。full保留全部历史，local仅使操作部分看到当前工具和实际状态。',
           '', '|模型|比较|长度|新方案完整成功|对照完整成功|差值pp|三个seed差值pp|',
           '|---|---|---|---:|---:|---:|---|']
    for r in records:
        a=sum(s['scores']['complete']['a'] for s in r['seeds'])/3;b=sum(s['scores']['complete']['b'] for s in r['seeds'])/3
        delta=' / '.join(f'{100*s["delta"]:+.2f}' for s in r['seeds'])
        label=f'{r["a_route"]} {r["a_context"]} 对 {r["b_route"]} {r["b_context"]}'
        lines.append(f'|{r["model"]}|{label}|{r["length"]}|{100*a:.2f}%|{100*b:.2f}%|{100*r["mean_delta"]:+.2f}|{delta}|')
    lines += ['', '逐seed两子任务准确率、原始对错计数和程序成簇区间见analysis/comparisons.json；全量实际输入与输出审计见analysis/completion-audit.json。']
    (F/'REPORT.md').write_text('\n'.join(lines)+'\n');print('FRESH AUDIT AND COMPARISONS PASSED',total,len(records))


if __name__=='__main__':main()
