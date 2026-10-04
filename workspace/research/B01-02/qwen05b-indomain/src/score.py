"""Score frozen in-domain predictions with the historical strict trajectory endpoint."""
from common import R, B, SEEDS, CONDITIONS, sha, write
import argparse
import importlib.util
import json
import math
import re
import statistics
import time

parser = argparse.ArgumentParser()
parser.add_argument('--max-length', type=int, default=2)
parser.add_argument('--conditions', nargs='+', choices=CONDITIONS, default=['flat'])
args = parser.parse_args()

legacy_path = B/'scale-study/src/audit.py'
spec = importlib.util.spec_from_file_location('frozen_legacy_strict_audit', legacy_path)
legacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy)
header = re.compile(r'(?m)^[A-Za-z][A-Za-z0-9]*:$')
scores = {}
records = []
frozen_ids = None
for condition in args.conditions:
    per_seed = []
    for seed in SEEDS:
        run = R/f'runs/L{args.max_length}-{condition}-s{seed}'
        assert (run/'complete.json').exists(), f'Missing complete marker: {run}'
        pred_path = run/'runs'/f'{condition}-original-s{seed}'/'predictions.jsonl'
        rows = [json.loads(line) for line in pred_path.read_text().splitlines()]
        expected_n = 128 if args.max_length == 2 else json.loads((R/f'data/L{args.max_length}/manifest.json').read_text())['test_rows']
        assert len(rows) == expected_n, (run, len(rows))
        ids = [row['id'] for row in rows]
        if frozen_ids is None:
            frozen_ids = ids
        assert ids == frozen_ids, f'Test set mismatch: {run}'
        out = []
        for row in rows:
            normalized = dict(row)
            normalized['raw'] = header.sub('step:', row['raw'])
            if args.max_length >= 4:
                normalized['max_new_tokens'] = json.loads((R/f'data/L{args.max_length}/manifest.json').read_text())['generation_cap']
            result = legacy.check(normalized)
            if condition in ('flat', 'macro'):
                # Ensure normalization is equivalent to the historical endpoint.
                assert legacy.check(row)['strict_trace'] == result['strict_trace']
            out.append(result)
            records.append({'condition': condition, 'seed': seed,
                            'id': row['id'], 'depth': len(row['chain']),
                            'strict_trace': result['strict_trace'],
                            'final_answer': result['accuracy'],
                            'old_score': result})
        by_depth = {str(d): {'correct': sum(x['strict_trace'] for x, row in zip(out, rows)
                                            if len(row['chain']) == d),
                             'n': sum(len(row['chain']) == d for row in rows)}
                    for d in sorted({len(row['chain']) for row in rows})}
        per_seed.append({'seed': seed, 'correct': sum(x['strict_trace'] for x in out),
                         'n': len(out), 'rate': statistics.mean(x['strict_trace'] for x in out),
                         'by_depth': by_depth, 'predictions_sha256': sha(pred_path)})
    rates = [x['rate'] for x in per_seed]
    scores[condition] = {'mean': statistics.mean(rates),
                         'sample_sd': statistics.stdev(rates),
                         'seeds': per_seed}

paired = {}
if 'flat' in scores:
    baseline = {x['seed']: x['rate'] for x in scores['flat']['seeds']}
    for condition in args.conditions:
        if condition == 'flat':
            continue
        diffs = [x['rate'] - baseline[x['seed']] for x in scores[condition]['seeds']]
        mean = statistics.mean(diffs)
        # Normal-approximation interval is descriptive; tasks and mapping remain fixed.
        half_width = 1.96 * statistics.stdev(diffs) / math.sqrt(len(diffs))
        paired[condition] = {'per_seed': dict(zip(SEEDS, diffs)), 'mean': mean,
                             'sample_sd': statistics.stdev(diffs),
                             'descriptive_95pct_interval': [mean-half_width, mean+half_width],
                             'positive_seeds': sum(x > 0 for x in diffs),
                             'negative_seeds': sum(x < 0 for x in diffs)}

decision = None
if 'flat' in scores:
    rates = [x['rate'] for x in scores['flat']['seeds']]
    decision = {'eligible_for_four_label_comparison':
                statistics.mean(rates) <= .90 and sum(x <= .95 for x in rates) >= 15,
                'rule': 'flat mean <= 0.90 and at least 15/20 seeds <= 0.95',
                'seeds_at_or_below_95pct': sum(x <= .95 for x in rates)}

write(R/'analysis'/f'scores-L{args.max_length}.json',
      {'max_length': args.max_length, 'conditions': args.conditions,
       'legacy_audit_sha256': sha(legacy_path), 'test_ids': frozen_ids,
       'scores': scores, 'paired_vs_flat': paired, 'decision': decision,
       'scored_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())})
with (R/'analysis'/f'graded-L{args.max_length}.jsonl').open('w') as f:
    for row in records:
        f.write(json.dumps(row, ensure_ascii=False)+'\n')
print(json.dumps({'length': args.max_length, 'means':
                  {k: v['mean'] for k, v in scores.items()}, 'decision': decision}))
