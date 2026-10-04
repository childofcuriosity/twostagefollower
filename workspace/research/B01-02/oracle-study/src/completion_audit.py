"""Fail closed: verify full registered matrix and explicit evidence for completion."""
import hashlib,json,math
from protocol import R,MODES,MODELS,read

def main():
 missing=[];records=0;runs=[]
 for model in MODELS:
  for condition in MODES:
   for seed in [11,22,33]:
    run=R/'runs'/f'{model}-{condition}-s{seed}';needed=['training-complete.json','evaluation-complete.json']
    if any(not (run/x).exists() for x in needed):missing.append(str(run));continue
    tr=json.loads((run/'training-complete.json').read_text());assert tr['steps']==512 and tr['counts']['examples']==512*32
    args=tr['config']['args'];assert (args['model'],args['condition'],args['seed'])==(model,condition,seed)
    expected_tokens=json.loads((R/'analysis/preflight.json').read_text())[model]['supervised_tokens'][condition]*4
    assert tr['counts']['supervised_tokens']==expected_tokens
    log=[json.loads(l) for l in (run/'train.jsonl').read_text().splitlines()]
    assert [r['step'] for r in log]==list(range(1,513)) and all(math.isfinite(r['loss']) and math.isfinite(r['grad_norm']) for r in log)
    assert (run/'adapter/adapter_model.safetensors').exists()
    for src in ['protocol.py','evaluate.py']:
     assert hashlib.sha256((R/'src'/src).read_bytes()).hexdigest()==tr['config']['source_sha256'][src]
    for ck in [64,128,256,512]:assert (run/f'checkpoints/step{ck:04d}/adapter/adapter_model.safetensors').exists()
    summary=json.loads((run/'evaluation-complete.json').read_text())
    for mode in MODES if condition=='joint' else [condition]:
     for split in ['test','independent']:
      p=run/f'evaluation-{mode}-{split}.jsonl';assert p.exists();rows=[json.loads(l) for l in p.read_text().splitlines()];ref=read(split)
      assert len(rows)==len(ref)==summary[p.name]['n'];assert {r['id'] for r in rows}=={r['id'] for r in ref}
      refs={r['id']:r for r in ref}
      assert all((r['x'],r['chain'])==(refs[r['id']]['x'],refs[r['id']]['chain']) for r in rows)
      records+=len(rows)
    runs.append(run.name)
 status={'registered_runs':36,'completed_runs':len(runs),'expected_trajectories':62400,'observed_trajectories':records,'missing':missing,'complete':False}
 if not missing:
  assert records==62400
  replay=json.loads((R/'analysis/token-replay.json').read_text());assert sum(v['trajectories'] for v in replay['counts'].values())==62400
  audit=json.loads((R/'analysis/results-audit.json').read_text());assert audit['records']==62400
  for rel,h in audit['source_hashes'].items():assert hashlib.sha256((R/rel).read_bytes()).hexdigest()==h
  assert replay['files']==audit['source_hashes']
  input_manifest=json.loads((R/'analysis/reproducibility-inputs.json').read_text())
  for rel,h in input_manifest['datasets'].items():assert hashlib.sha256((R.parents[3]/rel).read_bytes()).hexdigest()==h
  for model in MODELS:
   m=input_manifest['models'][model]
   for name,h in m['json_hashes'].items():assert hashlib.sha256((MODELS[model]/name).read_bytes()).hexdigest()==h
   for w in m['weight_files']:assert (MODELS[model]/w['name']).stat().st_size==w['bytes']
   re=json.loads((R/'analysis/reproduction'/model/'summary.json').read_text());assert re['records']==re['exact']==re['grades']==120
  assert len(json.loads((R/'analysis/controller-preflight.json').read_text())['checks'])==10
  budgets=json.loads((R/'analysis/reference-budget-audit.json').read_text())
  assert set(budgets)==set(MODELS) and all(v['reference_trajectories']==5136 for v in budgets.values())
  status['new_process_exact_replays']=480
  status['fixed_data_and_model_manifests']=True
  status['all_formal_training_losses_finite']=True
  status['inference_and_protocol_code_unchanged']=True
  status['complete']=True
 (R/'analysis/completion-audit.json').write_text(json.dumps(status,indent=2));print(json.dumps(status))
if __name__=='__main__':main()
