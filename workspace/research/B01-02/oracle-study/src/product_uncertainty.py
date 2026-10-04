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
    lines=['# Oracle子任务乘积校验','每长度24个程序×4输入×3训练seed。先在每seed求A×B，再平均；同题均对来自两次oracle测试，未实际运行组合模型。下表是“同题均对−A×B”，百分数单位为百分点。区间按程序成簇重采样2000次，条件于已有三个seed；不包含训练seed总体的不确定性。区间包含0不能证明独立或等价。','|模型|调用数|差值|程序bootstrap 95%区间|seed11 / 22 / 33差值|','|---|---:|---:|---|---|']
    for r in results:
        lo,hi=r['program_bootstrap95'];seeds=' / '.join(f'{100*v:+.2f}' for v in r['per_seed_delta'])
        lines.append(f'|{r["model"]}|{r["length"]}|{100*r["co_success_minus_product"]:+.2f}|[{100*lo:+.2f}, {100*hi:+.2f}]|{seeds}|')
    lines+=['','A、B和联合自由执行的准确率见ORACLE_PRODUCTS.md。两类差异必须区分：同题均对与乘积的差，是oracle子任务输出的统计关联；乘积与联合自由执行的差，还包含训练方式和推理环境改变，不能只归为相关性。']
    (R/'FACTORIZATION.md').write_text('\n'.join(lines));print('Factorization uncertainty cells:',len(results))
if __name__=='__main__':main()
