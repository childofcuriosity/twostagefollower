"""Post-hoc, outcome-independent semantic tags; never replace the frozen primary set."""
import collections,json
from common import R,write,Path

F=R/'fresh-confirmation'
assert (F/'analysis/pipeline-complete.json').exists()
tags={tuple(p['chain']):p for p in json.loads((R/'analysis/dataset-semantics.json').read_text())['programs'] if p['dataset']=='fresh'}
lookup={}
for p in sorted((F/'runs').glob('*/complete.json')):
    d=json.loads(p.read_text());j=d['job']
    for src in d['summary']:
        lookup[j['model'],j['seed'],src['route'],src['scope']]=list(map(json.loads,Path(src['source']).read_text().splitlines()))
results=[]
for model in ['qwen3b','qwen32b']:
    for route in ['JJ','SE']:
        for criterion in ['equivalent_to_training_function','equivalent_to_any_prior_function']:
            for seen in [False,True]:
                seeds=[];programs=set();functions=set()
                for seed in [11,22,33]:
                    pairs=[(a,b) for a,b in zip(lookup[model,seed,route,'full'],lookup[model,seed,route,'local']) if tags[tuple(a['chain'])][criterion]==seen]
                    assert pairs
                    for a,b in pairs:
                        assert a['id']==b['id'];programs.add(tuple(a['chain']));functions.add(tags[tuple(a['chain'])]['signature_sha256'])
                    full=sum(a['grade']['complete'] for a,b in pairs);local=sum(b['grade']['complete'] for a,b in pairs)
                    seeds.append(dict(seed=seed,n=len(pairs),full_correct=full,local_correct=local,delta=(local-full)/len(pairs)))
                results.append(dict(model=model,route=route,criterion=criterion,function_seen=seen,programs=len(programs),unique_functions=len(functions),seeds=seeds,
                                    mean_full=sum(s['full_correct']/s['n'] for s in seeds)/3,
                                    mean_local=sum(s['local_correct']/s['n'] for s in seeds)/3))
write(F/'analysis/semantic-strata.json',dict(results=results,note='Post-hoc diagnostic defined by exact affine-function identity, not by model success. All 400 rows remain primary; these overlapping grouping schemes are not additional independent confirmation experiments.'))
lines=['# 新确认集的函数等价性分层：事后诊断',
       '主结果仍包含全部400题。此分层在部分输出产生后新增，只解释数据范围，不把某个较好子集改成主结果。两种分组互相重叠，不能当成额外两套独立实验。',
       '“此前全部数据”包括训练、开发、旧测试和旧独立集；不等于都参与训练。分组依据是最终函数的精确仿射签名，工具序列本身均未与此前数据重复。',
       '', '|模型|训练方式|函数参照集合|等价函数曾出现|程序数 / 函数数|完整历史成功|局部操作输入成功|三个seed变化pp|',
       '|---|---|---|---|---|---:|---:|---|']
for r in results:
    label='一起训练' if r['route']=='JJ' else '两个专用模型'
    reference='训练集' if r['criterion']=='equivalent_to_training_function' else '此前全部数据'
    deltas=' / '.join(f'{100*s["delta"]:+.2f}' for s in r['seeds'])
    lines.append(f'|{r["model"]}|{label}|{reference}|{"是" if r["function_seen"] else "否"}|{r["programs"]} / {r["unique_functions"]}|{100*r["mean_full"]:.2f}%|{100*r["mean_local"]:.2f}%|{deltas}|')
(F/'SEMANTIC_STRATA.md').write_text('\n'.join(lines)+'\n');print('Semantic strata:',len(results))
