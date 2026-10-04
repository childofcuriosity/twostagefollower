"""Verify actual generated token streams and report non-additive cost measures."""
import collections
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
TASKS = ['7b-L3', '7b-L4', '7b-L5', '14b-L5', '14b-L6', '14b-L7']
assert (R / 'analysis/computation-complete.json').exists()

def read(p):
    return json.loads(p.read_text())

def audit(paths, cap, eos):
    tokens = count = 0
    endings = collections.Counter()
    for p in paths:
        with p.open() as f:
            for line in f:
                x = json.loads(line)
                ids = x['output_ids']
                assert len(ids) == x['generated_tokens'] and len(ids) <= cap
                if x['finish_reason'] == 'eos':
                    assert ids and ids[-1] in eos and not any(t in eos for t in ids[:-1])
                else:
                    assert x['finish_reason'] == 'length'
                    assert len(ids) == cap and not any(t in eos for t in ids)
                tokens += len(ids)
                count += 1
                endings[x['finish_reason']] += 1
    return dict(outputs=count, output_tokens=tokens, endings=dict(endings))

records = []
precheck = []
for task in TASKS:
    cfg = read(R / task / 'config/frozen.json')
    eos = read(Path(cfg['model_path']) / 'generation_config.json')['eos_token_id']
    eos = {eos} if isinstance(eos, int) else set(eos)
    d = read(R / task / 'analysis/results.json')
    row = dict(task=task, conditions={})
    for c in ['STEP', 'NAME']:
        train = audit(sorted((R / task / 'runs').glob(f'v1-{c}-s*/candidates/*.jsonl')),
                      cfg['max_new_tokens'], eos)
        metrics = [x for x in d['training'] if x['condition'] == c]
        assert train['outputs'] == 38400
        assert train['output_tokens'] == sum(x['output_tokens'] for x in metrics)
        assert train['endings'].get('length', 0) == sum(x['truncated'] for x in metrics)
        evaluation = audit(sorted((R / 'eval/outputs').glob(f'{task}-{c}-*/predictions.jsonl')),
                           cfg['max_new_tokens'], eos)
        assert evaluation['outputs'] == 9984
        train['post_nccl_run_gpu_hours'] = sum(x['allocated_gpu_seconds'] for x in metrics) / 3600
        row['conditions'][c] = dict(training=train, evaluation=evaluation)
        pre = audit(sorted((R / task / 'precheck').glob(f'v1-{c}*/candidates/*.jsonl')),
                    cfg['max_new_tokens'], eos)
        assert pre['outputs'] == 768
        precheck.append(dict(task=task, condition=c, **pre))
    s, n = [row['conditions'][c] for c in ['STEP', 'NAME']]
    row['NAME_vs_STEP_training_token_percent'] = 100 * (n['training']['output_tokens'] / s['training']['output_tokens'] - 1)
    row['NAME_vs_STEP_training_segment_gpu_percent'] = 100 * (n['training']['post_nccl_run_gpu_hours'] / s['training']['post_nccl_run_gpu_hours'] - 1)
    records.append(row)
    print('TOKEN_STREAM_AUDITED', task, flush=True)

totals = {kind: dict(outputs=sum(x['conditions'][c][kind]['outputs'] for x in records for c in ['STEP', 'NAME']),
                    output_tokens=sum(x['conditions'][c][kind]['output_tokens'] for x in records for c in ['STEP', 'NAME']),
                    truncated=sum(x['conditions'][c][kind]['endings'].get('length', 0) for x in records for c in ['STEP', 'NAME']))
          for kind in ['training', 'evaluation']}
assert totals['training']['outputs'] == 460800
assert totals['evaluation']['outputs'] == 119808
assert sum(x['outputs'] for x in precheck) == 9216
lifecycle = read(R / 'analysis/lifecycle-audit.json')
result = dict(passed=True, records=records, totals=totals, precheck_actual_outputs=9216,
              precheck=precheck, lifecycle=lifecycle['allocated_gpu_hours'],
              total_allocated_gpu_hours=lifecycle['total_allocated_gpu_hours'])
(R / 'analysis/cost-and-token-audit.json').write_text(json.dumps(result, indent=2) + '\n')
lines = ['# Compute, output tokens, and stopping reasons', '',
         'All token counts are checked record by record against saved output_ids, including actual EOS and excluding prompt and padding. EOS must be the final output token; cap-truncated outputs must exactly match the frozen cap. Token totals in training-loss records also match the raw candidates.', '',
         '| Setting | STEP training tokens | NAME training tokens | NAME relative change | STEP training-segment GPUh | NAME training-segment GPUh | NAME relative change |',
         '|---|---:|---:|---:|---:|---:|---:|']
for x in records:
    s, n = [x['conditions'][c]['training'] for c in ['STEP', 'NAME']]
    lines.append(f'| {x["task"]} | {s["output_tokens"]:,} | {n["output_tokens"]:,} | {x["NAME_vs_STEP_training_token_percent"]:+.2f}% | {s["post_nccl_run_gpu_hours"]:.3f} | {n["post_nccl_run_gpu_hours"]:.3f} | {x["NAME_vs_STEP_training_segment_gpu_percent"]:+.2f}% |')
lines += ['', 'Each cell totals three seeds and 38400 candidates. Training-segment GPUh is run wall time after NCCL initialization multiplied by 2, including loading, sampling, backpropagation, saving, and waiting, but excluding earlier process/NCCL startup. Paired conditions run sequentially in the same physical two-GPU slot. Time differences are measurements from this study, not pure GPU-kernel speedups. Output length is a result of generation behavior; success differences cannot be attributed entirely to the token lengths of the labels themselves.', '',
          '## Total job occupancy and nested timings', '',
          '| Scope | GPU-hours |', '|---|---:|']
for key, label in [('precheck', 'Prechecks and recovery'), ('formal_training', 'Complete main paired training jobs'), ('evaluation_workers', 'Complete evaluation-worker lifecycles')]:
    lines.append(f'| {label} | {lifecycle["allocated_gpu_hours"][key]:.3f} |')
lines += [f'| Total | {lifecycle["total_allocated_gpu_hours"]:.3f} |', '',
          f'Total evaluation-task time: {lifecycle["evaluation_task_gpu_hours"]:.3f} GPUh, including model generate time of {lifecycle["evaluation_generation_gpu_hours"]:.3f} GPUh. Both timings are nested within worker lifecycles and must not be added to the total above. Full-job accounting includes startup, loading, and waiting; sparse utilization samples are not used to estimate active GPU-kernel time. CPU-only data preparation, scoring, and plotting contribute no GPU time.', '',
          'Resources changed from 6 two-GPU training slots + 4 evaluation GPUs to 7 two-GPU slots + 2 evaluation GPUs in the first hour. Once all training jobs had been dispatched and two GPUs became free, 2 evaluation GPUs were added to finish the queue. These changes affected scheduling only; frozen models, data, sampling, scoring, and training budgets remained unchanged. Training was not interrupted or restarted.', '',
          '## Actual samples and truncations', '',
          f'Main candidates: {totals["training"]["outputs"]:,}; output tokens: {totals["training"]["output_tokens"]:,}; cap truncations: {totals["training"]["truncated"]}. Independently generated scheduled evaluations: {totals["evaluation"]["outputs"]:,}; output tokens: {totals["evaluation"]["output_tokens"]:,}; cap truncations: {totals["evaluation"]["truncated"]}. All other outputs end with EOS, which alone does not imply task success.', '',
          'An additional 9216 candidates were generated during prechecks/recovery: 4 original updates + 2 replayed recovery updates for each of 12 condition/tasks. Recovery replays are not independent seeds or main evidence; their costs are included in prechecks. Original-model step0 is generated once per setting/condition and referenced by three seeds; reference counts are not treated as independent generations.', '',
          'Complete per-setting training/evaluation tokens and stopping reasons: analysis/cost-and-token-audit.json; per-job allocations: analysis/lifecycle-audit.json.']
(R / 'COSTS.md').write_text('\n'.join(lines) + '\n')
print(json.dumps(totals, indent=2))
