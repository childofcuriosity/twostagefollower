"""Final infrastructure and freeze audit; run only after computation finishes.

Job lifecycle allocation includes NCCL startup, loading and idle evaluator time.
It is distinct from update timers and must not be added to them.
"""
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
TASKS = ['7b-L3', '7b-L4', '7b-L5', '14b-L5', '14b-L6', '14b-L7']

def read(p):
    return json.loads(p.read_text())

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

assert (R / 'analysis/computation-complete.json').exists()
freeze = read(R / 'config/freeze-manifest.json')
reference = R / 'snapshots/reference-inputs'
for name, info in read(reference / 'manifest.json').items():
    assert sha(reference / name) == info['sha256'], name
    assert sha(Path(info['source'])) == info['sha256'], name
for name, digest in freeze['source'].items():
    assert sha(R / 'src' / name) == digest, name
    assert sha(R / 'snapshots/formal-v1' / name) == digest, name

jobs = []
for pattern, stage, cards, expected in [
    ('precheck-*.json', 'precheck', 2, 12),
    ('formal-pair-*.json', 'formal_training', 2, 18),
    ('evaluator-*.json', 'evaluation_workers', 1, 8),
]:
    paths = [p for p in (R / 'infrastructure').glob(pattern)
             if not p.name.endswith(('.launched.json', '.exit.json'))
             and p.name != 'precheck-state.json']
    assert len(paths) == expected, (stage, len(paths))
    for p in paths:
        launched = read(p.with_suffix('.json.launched.json'))
        done = read(p.with_suffix('.json.exit.json'))
        assert done['returncode'] == 0, p
        if stage != 'precheck':
            assert launched['started'] >= freeze['created'], p
        jobs.append(dict(name=p.stem, stage=stage, cards=cards,
                         started=launched['started'], finished=done['finished'],
                         wall_seconds=done['seconds'],
                         allocated_gpu_hours=cards * done['seconds'] / 3600))

for task in TASKS:
    root = R / task
    manifest = read(root / 'config/freeze-manifest.json')
    assert sha(root / 'config/frozen.json') == manifest['config_sha256']
    assert sha(root / 'data/manifest.json') == manifest['data_manifest_sha256']
    data = read(root / 'data/manifest.json')
    assert data['legacy_score_sha256'] == sha(reference / 'legacy-audit.py')
    for condition, digest in data['prompt_sha256'].items():
        assert sha(reference / (condition + '.txt')) == digest
    for split, info in data['datasets'].items():
        assert sha(root / 'data' / (split + '.jsonl')) == info['sha256']
    for seed in [301, 302, 303]:
        for condition in ['STEP', 'NAME']:
            run = root / f'runs/v1-{condition}-s{seed}'
            job = read(run / 'job.json')
            done = read(run / 'complete.json')
            assert job['started'] >= manifest['created']
            assert job['resume'] is None and not job['precheck']
            assert done['updates'] == 100 and done['started_from'] == 0
            assert job['source'] == freeze['source']

eval_meta = [read(p) for p in (R / 'eval/outputs').glob('*/complete.json')]
assert len(eval_meta) == 1680
for meta in eval_meta:
    assert meta['config_sha256'] == sha(R / meta['task'] / 'config/frozen.json')
    assert meta['split'] in ['test', 'validation']
    if meta['split'] == 'test':
        assert meta['step'] in [0, 100]
    else:
        assert meta['step'] in range(0, 101, 10)

summary = {stage: sum(j['allocated_gpu_hours'] for j in jobs if j['stage'] == stage)
           for stage in ['precheck', 'formal_training', 'evaluation_workers']}
result = dict(passed=True, jobs=jobs, allocated_gpu_hours=summary,
              total_allocated_gpu_hours=sum(summary.values()),
              evaluation_task_gpu_hours=sum(m['wall_seconds'] for m in eval_meta) / 3600,
              evaluation_generation_gpu_hours=sum(m['generate_seconds'] for m in eval_meta) / 3600,
              caveat='Lifecycle allocation includes startup/loading/waiting; nested timers are not additive. Resource release requires a separate live process/GPU check.')
(R / 'analysis/lifecycle-audit.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: v for k, v in result.items() if k != 'jobs'}, indent=2))
