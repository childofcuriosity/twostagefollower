"""Program-cluster uncertainty for the observed oracle-task co-success minus product."""
import collections,json
import numpy as np
from protocol import R

def main():
    rng=np.random.default_rng(20260925);results=[]
    for model in ['qwen1.5b','qwen3b','qwen7b','qwen32b']:
        paired={}
        for seed in [11,22,33]:
            runs=[R/'runs'/f'{model}-{m}-s{seed}' for m in ['operation_oracle','order_oracle']]
            if not all((r/'evaluation-complete.json').exists() for r in runs):continue
            maps=[{r['id']:r for r in map(json.loads,(p/f'evaluation-{m}-independent.jsonl').read_text().splitlines())} for p,m in zip(runs,['operation_oracle','order_oracle'])]
            for rid,a in maps[0].items():
                b=maps[1][rid];paired[seed,rid]=(tuple(a['chain']),int(a['grade']['complete']),int(b['grade']['complete']))
        for L in [3,4,5,6,8]:
            programs=sorted({v[0] for v in paired.values() if len(v[0])==L})
            if len(programs)!=24 or len([v for v in paired.values() if len(v[0])==L])!=288:continue
            counts=np.zeros((3,24,3))
            for si,seed in enumerate([11,22,33]):
                for pi,program in enumerate(programs):
                    rows=[v for (s,i),v in paired.items() if s==seed and v[0]==program];assert len(rows)==4
                    counts[si,pi]=[sum(v[1] for v in rows)/4,sum(v[2] for v in rows)/4,sum(v[1]*v[2] for v in rows)/4]
            avg=counts.mean(axis=1);delta=avg[:,2]-avg[:,0]*avg[:,1]
            samples=rng.integers(24,size=(2000,24));boot=counts[:,samples,:].mean(axis=2)
            bd=(boot[:,:,2]-boot[:,:,0]*boot[:,:,1]).mean(axis=0)
            results.append(dict(model=model,length=L,programs=24,records=288,co_success_minus_product=float(delta.mean()),per_seed_delta=delta.tolist(),program_bootstrap95=np.quantile(bd,[.025,.975]).tolist()))
    (R/'analysis/product-uncertainty.json').write_text(json.dumps(dict(results=results,note='Shared program resampling across all three seeds, conditional on these trained checkpoints. CI crossing zero is not evidence of equivalence or internal independence. No multiplicity correction; descriptive only.'),indent=2))
    lines=['# Checking oracle subtask products','Each length has 24 programs x 4 inputs x 3 training seeds. Compute A x B within each seed, then average. Both-correct on the same example is measured from two oracle evaluations, not an executed composed model. The table reports both-correct minus A x B, in percentage points. Intervals use 2000 program-cluster bootstrap resamples, conditional on the three observed seeds; they exclude population uncertainty over training seeds. An interval containing 0 does not establish independence or equivalence.','|Model|Calls|Difference|Program bootstrap 95% interval|Seed11 / 22 / 33 differences|','|---|---:|---:|---|---|']
    for r in results:
        lo,hi=r['program_bootstrap95'];seeds=' / '.join(f'{100*v:+.2f}' for v in r['per_seed_delta'])
        lines.append(f'|{r["model"]}|{r["length"]}|{100*r["co_success_minus_product"]:+.2f}|[{100*lo:+.2f}, {100*hi:+.2f}]|{seeds}|')
    lines+=['','See ORACLE_PRODUCTS.md for A, B, and joint free-execution accuracy. Distinguish two differences: both-correct versus the product measures statistical association between oracle subtask outputs; the product versus joint free execution additionally changes training and inference environments and cannot be attributed only to correlation.']
    (R/'FACTORIZATION.md').write_text('\n'.join(lines));print('Factorization uncertainty cells:',len(results))
if __name__=='__main__':main()
