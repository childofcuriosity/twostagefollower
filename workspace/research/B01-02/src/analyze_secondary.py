import json,statistics,math,hashlib,collections
from pathlib import Path
import numpy as np
from scipy.stats import t
from secondary import signature,expand,execute,answer
ROOT=Path(__file__).resolve().parents[1]/'secondary'
lib=json.loads((ROOT/'data/worlds.json').read_text())['original']['library']
train=[json.loads(s) for s in (ROOT/'data/train.jsonl').read_text().splitlines()];test=[json.loads(s) for s in (ROOT/'data/test.jsonl').read_text().splitlines()]
keys={signature(expand(r['chain'],lib)) for r in train}
assert not keys.intersection(signature(expand(r['chain'],lib)) for r in test if r['split']!='iid')
raw={};summ={};diff=[]
for seed in [11,22,33]:
 for c in ['flat','macro']:
  name=f'{c}-original-s{seed}';p=ROOT/'runs'/name
  summ[name]=json.loads((p/'summary.json').read_text());rs=[json.loads(s) for s in (p/'predictions.jsonl').read_text().splitlines()]
  assert len(rs)==len(test) and len({r['id'] for r in rs})==len(test)
  for r in rs:
   assert execute(r['x'],expand(r['chain'],lib))==r['expected']
   assert answer(r['raw'])==r['prediction']
   assert r['correct']==(r['prediction']==r['expected'])
  raw[name]=rs
 a=summ[f'macro-original-s{seed}'];b=summ[f'flat-original-s{seed}'];assert a['training']['counts']==b['training']['counts']
 diff.append(a['evaluation']['groups']['ood']['accuracy']-b['evaluation']['groups']['ood']['accuracy'])
mean=statistics.mean(diff);se=statistics.stdev(diff)/math.sqrt(3)
program_diagnostics={}
for name,rs in raw.items():
 groups=collections.defaultdict(list)
 for r in rs:
  if r['split']=='ood':groups[tuple(r['chain'])].append(r)
 program_diagnostics[name]={'all_four_inputs_correct_fraction':sum(all(r['correct'] for r in group) for group in groups.values())/len(groups),'exact_primitive_sequence_accuracy':summ[name]['evaluation']['groups']['ood']['program_accuracy']}
report={'seed_differences':diff,'mean_difference':mean,'seed_t_interval_95':[mean-t.ppf(.975,2)*se,mean+t.ppf(.975,2)*se] if se else None,'verification':'recomputed every answer, exact semantic split, actual target/input tokens matched','conditions':{c:{split:[summ[f'{c}-original-s{s}']['evaluation']['groups'][split]['accuracy'] for s in [11,22,33]] for split in ['iid','ood','pressure']} for c in ['flat','macro']},'program_diagnostics':program_diagnostics,'interpretation':'Post-hoc second generator with separately trained adapters; same proposed macro structures, different primitive semantics and input lengths. Not zero-shot transfer. Short binary strings have substantial accidental answer matches; report exact trace and all-four-input program metrics alongside accuracy.'}
(ROOT/'analysis/results.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
manifest={}
for p in ROOT.rglob('*'):
 if p.is_file() and p.suffix in ['.py','.json','.jsonl','.safetensors'] and 'model' not in p.parts and p.name!='verification.json':
  h=hashlib.sha256()
  with p.open('rb') as f:
   for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
  manifest[str(p.relative_to(ROOT))]=h.hexdigest()
(ROOT/'analysis/verification.json').write_text(json.dumps(manifest,indent=2))
