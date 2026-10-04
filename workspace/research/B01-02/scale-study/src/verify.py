from pathlib import Path
import hashlib,json,time,math
R=Path(__file__).resolve().parents[1];P=R.parent
reg=json.loads((R/'analysis/registration.json').read_text())
for name,h in reg['hashes'].items():
 p=Path(name)
 if '/data/' in name:assert hashlib.sha256(p.read_bytes()).hexdigest()==h,name
assert hashlib.sha256((R/'src/train.py').read_bytes()).hexdigest()==json.loads((R/'analysis/registration-v2.json').read_text())['train_sha256']
assert hashlib.sha256((R/'src/launch.py').read_bytes()).hexdigest()==json.loads((R/'analysis/registration-v4.json').read_text())['launch_sha256']
checkpoints={};counts=[]
for model in ['qwen7b','qwen32b']:
 for seed in [11,22,33]:
  pair=[]
  for c in ['flat','macro']:
   run=R/f'{model}/runs/{c}-original-s{seed}';meta=json.loads((run/'summary.json').read_text());train=[json.loads(l) for l in (run/'train.jsonl').read_text().splitlines()];assert len(train)==512 and train[-1]['examples']==16384;assert train[-1]['input_tokens']==meta['training']['counts']['input_tokens'];assert train[-1]['target_tokens']==meta['training']['counts']['target_tokens'];pair.append(meta['training']['counts'])
   assert [row['step'] for row in train]==list(range(1,513)),(model,seed,c,'missing or repeated training steps')
   for row in train:
    for key in ['loss','lr','grad_norm','elapsed']:
     assert math.isfinite(row[key]),(model,seed,c,row['step'],key,'nonfinite training value')
   assert all(row['examples']==32*row['step'] for row in train),(model,seed,c,'inconsistent effective batch')
   files=[run/'adapter/adapter_model.safetensors']+[run/f'checkpoints/step{step:04d}/adapter/adapter_model.safetensors' for step in [0,16,64,128,256,512]]
   for p in files:
    h=hashlib.sha256()
    with p.open('rb') as f:
     for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    checkpoints[str(p.relative_to(R))]=h.hexdigest()
   assert checkpoints[str(files[0].relative_to(R))]==checkpoints[str(files[-1].relative_to(R))]
  assert pair[0]==pair[1],(model,seed,'flat/macro token budgets differ');counts.append(dict(model=model,seed=seed,counts=pair[0]))
assert len(checkpoints)==84
res=json.loads((R/'analysis/results.json').read_text());ext=json.loads((R/'analysis/extended-results.json').read_text());assert not res['missing'];assert res['final_execution_records']==13440 and ext['records_checked']==13440
# Verify every expected file against the complete registered question set, not just row counts.
from audit import check
original={x['id']:x for x in map(json.loads,(P/'data/test.jsonl').read_text().splitlines())}
extended={x['id']:x for x in map(json.loads,(R/'data/extended-test.jsonl').read_text().splitlines())}
assert len(original)==560 and len(extended)==480
assert hashlib.sha256((R/'data/extended-test.jsonl').read_bytes()).hexdigest()==json.loads((R/'analysis/extended-data-registration.json').read_text())['sha256']
raw_hashes={}; coverage=[]
def validate_raw(path,questions):
 rows=[json.loads(line) for line in path.read_text().splitlines()]
 assert len(rows)==len(questions) and {x['id'] for x in rows}==set(questions),str(path)
 for row in rows:
  expected=questions[row['id']]
  assert all(row[k]==expected[k] for k in ['chain','x','split']),str(path)
  check(row)
 raw_hashes[str(path.resolve())]=hashlib.sha256(path.read_bytes()).hexdigest()
 return len(rows)
for path in res['source_sha256']:validate_raw(Path(path),original)
additional=0
for model in ['qwen7b','qwen32b']:
 for seed in [11,22,33]:
  for c in ['flat','macro']:
   run=R/f'{model}/runs/{c}-original-s{seed}'
   paths=[run/f'checkpoint-tests/step{step:04d}-predictions.jsonl' for step in [0,16,64,128,256]]
   paths += [run/'checkpoint-tests/step0000-with-library.jsonl',run/'predictions-with-library.jsonl']
   for path in paths:additional+=validate_raw(path,original)
   coverage.append(dict(model=model,seed=seed,condition=c,files=len(paths),rows=3920))
assert additional==47040==res['additional_execution_records_checked']
for model in ['qwen1.5b','qwen3b','qwen7b','qwen32b']:
 paths=[R/f'extended/{model}/{c}-s{seed}.jsonl' for c in ['flat','macro'] for seed in [11,22,33]]
 frozen=list((R/f'extended/{model}').glob('frozen*.jsonl'));assert len(frozen)==1
 for path in paths+frozen:validate_raw(path,extended)
supp=json.loads((R/'analysis/supplement-results.json').read_text());assert supp['raw_records']==21280
for path,sha in supp['source_sha256'].items():
 validate_raw(R/path,original);assert raw_hashes[str((R/path).resolve())]==sha
assert len(raw_hashes)==174 and sum([13440,additional,13440,21280])==95200
# The numeric, parsing and per-step audits are performed by analyze/inference on raw source records; this verifies file provenance and full-run coverage.
for file,h in res['source_sha256'].items():assert hashlib.sha256(Path(file).read_bytes()).hexdigest()==h
for file,h in ext['manifest'].items():assert hashlib.sha256((R/file).read_bytes()).hexdigest()==h
report=dict(raw_output_sha256=raw_hashes,complete_fixed_checkpoint_coverage=coverage,total_unique_raw_output_records=95200,utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),registered_training_data_unchanged=True,registered_train_source_unchanged_since_v2=True,registered_launcher_unchanged_since_v4=True,flat_macro_token_budgets=counts,checkpoint_sha256=checkpoints,final_records=res['final_execution_records'],additional_fixed_checkpoint_and_library_records=res['additional_execution_records_checked'],independent_confirmation_records=ext['records_checked'])
from matched_context import main as verify_matched_context
verify_matched_context()
(R/'analysis/verification.json').write_text(json.dumps(report,indent=2));print('Verified 12 formal trainings, 84 checkpoints and all analysis provenance',flush=True)
