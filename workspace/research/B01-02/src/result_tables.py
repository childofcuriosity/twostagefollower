import json,statistics,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name):return json.loads((ROOT/f'runs/{name}/summary.json').read_text())
def pct(x):return f'{100*x:.2f}'
lines=['# 实测结果表','', '所有百分比均为准确率或百分点，不是相对提升。OOD有384题、96个独立程序组合；三个训练种子为11/22/33。','', '## 主实验','', '| 条件 | IID均值 | OOD种子11/22/33 | OOD均值 | 压力集均值 | 每次有效训练target token | 平均生成token/题 |','|---|---:|---|---:|---:|---:|---:|']
for c in ['flat','macro','natural','shuffled']:
 ss=[load(f'{c}-original-s{s}') for s in [11,22,33]]
 acc=lambda split:statistics.mean(s['evaluation']['groups'][split]['accuracy'] for s in ss)
 tokens=statistics.mean(s['evaluation']['generated_tokens']/560 for s in ss)
 lines.append(f"| {c} | {pct(acc('iid'))} | {' / '.join(pct(s['evaluation']['groups']['ood']['accuracy']) for s in ss)} | {pct(acc('ood'))} | {pct(acc('pressure'))} | {ss[0]['training']['counts']['target_tokens']:,} | {tokens:.1f} |")
lines+=['','## 干预','', '| 世界 | IID均值 | OOD种子11/22/33 | OOD均值 |','|---|---:|---|---:|']
for w in ['original','renamed','semantic']:
 ss=[load(f'macro-{w}-s{s}') for s in [11,22,33]]
 lines.append(f"| {w} | {pct(statistics.mean(s['evaluation']['groups']['iid']['accuracy'] for s in ss))} | {' / '.join(pct(s['evaluation']['groups']['ood']['accuracy']) for s in ss)} | {pct(statistics.mean(s['evaluation']['groups']['ood']['accuracy'] for s in ss))} |")
lines+=['','## 事后对齐对照','', '| 边界标签 | IID均值 | OOD种子11/22/33 | OOD均值 | 每次有效训练target token |','|---|---:|---|---:|---:|']
alignment={}
for c in ['stable','call']:
 ss=[load(f'macro-original-s{s}-tagged-{c}') for s in [11,22,33]]
 alignment[c]=ss
 lines.append(f"| {c} | {pct(statistics.mean(s['evaluation']['groups']['iid']['accuracy'] for s in ss))} | {' / '.join(pct(s['evaluation']['groups']['ood']['accuracy']) for s in ss)} | {pct(statistics.mean(s['evaluation']['groups']['ood']['accuracy'] for s in ss))} | {ss[0]['training']['counts']['target_tokens']:,} |")
for a,b in zip(alignment['stable'],alignment['call']):assert a['training']['counts']==b['training']['counts']
lines+=['','## 事后外部路由诊断','', '外部循环逐个调用宏，模型提供全部中间状态；不能替换自主执行结果。每次96个独立程序。','', '| 模型 | 各种子准确率 | 均值 |','|---|---|---:|']
for c in ['flat','macro','frozen']:
 seeds=[11] if c=='frozen' else [11,22,33]
 ss=[json.loads((ROOT/f'analysis/routing-probe/{c}-s{s}-summary.json').read_text()) for s in seeds]
 lines.append(f"| {c} | {' / '.join(pct(s['accuracy']) for s in ss)} | {pct(statistics.mean(s['accuracy'] for s in ss))} |")
lines+=['','## 冻结基线','', '| 提示 | IID | OOD | 压力集 |','|---|---:|---:|---:|']
for c in ['no-library','with-library']:
 ss=load(f'frozen-original-s11-{c}')['evaluation']['groups']
 lines.append(f"| {c} | {pct(ss['iid']['accuracy'])} | {pct(ss['ood']['accuracy'])} | {pct(ss['pressure']['accuracy'])} |")
lines+=['','## 主统计','', '```json',json.dumps(json.loads((ROOT/'analysis/results.json').read_text())['primary_comparisons']['macro-vs-flat'],indent=2),'```','']
(ROOT/'analysis/RESULT_TABLES.md').write_text('\n'.join(lines));print('\n'.join(lines))
# Device reservation estimates include process startup/model loading.
phases={}
for phase in ['core','intervention','baseline']:
 rs=json.loads((ROOT/f'analysis/{phase}-completed.json').read_text());phases[phase]=sum(r.get('wall_seconds',0) for r in rs)/3600
post=json.loads((ROOT/'analysis/posthoc-completed.json').read_text())
for kind in ['alignment','routing']:phases[kind]=sum(r['wall_seconds'] for r in post if r['kind']==kind)/3600
phases['discovery']=json.loads((ROOT/'data/library.json').read_text())['wall_seconds']/3600
phases['calibration_excluding_load']=load('flat-original-s11-calibration')['gpu_hours']
(ROOT/'analysis/compute-cost.json').write_text(json.dumps({'reserved_gpu_hours_by_phase':phases,'total':sum(phases.values()),'not_kernel_busy_time':True,'excludes_install_download_idle_time':True,'baseline_initial_argument_failures_reserved_seconds':20.11,'note':'Small job startup overhead and calibration model-load time are not fully instrumented. No claim of exact energy consumption.'},indent=2))
