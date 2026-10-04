"""Post-run integrity checks, independent of model correctness."""
from pathlib import Path
import json,hashlib
from dsl import execute,expand,signature
ROOT=Path(__file__).resolve().parents[1]
worlds=json.loads((ROOT/'data/worlds.json').read_text())
train=[json.loads(s) for s in (ROOT/'data/train.jsonl').read_text().splitlines()]
test=[json.loads(s) for s in (ROOT/'data/test.jsonl').read_text().splitlines()]
assert not ({(tuple(r['chain']),tuple(r['x'])) for r in train}&{(tuple(r['chain']),tuple(r['x'])) for r in test})
for world in worlds.values():
 trainkeys={signature(expand(r['chain'],world['library'])) for r in train}
 assert not (trainkeys & {signature(expand(r['chain'],world['library'])) for r in test if r['split']!='iid'})
checked=[]
for p in (ROOT/'runs').glob('*/summary.json'):
 meta=json.loads(p.read_text());world=worlds[meta['args']['world']];rows=[json.loads(s) for s in (p.parent/'predictions.jsonl').read_text().splitlines()]
 assert len({r['id'] for r in rows})==len(rows)
 for r in rows:
  y=execute(r['x'],expand(r['chain'],world['library']));assert list(y)==r['expected']
  assert r['correct']==(r['prediction']==r['expected'])
 if not meta['args']['calibrate']:assert len(rows)==len(test)
 checked.append(p.parent.name)
token_checks={}
for seed in [11,22,33]:
 paths=[ROOT/f'runs/{c}-original-s{seed}/summary.json' for c in ['flat','macro','shuffled']]
 if all(p.exists() for p in paths):
  counts=[json.loads(p.read_text())['training']['counts'] for p in paths]
  assert counts[0]==counts[1]==counts[2],('token mismatch',seed,counts)
  token_checks[str(seed)]=counts[0]
checkpoints={}
for p in (ROOT/'runs').glob('*/adapter/adapter_model.safetensors'):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 checkpoints[str(p.relative_to(ROOT))]=h.hexdigest()
result={'checked_runs':checked,'exact_answer_recomputation':'pass','data_isolation':'pass','actual_primary_training_token_match':token_checks,'checkpoint_sha256':checkpoints,'base_model_manifest':json.loads((ROOT/'model/download-manifest.json').read_text()),'manifest':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.rglob('*') if p.is_file() and p.suffix in ['.py','.json','.jsonl','.md','.csv'] and p.name!='artifact-verification.json' and 'model' not in p.parts and '__pycache__' not in p.parts}}
(ROOT/'analysis/artifact-verification.json').write_text(json.dumps(result,indent=2));print('VERIFIED',len(checked),'runs')
