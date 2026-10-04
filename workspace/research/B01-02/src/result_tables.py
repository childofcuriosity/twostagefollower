import json,statistics,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name):return json.loads((ROOT/f'runs/{name}/summary.json').read_text())
def pct(x):return f'{100*x:.2f}'
lines=['# Measured results','', 'All percentages report accuracy or percentage-point differences, not relative improvements. OOD contains 384 examples from 96 independent program compositions. Training seeds are 11/22/33.','', '## Main experiment','', '| Condition | Mean IID | OOD seeds 11/22/33 | Mean OOD | Mean stress-set accuracy | Effective training target tokens per run | Mean generated tokens/example |','|---|---:|---|---:|---:|---:|---:|']
for c in ['flat','macro','natural','shuffled']:
 ss=[load(f'{c}-original-s{s}') for s in [11,22,33]]
 acc=lambda split:statistics.mean(s['evaluation']['groups'][split]['accuracy'] for s in ss)
 tokens=statistics.mean(s['evaluation']['generated_tokens']/560 for s in ss)
 lines.append(f"| {c} | {pct(acc('iid'))} | {' / '.join(pct(s['evaluation']['groups']['ood']['accuracy']) for s in ss)} | {pct(acc('ood'))} | {pct(acc('pressure'))} | {ss[0]['training']['counts']['target_tokens']:,} | {tokens:.1f} |")
lines+=['','## Interventions','', '| World | Mean IID | OOD seeds 11/22/33 | Mean OOD |','|---|---:|---|---:|']
for w in ['original','renamed','semantic']:
 ss=[load(f'macro-{w}-s{s}') for s in [11,22,33]]
 lines.append(f"| {w} | {pct(statistics.mean(s['evaluation']['groups']['iid']['accuracy'] for s in ss))} | {' / '.join(pct(s['evaluation']['groups']['ood']['accuracy']) for s in ss)} | {pct(statistics.mean(s['evaluation']['groups']['ood']['accuracy'] for s in ss))} |")
lines+=['','## Post hoc alignment controls','', '| Boundary label | Mean IID | OOD seeds 11/22/33 | Mean OOD | Effective training target tokens per run |','|---|---:|---|---:|---:|']
alignment={}
for c in ['stable','call']:
 ss=[load(f'macro-original-s{s}-tagged-{c}') for s in [11,22,33]]
 alignment[c]=ss
 lines.append(f"| {c} | {pct(statistics.mean(s['evaluation']['groups']['iid']['accuracy'] for s in ss))} | {' / '.join(pct(s['evaluation']['groups']['ood']['accuracy']) for s in ss)} | {pct(statistics.mean(s['evaluation']['groups']['ood']['accuracy'] for s in ss))} | {ss[0]['training']['counts']['target_tokens']:,} |")
for a,b in zip(alignment['stable'],alignment['call']):assert a['training']['counts']==b['training']['counts']
lines+=['','## Post hoc external-routing diagnostic','', 'An external loop calls macros individually; the model supplies every intermediate state. This cannot replace autonomous-execution results. Each evaluation uses 96 independent programs.','', '| Model | Accuracy by seed | Mean |','|---|---|---:|']
for c in ['flat','macro','frozen']:
 seeds=[11] if c=='frozen' else [11,22,33]
 ss=[json.loads((ROOT/f'analysis/routing-probe/{c}-s{s}-summary.json').read_text()) for s in seeds]
 lines.append(f"| {c} | {' / '.join(pct(s['accuracy']) for s in ss)} | {pct(statistics.mean(s['accuracy'] for s in ss))} |")
lines+=['','## Frozen baselines','', '| Prompt | IID | OOD | Stress set |','|---|---:|---:|---:|']
for c in ['no-library','with-library']:
 ss=load(f'frozen-original-s11-{c}')['evaluation']['groups']
 lines.append(f"| {c} | {pct(ss['iid']['accuracy'])} | {pct(ss['ood']['accuracy'])} | {pct(ss['pressure']['accuracy'])} |")
lines+=['','## Primary statistics','', '```json',json.dumps(json.loads((ROOT/'analysis/results.json').read_text())['primary_comparisons']['macro-vs-flat'],indent=2),'```','']
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
