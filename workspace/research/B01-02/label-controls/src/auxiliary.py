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
lines=['# Supplementary evaluations retained from the original trainer','These outputs all come from the existing workflow of the original trainer; no extra model conditions were run. Primary conclusions still use the original tests without tool definitions and the fixed-512-step independent set. This table does not substitute better-performing conditions for the primary results.','', '## Original tests with tool definitions (final step512)','', '|Model|Subset|Original STEP|Original NAME|Position numbering|Fixed aliases|','|---|---|---:|---:|---:|---:|']
for model in ['qwen7b','qwen32b']:
 groups=sorted({g for x in records if x['model']==model and x['file']=='predictions-with-library.jsonl' for g in x['groups']})
 for group in groups:
  vals=[]
  for condition in ['flat','macro','position','alias']:
   cells=[x['groups'][group] for x in records if (x['model'],x['condition'],x['file'])==(model,condition,'predictions-with-library.jsonl')];assert len(cells)==3
   vals.append(sum(c['strict_trace']/c['n'] for c in cells)/3)
  lines.append('|'+model+'|'+group+'|'+'|'.join(f'{100*v:.2f}%' for v in vals)+'|')
lines+=['','Per-seed and per-subset development scores at every checkpoint are saved in analysis/auxiliary-audit.json and are not pooled with formal tests as additional independent samples.']
(R/'AUXILIARY_EVALUATIONS.md').write_text('\n'.join(lines)+'\n')
print('Auxiliary existing outputs audited:',sum(x['n'] for x in records),flush=True)
