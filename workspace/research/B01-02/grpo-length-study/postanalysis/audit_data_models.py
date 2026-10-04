import concurrent.futures
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]

def read(p):
    return json.loads(p.read_text())

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def keys(p):
    rows = [json.loads(line) for line in p.read_text().splitlines()]
    return rows, {(tuple(x['chain']), tuple(x['x'])) for x in rows}

manifest = read(R / 'datasets/manifest.json')
old = {i: set() for i in range(3, 8)}
for source in manifest['sources']:
    p = Path(source['path'])
    assert sha(p) == source['sha256']
    for line in p.read_text().splitlines():
        x = json.loads(line)
        if isinstance(x, dict) and isinstance(x.get('chain'), list) and isinstance(x.get('x'), list):
            length = len(x['chain'])
            if length in old and len(x['x']) == 4:
                old[length].add((tuple(x['chain']), tuple(x['x'])))
datasets = []
for length in range(3, 8):
    root = R / f'datasets/L{length}'
    excluded_rows, excluded = keys(root / 'excluded-old.jsonl')
    assert excluded == old[length]
    seen = set(excluded)
    for split, n in [('train', 4096), ('validation', 256), ('test', 512), ('precheck', 64)]:
        p = root / (split + '.jsonl')
        rows, current = keys(p)
        assert len(rows) == len(current) == n and not (current & seen)
        assert sha(p) == manifest['lengths'][str(length)]['datasets'][split]['sha256']
        assert all(len(x['chain']) == length and len(x['x']) == 4 and
                   all(0 <= t < 9 for t in x['chain']) and all(0 <= d < 10 for d in x['x'])
                   for x in rows)
        seen |= current
    datasets.append(dict(length=length, old_excluded=len(excluded),
                         all_splits_unique_and_disjoint=True))
for split in ['train', 'validation', 'test', 'precheck']:
    assert sha(R / '7b-L5/data' / (split + '.jsonl')) == sha(R / '14b-L5/data' / (split + '.jsonl'))

def model_check(name):
    model = R.parent / 'prompt-only/models' / ('qwen' + name)
    d = read(model / 'download-manifest.json')
    for entry in d['files']:
        p = model / entry['file']
        assert p.stat().st_size == entry['bytes']
        assert sha(p) == entry['sha256'], str(p)
    for task in R.glob(name + '-L*/config/frozen.json'):
        assert read(task)['model_revision'] == d['revision']
    return dict(model=name, revision=d['revision'], all_original_files_sha256_match=True,
                files=len(d['files']))

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    models = list(pool.map(model_check, ['7b', '14b']))

result = dict(passed=True, datasets=datasets, shared_L5_verified=True,
              historical_source_files_verified=len(manifest['sources']), models=models)
(R / 'analysis/data-model-final-audit.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
