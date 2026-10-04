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
lines=['# Function-equivalence strata in the new confirmation set: post hoc diagnosis',
       'Primary results still include all 400 examples. This stratification was added after some outputs existed to explain dataset scope, not to promote a better-performing subset to the primary result. The two groupings overlap and are not two additional independent experiments.',
       'All earlier data includes training, development, old tests, and the old independent set, not just training data. Groups use exact affine signatures of final functions; tool sequences themselves are all distinct from earlier data.',
       '', '|Model|Training|Function reference set|Equivalent function seen before|Programs / functions|Full-history success|Local-operation-input success|Three seed changes pp|',
       '|---|---|---|---|---|---:|---:|---|']
for r in results:
    label='Joint training' if r['route']=='JJ' else 'Two specialist models'
    reference='Training set' if r['criterion']=='equivalent_to_training_function' else 'All earlier data'
    deltas=' / '.join(f'{100*s["delta"]:+.2f}' for s in r['seeds'])
    lines.append(f'|{r["model"]}|{label}|{reference}|{"Yes" if r["function_seen"] else "No"}|{r["programs"]} / {r["unique_functions"]}|{100*r["mean_full"]:.2f}%|{100*r["mean_local"]:.2f}%|{deltas}|')
(F/'SEMANTIC_STRATA.md').write_text('\n'.join(lines)+'\n');print('Semantic strata:',len(results))
