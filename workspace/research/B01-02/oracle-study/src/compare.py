"""Paired per-seed and program-cluster descriptive contrasts."""
import collections,json
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1]
def main():
 rows={}
 for run in (R/'runs').iterdir():
  if not (run/'evaluation-complete.json').exists():continue
  c=json.loads((run/'config.json').read_text())['args']
  for p in run.glob('evaluation-*.jsonl'):
   for line in p.read_text().splitlines():
    r=json.loads(line);rows[c['model'],c['condition'],c['seed'],r['mode'],r['split'],r['id']]=r
 rng=np.random.default_rng(20260925);results=[]
 for model in ['qwen1.5b','qwen3b','qwen7b','qwen32b']:
  for mode in ['order_oracle','operation_oracle']:
   splits=sorted({key[4] for key in rows if key[0]==model})
   for split in splits:
    for L in sorted({len(r['chain']) for key,r in rows.items() if key[0]==model and key[4]==split}):
     paired=[];seeds=[]
     for seed in [11,22,33]:
      pairs=[]
      for key,r in rows.items():
       if key[:5]!=(model,mode,seed,mode,split) or len(r['chain'])!=L:continue
       ref=rows.get((model,'joint',seed,mode,split,key[5]))
       if ref is None:continue
       assert (r['chain'],r['x'])==(ref['chain'],ref['x'])
       delta=int(r['grade']['complete'])-int(ref['grade']['complete']);pairs.append(delta);paired.append((tuple(r['chain']),delta))
      if pairs:seeds.append(dict(seed=seed,n=len(pairs),delta=float(np.mean(pairs))))
     if len(seeds)!=3:continue
     groups=collections.defaultdict(list)
     for chain,v in paired:groups[chain].append(v)
     sums=np.array([sum(v) for v in groups.values()]);ns=np.array([len(v) for v in groups.values()]);ix=rng.integers(len(ns),size=(2000,len(ns)));boot=sums[ix].sum(axis=1)/ns[ix].sum(axis=1)
     results.append(dict(model=model,mode=mode,split=split,length=L,seeds=seeds,paired_n=len(paired),programs=len(ns),specialist_minus_joint_same_oracle=float(sums.sum()/ns.sum()),program_bootstrap95=np.quantile(boot,[.025,.975]).tolist()))
 (R/'analysis/paired-comparisons.json').write_text(json.dumps(dict(results=results,note='Difference: specialist training minus joint training in the SAME oracle environment. Program bootstrap conditional on three observed seeds; seed-specific differences reported. Non-significance is not equivalence.'),indent=2));print('Paired contrasts:',len(results))
if __name__=='__main__':main()
