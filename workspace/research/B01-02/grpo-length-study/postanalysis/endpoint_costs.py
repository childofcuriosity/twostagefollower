import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
tasks = ['7b-L3', '7b-L4', '7b-L5', '14b-L5', '14b-L6', '14b-L7']
records = []
lines = ['## Inference costs for step100 greedy tests', '',
         'Each condition totals 512 examples per seed across three seeds, or 1536 fresh test responses. The table uses only the scheduled step100 endpoint, includes EOS, and does not treat multiple seeds as independent samples from one policy. Generation time is actual batch generate wall time, apportioned across outputs and summed, multiplied by the single-GPU count of 1; loading and worker waiting are excluded.', '',
         '| Setting | STEP mean output tokens | NAME mean output tokens | NAME change | STEP generation GPUh | NAME generation GPUh | NAME change |',
         '|---|---:|---:|---:|---:|---:|---:|']
for task in tasks:
    d = json.loads((R / task / 'analysis/results.json').read_text())
    row = dict(task=task)
    for c in ['STEP', 'NAME']:
        details = [x['details'] for x in d['endpoints'] if x['condition'] == c]
        n = sum(x['n'] for x in details)
        assert n == 1536
        row[c] = dict(n=n, mean_output_tokens=sum(x['output_tokens'] for x in details) / n,
                      generation_gpu_hours=sum(x['generate_seconds'] for x in details) / 3600)
    row['token_change_percent'] = 100 * (row['NAME']['mean_output_tokens'] / row['STEP']['mean_output_tokens'] - 1)
    row['generation_time_change_percent'] = 100 * (row['NAME']['generation_gpu_hours'] / row['STEP']['generation_gpu_hours'] - 1)
    s, n = row['STEP'], row['NAME']
    lines.append(f'| {task} | {s["mean_output_tokens"]:.2f} | {n["mean_output_tokens"]:.2f} | {row["token_change_percent"]:+.2f}% | {s["generation_gpu_hours"]:.4f} | {n["generation_gpu_hours"]:.4f} | {row["generation_time_change_percent"]:+.2f}% |')
    records.append(row)
lines += ['', 'Timing depends on the longest output in each batch and on scheduling. Fewer output tokens do not guarantee a proportional decrease in generate time. These measured time differences are not a cross-hardware or independent throughput benchmark. Full training and evaluation use the same frozen generation caps, with no relaxed budget for NAME.']
p = R / 'COSTS.md'
p.write_text(p.read_text().split('## Inference costs for step100 greedy tests')[0].rstrip() + '\n\n' + '\n'.join(lines) + '\n')
(R / 'analysis/endpoint-costs.json').write_text(json.dumps(records, indent=2) + '\n')
print(json.dumps(records, indent=2))
