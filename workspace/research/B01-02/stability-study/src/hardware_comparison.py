"""Quantify old 5090 versus current 3B outputs without substituting old baselines."""
import hashlib,json
from common import R,O,write,Path


def main():
    hashes=json.loads((R/'analysis/adapter-hashes.json').read_text())['files'];weights=[];results=[]
    for condition in ['joint','order_oracle','operation_oracle']:
        for seed in [11,22,33]:
            oldroot=O/'runs'/f'qwen3b-{condition}-s{seed}'
            cp=oldroot/'checkpoints/step0512/adapter/adapter_model.safetensors'
            final=oldroot/'adapter/adapter_model.safetensors'
            h=hashlib.sha256(final.read_bytes()).hexdigest();assert h==hashes[str(cp)]['sha256']
            assert json.loads((cp.parent/'adapter_config.json').read_text())==json.loads((final.parent/'adapter_config.json').read_text())
            weights.append(dict(condition=condition,seed=seed,final_equals_checkpoint512=True,sha256=h))
            newroot=R/'runs'/f'curve-qwen3b-{condition}-s{seed}'
            assert (newroot/'complete.json').exists(),newroot
            for mode in (['joint','order_oracle','operation_oracle'] if condition=='joint' else [condition]):
                old=oldroot/f'evaluation-{mode}-independent.jsonl';new=newroot/f'step512-{mode}-independent.jsonl'
                a=list(map(json.loads,old.read_text().splitlines()));b=list(map(json.loads,new.read_text().splitlines()))
                assert len(a)==len(b)==480 and [r['id'] for r in a]==[r['id'] for r in b]
                results.append(dict(condition=condition,seed=seed,mode=mode,n=480,
                                    exact_records=sum(x==y for x,y in zip(a,b)),
                                    same_grades=sum(x['grade']==y['grade'] for x,y in zip(a,b)),
                                    old_complete=sum(x['grade']['complete'] for x in a),
                                    new_complete=sum(x['grade']['complete'] for x in b),
                                    old_wrong_new_correct=sum(y['grade']['complete'] and not x['grade']['complete'] for x,y in zip(a,b)),
                                    old_correct_new_wrong=sum(x['grade']['complete'] and not y['grade']['complete'] for x,y in zip(a,b)),
                                    sources={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [old,new]}))
    assert len(results)==15
    write(R/'analysis/hardware-comparison.json',dict(weights=weights,results=results,
          note='Weights and adapter configurations equal. Old 5090 and current PRO6000 executions can differ numerically; this comparison does not isolate the exact kernel or driver cause. All main 3B contrasts use current same-hardware outputs.'))
    print('3B old/current comparison:',sum(r['exact_records'] for r in results),'exact of',sum(r['n'] for r in results))


if __name__=='__main__':main()
