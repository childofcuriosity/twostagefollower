import json,sys
from pathlib import Path
import torch
from safetensors.torch import load_file
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'src'))
from common import readrows,key,sha,write,CONDITIONS,SEEDS,OLD,B
freeze=json.loads((R/'config/freeze-manifest.json').read_text());manifest=json.loads((R/'data/manifest.json').read_text())
sets={}
for split,n in [('train',4096),('validation',256),('test',512),('precheck',64)]:
 rows=readrows(R/f'data/{split}.jsonl');sets[split]={key(x) for x in rows}
 assert len(rows)==len(sets[split])==n
 assert sha(R/f'data/{split}.jsonl')==manifest['datasets'][split]['sha256']
excluded={key(x) for x in readrows(R/'data/excluded-old-L2.jsonl')}
for a,sa in sets.items():
 assert not sa&excluded
 for b,sb in sets.items():
  if a!=b:assert not sa&sb
for c in CONDITIONS:assert sha(R/f'config/prompt-{c}.txt')==sha(OLD/f'prompts/{c}.txt')==manifest['prompt_sha256'][c]
assert sha(B/'scale-study/src/audit.py')==manifest['legacy_score_sha256']
for seed in SEEDS:
 for c in CONDITIONS:
  d=R/f'runs/v1-{c}-s{seed}';job=json.loads((d/'job.json').read_text())
  assert freeze['created']<job['started'] and job['resume'] is None and not job['precheck']
  w=load_file(str(d/'checkpoint-000/adapter_model.safetensors'))
  assert all(torch.count_nonzero(t)==0 for name,t in w.items() if 'lora_B' in name)
  for name in ['engine.py','common.py','train.py']:assert job['source'][name]==freeze['source'][name]
  assert not list(d.glob('failure-*.json'))
  assert json.loads((R/f'infrastructure/formal-{c}-s{seed}.json.exit.json').read_text())['returncode']==0
for worker in range(4):assert json.loads((R/f'infrastructure/evaluator-{worker}.json.exit.json').read_text())['returncode']==0
assert json.loads((R/'analysis/precheck-complete.json').read_text())['passed']
results=json.loads((R/'analysis/results.json').read_text())
assert results['fixed_checkpoints_verified']==66 and results['formal_candidates_verified']==76800 and results['independent_eval_outputs_verified']==19968
write(R/'analysis/final-audit.json',dict(passed=True,data_disjoint=True,original_prompts_and_scorer_unchanged=True,formal_frozen_before_start=True,zero_LoRA_B_at_step0=True,six_training_jobs_exit_zero=True,four_eval_workers_exit_zero=True,formal_checkpoints=66,formal_candidates=76800,unique_evaluation_outputs=19968,resource_clearance_requires_separate_live_check=True))
print('FINAL_ARTIFACT_AUDIT_PASSED')
