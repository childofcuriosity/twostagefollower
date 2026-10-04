"""Fixed-seed gain/loss examples and first changed output, including exceptions."""
import collections,json,random
from common import R,Path,write
from protocol import NAMES,body
from attribution import first_difference


def main():
    lookup={};original=json.loads((R/'analysis/results.json').read_text())
    jobs={j['id']:j for j in json.loads((R/'analysis/jobs.json').read_text())}
    for src in original['sources']:
        if src['step']!=512 or src['split']!='independent':continue
        j=jobs[src['job']]
        if j['kind']=='curve' and (j['condition']!='joint' or src['mode']!='joint'):continue
        route='JJ' if j['kind']=='curve' else src['mode']
        lookup['old',j['model'],j['seed'],route,'full']=list(map(json.loads,Path(src['source']).read_text().splitlines()))
    for directory,dataset in [('context-intervention','old'),('fresh-confirmation','fresh')]:
        for path in sorted((R/directory/'runs').glob('*/complete.json')):
            d=json.loads(path.read_text());j=d['job']
            if j['kind']=='control':continue
            for src in d['summary']:
                if dataset=='old' and src['split']!='independent':continue
                scope='local' if dataset=='old' else src['scope']
                lookup[dataset,j['model'],j['seed'],src['route'],scope]=list(map(json.loads,Path(src['source']).read_text().splitlines()))
    counts=collections.defaultdict(collections.Counter);pools=collections.defaultdict(list)
    functional=collections.defaultdict(collections.Counter)
    for dataset in ['old','fresh']:
        for model in ['qwen3b','qwen32b']:
            for route in ['JJ','SE']:
                for seed in [11,22,33]:
                    aa=lookup[dataset,model,seed,route,'full'];bb=lookup[dataset,model,seed,route,'local']
                    for a,b in zip(aa,bb):
                        assert a['id']==b['id']
                        z=functional[dataset,model,route,seed,len(a['chain'])];z['n']+=1
                        for label,row in [('full',a),('local',b)]:
                            z[label+'_strict']+=row['grade']['complete']
                            z[label+'_sequence_and_final_state']+=bool(row['grade']['sequence_correct'] and row['grade']['final_state']==row['grade']['expected'])
                        gain=b['grade']['complete'] and not a['grade']['complete']
                        loss=a['grade']['complete'] and not b['grade']['complete']
                        label='gain' if gain else 'loss' if loss else 'same_correctness'
                        c=counts[dataset,model,route];c[label]+=1
                        if not (gain or loss):continue
                        diff=first_difference(a,b)
                        category='no_shared_event_difference' if diff is None else diff['phase']
                        c['first_difference:'+category]+=1
                        case=dict(seed=seed,id=a['id'],x=a['x'],chain=[NAMES[t] for t in a['chain']],
                                  full_stop=a['stop'],local_stop=b['stop'],difference=diff)
                        if diff is not None and diff['phase']=='body' and diff['same_prefix']:
                            index=sum(e['phase']=='body' for e in a['events'][:diff['event']])
                            call=a['calls'][index]
                            case['tool_position']=index+1;case['tool']=NAMES[call['tool']]
                            case['actual_state_before_call']=call['input_state']
                            case['correct_body_for_actual_state']=body(call['tool'],tuple(call['input_state']))[0]
                        pools[dataset,model,route,label].append(case)
    rng=random.Random(20260925)
    samples=[dict(dataset=k[0],model=k[1],route=k[2],change=k[3],population=len(v),cases=rng.sample(v,min(3,len(v)))) for k,v in sorted(pools.items())]
    write(R/'analysis/context-cases.json',dict(counts=[dict(dataset=k[0],model=k[1],route=k[2],counts=dict(v)) for k,v in sorted(counts.items())],samples=samples,
          metric_sensitivity=[dict(dataset=k[0],model=k[1],route=k[2],seed=k[3],length=k[4],counts=dict(v)) for k,v in sorted(functional.items())],
          note='Random samples of gains AND losses using a fixed analysis seed. Correct body is computed only after inference for explanation, never fed into generation. Header-first changes are retained, not silently attributed to operation context. Primary success requires faithful primitive sequence and each intermediate state; the additional relaxed metric keeps correct names/termination/final state but allows unfaithful intermediate traces, and never replaces the primary metric.'))
    print('Context case populations:',len(counts),'sample groups:',len(samples))


if __name__=='__main__':main()
