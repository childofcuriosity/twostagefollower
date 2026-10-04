import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
tasks = ['7b-L3', '7b-L4', '7b-L5', '14b-L5', '14b-L6', '14b-L7']
records = []
lines = ['## step100贪心测试的推理开销', '',
         '每个条件合计三个seed各512题，共1536个新测试回答；下表只取预定step100端点，包含EOS，不把多个seed当同一策略的独立采样。生成时间为实际batch generate墙钟按输出均摊后合计，乘单卡数1；不含加载与worker等待。', '',
         '| 组合 | STEP平均输出token | NAME平均输出token | NAME变化 | STEP生成GPUh | NAME生成GPUh | NAME变化 |',
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
lines += ['', '时间受batch内最长输出及调度影响，输出token减少不保证按相同比例减少generate时间。本轮测得的时间差不是跨硬件或独立吞吐基准。完整训练与评测采用相同冻结生成上限；没有为NAME放宽预算。']
p = R / 'COSTS.md'
p.write_text(p.read_text().split('## step100贪心测试的推理开销')[0].rstrip() + '\n\n' + '\n'.join(lines) + '\n')
(R / 'analysis/endpoint-costs.json').write_text(json.dumps(records, indent=2) + '\n')
print(json.dumps(records, indent=2))
