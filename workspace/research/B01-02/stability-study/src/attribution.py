"""Paired first-divergence and oracle-to-real history comparisons, all cases retained."""
import collections,json,random
from common import *

def first_difference(a,b):
    for i,(x,y) in enumerate(zip(a['events'],b['events'])):
        if x['token_ids']!=y['token_ids']:
            return dict(event=i,phase=x['phase'],other_phase=y['phase'],same_prefix=x['prefix_sha256']==y['prefix_sha256'],left_text=x['text'],right_text=y['text'])
    return None

def main():
    d=json.loads((R/'analysis/results.json').read_text());jobs={j['id']:j for j in json.loads((R/'analysis/jobs.json').read_text())};lookup={}
    for e in d['sources']:
        if e['split']!='independent' or e['step'] not in [256,512]:continue
        j=jobs[e['job']];label=(j.get('condition'),e['mode']) if j['kind']=='curve' else ('compose',e['mode'])
        lookup[j['model'],j['seed'],e['step'],*label]={r['id']:r for r in map(json.loads,Path(e['source']).read_text().splitlines())}
    groups=collections.defaultdict(collections.Counter);pools=collections.defaultdict(list);exceptions=[]
    for model in ['qwen3b','qwen32b']:
        for seed in [11,22,33]:
            for step in [256,512]:
                base=lookup.get((model,seed,step,'joint','joint'));order=lookup.get((model,seed,step,'operation_oracle','operation_oracle'))
                if base is None:continue
                for mode in ['SE','SJ','JE']:
                    current=lookup.get((model,seed,step,'compose',mode))
                    if current is None:continue
                    for rid,r in current.items():
                        ref=base[rid];c=groups[model,step,mode,len(r['chain'])];c['n']+=1;diff=first_difference(ref,r)
                        change='gain' if r['grade']['complete'] and not ref['grade']['complete'] else 'loss' if ref['grade']['complete'] and not r['grade']['complete'] else 'same_correctness'
                        c[change]+=1
                        if diff:
                            expected=diff['same_prefix'] and diff['phase']==diff['other_phase'] and (mode=='SE' or diff['phase']==('header' if mode=='SJ' else 'body'))
                            c['first_difference_expected_role' if expected else 'first_difference_other_role']+=1
                            if not expected:exceptions.append(dict(model=model,seed=seed,step=step,mode=mode,id=rid,difference=diff))
                        else:c['identical_shared_events']+=1
                        if change!='same_correctness':pools[model,step,mode,change].append(dict(seed=seed,id=rid,length=len(r['chain']),first_difference=diff,base_stop=ref['stop'],composition_stop=r['stop']))
                        if mode=='SE' and order is not None:
                            os=order[rid]['grade']['sequence_correct'];rs=r['grade']['sequence_correct']
                            c['sequence_oracle_correct']+=os;c['sequence_real_correct']+=rs
                            if os and not rs:
                                c['sequence_correct_with_oracle_but_wrong_in_real']+=1
                                firstwrong=next((i for i,x in enumerate(r['calls']) if i>=len(r['chain']) or x['tool']!=r['chain'][i]),len(r['calls']))
                                prior=r['calls'][:firstwrong];bad=any(not x.get('body',{}).get('correct',False) for x in prior)
                                c['lost_sequence_with_prior_body_error' if bad else 'lost_sequence_without_prior_body_error']+=1
    rng=random.Random(20260925)
    write(R/'analysis/attribution.json',dict(cells=[dict(model=k[0],step=k[1],mode=k[2],length=k[3],counts=dict(v)) for k,v in groups.items()],examples=[dict(group=k,total=len(v),samples=rng.sample(v,min(3,len(v)))) for k,v in sorted(pools.items())],exceptions=exceptions,note='Prior body error is observational association, not proof of causal error propagation. First-token differences outside changed role may reflect numerical batching effects and are explicitly retained.'))
    print('Attribution cells',len(groups),'pre-intervention exceptions',len(exceptions))
if __name__=='__main__':main()
