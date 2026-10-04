"""Post-hoc descriptive classification; never selects checkpoints or changes outcomes."""
import collections, functools, hashlib, json, re
from pathlib import Path
from audit import check, dsl, lib
R=Path(__file__).resolve().parents[1]
@functools.lru_cache(None)
def signature(ops): return dsl.signature(ops)
summary=[]; hashes={}; n=0
with (R/'analysis/outcome-diagnostics.jsonl').open('w') as out:
 for family, manifest, relative in [
  ('main',json.loads((R/'analysis/results.json').read_text())['source_sha256'],False),
  ('independent',json.loads((R/'analysis/extended-results.json').read_text())['manifest'],True),
  ('supplement',json.loads((R/'analysis/supplement-results.json').read_text())['source_sha256'],True)]:
  for filename, expected_hash in manifest.items():
   p=R/filename if relative else Path(filename)
   h=hashlib.sha256(p.read_bytes()).hexdigest();assert h==expected_hash
   hashes[str(p.relative_to(R.parent))]=h; groups=collections.defaultdict(collections.Counter)
   for line in p.read_text().splitlines():
    row=json.loads(line);a=check(row);n+=1
    emitted=tuple(re.findall(r'^(rev|rot|inc|neg|swap|ends) [0-9] [0-9] [0-9] [0-9]$',row['raw'],re.M))
    wanted=tuple(dsl.expand(row['chain'],lib));pred=dsl.answer(row['raw'])
    if not a['accuracy']:category='answer_incorrect_or_invalid'
    elif a['strict_trace']:category='exact_trace'
    elif emitted and not a['numeric_step_error'] and not a['format_extra_lines'] and tuple(pred)==dsl.execute(row['x'],emitted):
     category='different_trace_globally_equivalent' if signature(emitted)==signature(wanted) else 'different_trace_correct_only_on_this_input'
    else:category='correct_answer_without_valid_supporting_trace'
    # Broad observable truncation includes erroneous prefixes; not proof of why stopping occurred.
    trunc=int(a['answer_present'] and a['emitted_ops']<a['required_ops'])
    item=dict(family=family,source=str(p.relative_to(R.parent)),id=row['id'],split=row['split'],category=category,answer_with_fewer_primitive_steps=trunc,correct_prefix_early_answer=a['correct_prefix_early_answer'])
    out.write(json.dumps(item)+'\n');g=groups[row['split']];g['n']+=1;g[category]+=1;g['answer_with_fewer_primitive_steps']+=trunc;g['correct_prefix_early_answer']+=a['correct_prefix_early_answer']
   summary.extend(dict(family=family,source=str(p.relative_to(R.parent)),split=s,counts=dict(c)) for s,c in groups.items())
assert n==48160,n
params=[]
for model,root in [('qwen1.5b',R.parent),('qwen3b',R.parent/'rsi-study/replications/qwen3b'),('qwen7b',R/'qwen7b'),('qwen32b',R/'qwen32b')]:
 values=[]
 for seed in [11,22,33]:
  for c in ['flat','macro']:
   m=json.loads((root/f'runs/{c}-original-s{seed}/summary.json').read_text());values.append((m['trainable_parameters'],m['total_parameters']))
 assert len(set(values))==1
 trainable,total=values[0];params.append(dict(model=model,trainable=trainable,total_including_adapters=total,frozen_base=total-trainable,trainable_fraction=trainable/total))
(R/'analysis/outcome-diagnostics.json').write_text(json.dumps(dict(records=n,summary=summary,source_sha256=hashes,parameter_counts=params,notes='Post-hoc descriptive audit. Categories partition all rows. Affine signatures prove equivalence on all 10^4 inputs. Fewer primitive steps plus an Answer is broader than the conservative correct-prefix early-answer subset and can include parsing/format failures; neither alone identifies causal mechanism.'),indent=2))
print('Classified',n,'raw outcomes and verified LoRA parameter counts across 24 main runs')
