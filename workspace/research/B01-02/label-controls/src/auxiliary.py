"""Audit already generated legacy auxiliary evaluations; never launch new inference."""
from common import *
from grading import grade
import collections
records=[];hashes={}
for model in ['qwen7b','qwen32b']:
 for condition in ['flat','macro','position','alias']:
  for seed in [11,22,33]:
   if condition in ['flat','macro']:base=ROOTS[model]/f'runs/{condition}-original-s{seed}'
   else:base=R/f'runs/{model}-{condition}-s{seed}/runs/{condition}-original-s{seed}'
   files=[base/'predictions-with-library.jsonl']
   if condition in ['position','alias']:files+=sorted(base.glob('step*-dev*.jsonl'))
   for p in files:
    assert p.exists(),p;rs=[json.loads(l) for l in p.read_text().splitlines()];counts=collections.defaultdict(collections.Counter)
    for row in rs:
     g=grade(row,condition);c=counts[row['split']];c['n']+=1;c['strict_trace']+=g['strict_trace'];c['label_sequence_correct']+=g['label_sequence_correct'];c['accuracy']+=g['accuracy']
    hashes[str(p.relative_to(B))]=sha(p)
    records.append(dict(model=model,condition=condition,seed=seed,source=str(p.relative_to(B)),file=p.name,n=len(rs),groups=dict(counts)))
write(R/'analysis/auxiliary-audit.json',dict(records=records,total_rows=sum(x['n'] for x in records),source_sha256=hashes,note='Already produced auxiliary evaluations retained from original trainer: with-library main test and new large-model checkpoint dev. Separate from 49920 primary comparison records; no test-driven checkpoint selection.'))
lines=['# 沿旧训练器保留的补充评测','以下均由旧训练器原有流程产生；未额外运行新模型条件。主结论仍使用无工具定义的原测试和固定512步独立集。本表不选择较好条件替代主结果。','', '## 给出工具定义的原测试（最终512步）','', '|模型|子集|原STEP|原名称|位置编号|固定改名|','|---|---|---:|---:|---:|---:|']
for model in ['qwen7b','qwen32b']:
 groups=sorted({g for x in records if x['model']==model and x['file']=='predictions-with-library.jsonl' for g in x['groups']})
 for group in groups:
  vals=[]
  for condition in ['flat','macro','position','alias']:
   cells=[x['groups'][group] for x in records if (x['model'],x['condition'],x['file'])==(model,condition,'predictions-with-library.jsonl')];assert len(cells)==3
   vals.append(sum(c['strict_trace']/c['n'] for c in cells)/3)
  lines.append('|'+model+'|'+group+'|'+'|'.join(f'{100*v:.2f}%' for v in vals)+'|')
lines+=['','开发集各检查点逐seed和数据子集的成绩保存在analysis/auxiliary-audit.json，不与正式测试混成额外独立样本。']
(R/'AUXILIARY_EVALUATIONS.md').write_text('\n'.join(lines)+'\n')
print('Auxiliary existing outputs audited:',sum(x['n'] for x in records),flush=True)
