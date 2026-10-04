"""Descriptive first-error signatures and same-task gains/losses; no causal labels."""
import collections,json,random
from protocol import R,LIB,NAMES

def signature(row):
    for i,c in enumerate(row['calls']):
        b=c.get('body',{})
        if not b.get('correct',False):
            actual=b.get('ops');wanted=LIB[c['tool']]
            if actual is None:kind='unparsed_body'
            elif actual!=wanted:
                kind='early_EndTool' if len(actual)<len(wanted) and actual==wanted[:len(actual)] else 'wrong_primitive_sequence'
            else:kind='numeric_error'
            return dict(position=i+1,tool=NAMES[c['tool']],kind=kind,expected_ops=wanted,actual_ops=actual)
    return dict(kind='no_incorrect_parsed_body',stop=row['stop'])

def main():
    grouped=collections.defaultdict(collections.Counter);pool=collections.defaultdict(list);training=[]
    for model in ['qwen1.5b','qwen3b','qwen7b','qwen32b']:
        for seed in [11,22,33]:
            for cond in ['joint','order_oracle','operation_oracle']:
                run=R/'runs'/f'{model}-{cond}-s{seed}'
                if not (run/'training-complete.json').exists():continue
                log=list(map(json.loads,(run/'train.jsonl').read_text().splitlines()))
                training.append(dict(model=model,condition=cond,seed=seed,final_loss=log[-1]['loss'],mean_last32_loss=sum(r['loss'] for r in log[-32:])/32,supervised_tokens=log[-1]['supervised_tokens'],input_tokens=log[-1]['input_tokens']))
            for mode in ['order_oracle','operation_oracle']:
                paths=[R/'runs'/f'{model}-{cond}-s{seed}'/f'evaluation-{mode}-independent.jsonl' for cond in ['joint',mode]]
                if not all((p.parent/'evaluation-complete.json').exists() for p in paths):continue
                refs=[{r['id']:r for r in map(json.loads,p.read_text().splitlines())} for p in paths]
                for rid,a in refs[0].items():
                    b=refs[1][rid];key=(model,mode,len(a['chain']));c=grouped[key];c['n']+=1
                    av,bv=a['grade']['complete'],b['grade']['complete']
                    c['joint_success']+=av;c['specialist_success']+=bv
                    label='gain' if bv and not av else 'loss' if av and not bv else 'both_correct' if av else 'both_wrong'
                    c[label]+=1
                    if mode=='order_oracle':
                        for name,r in [('joint',a),('specialist',b)]:
                            if not r['grade']['complete']:
                                s=signature(r);c[name+':first_error:'+s['kind']]+=1
                                if 'position' in s:c[name+':first_error_position:'+str(s['position'])]+=1
                    if label in ['gain','loss']:
                        pool[key+(label,)].append(dict(seed=seed,id=rid,x=a['x'],chain=[NAMES[t] for t in a['chain']],joint_source=str(paths[0].relative_to(R)),specialist_source=str(paths[1].relative_to(R)),joint_signature=signature(a),specialist_signature=signature(b),joint_stop=a['stop'],specialist_stop=b['stop']))
    rng=random.Random(20260925)
    out=dict(cells=[dict(model=k[0],mode=k[1],length=k[2],counts=dict(v)) for k,v in grouped.items()],examples=[dict(group=k,total=len(v),samples=rng.sample(v,min(3,len(v)))) for k,v in sorted(pool.items())],training=training,note='First incorrect body is a descriptive signature, not a proven cause. All examples sampled after counting every paired trajectory. Loss is teacher-forced training loss, not generalization accuracy.')
    (R/'analysis/mechanism-diagnostics.json').write_text(json.dumps(out,indent=2));print('Mechanism signatures:',len(grouped),'paired cells')
if __name__=='__main__':main()
