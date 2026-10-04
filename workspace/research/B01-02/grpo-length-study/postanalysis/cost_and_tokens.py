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
lines = ['# 计算量、输出token与结束原因', '',
         '所有token数由实际保存的output_ids逐条复核，包含真实EOS，排除prompt与padding。EOS必须在输出末尾，达到上限必须恰好等于冻结cap；训练loss记录的token总数也与原始候选一致。', '',
         '| 组合 | STEP训练token | NAME训练token | NAME相对变化 | STEP训练段GPUh | NAME训练段GPUh | NAME相对变化 |',
         '|---|---:|---:|---:|---:|---:|---:|']
for x in records:
    s, n = [x['conditions'][c]['training'] for c in ['STEP', 'NAME']]
    lines.append(f'| {x["task"]} | {s["output_tokens"]:,} | {n["output_tokens"]:,} | {x["NAME_vs_STEP_training_token_percent"]:+.2f}% | {s["post_nccl_run_gpu_hours"]:.3f} | {n["post_nccl_run_gpu_hours"]:.3f} | {x["NAME_vs_STEP_training_segment_gpu_percent"]:+.2f}% |')
lines += ['', '每格合计三个seed、38400候选。训练段GPUh=各run在NCCL初始化结束后计时的墙钟×2，含加载、采样、反向、保存与等待；不含此前的进程/NCCL启动。配对在同一物理双卡slot顺序运行。时间差是本轮测量，不等同于纯GPU内核加速率。输出长度是生成行为的结果，不能把成功率差全部归因于标签自身的token长度。', '',
          '## 全部作业占用与嵌套计时', '',
          '| 范围 | GPU小时 |', '|---|---:|']
for key, label in [('precheck', '预检与恢复'), ('formal_training', '正式配对训练完整作业'), ('evaluation_workers', '评测worker完整生命周期')]:
    lines.append(f'| {label} | {lifecycle["allocated_gpu_hours"][key]:.3f} |')
lines += [f'| 合计 | {lifecycle["total_allocated_gpu_hours"]:.3f} |', '',
          f'评测任务计时合计{lifecycle["evaluation_task_gpu_hours"]:.3f} GPUh，其中模型generate计时{lifecycle["evaluation_generation_gpu_hours"]:.3f} GPUh。这两项嵌套于worker生命周期，不能再加入上表总计。完整作业口径包括启动、加载和等待，未用稀疏利用率采样估计GPU内核活动时间。纯CPU数据准备、评分和作图不计GPU时长。', '',
          '资源由6个双卡训练slot+4评测卡，在首小时调整为7个双卡slot+2评测卡；训练队列全部派出且有两卡释放后，增加2评测卡收尾。所有调整只影响资源调度，冻结模型、数据、采样、评分及训练预算未改，训练没有中断重启。', '',
          '## 实际样本与截断', '',
          f'正式候选{totals["training"]["outputs"]:,}条，输出token {totals["training"]["output_tokens"]:,}，上限截断{totals["training"]["truncated"]}条。独立生成的预定评测{totals["evaluation"]["outputs"]:,}条，输出token {totals["evaluation"]["output_tokens"]:,}，上限截断{totals["evaluation"]["truncated"]}条。其余均由EOS结束，EOS本身不等于任务成功。', '',
          '另有9216条预检/恢复实际候选：12个条件任务各4次原始更新+2次恢复重放。恢复重放不当作独立seed或正式证据，成本计入预检。原始模型step0每组合条件只生成一次并由三个seed引用，没有将引用数伪装为独立生成数。', '',
          '完整逐组训练/评测token及结束原因：analysis/cost-and-token-audit.json；逐个作业分配：analysis/lifecycle-audit.json。']
(R / 'COSTS.md').write_text('\n'.join(lines) + '\n')
print(json.dumps(totals, indent=2))
