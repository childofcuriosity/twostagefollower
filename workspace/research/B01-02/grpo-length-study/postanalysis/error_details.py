"""Describe already scored outputs; does not change reward or primary scoring."""
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from common import R, HEADER, prior, target, write

assert (R / 'analysis/results.json').exists(), 'Complete task audit required first'
records, cases = [], []
reason_keys = ['missing_or_multiple_Answer', 'unrecognized_extra_lines',
               'operation_sequence', 'numeric_step', 'final_Answer_only']
for condition in ['STEP', 'NAME']:
    for seed in ['base', 301, 302, 303]:
        step = 0 if seed == 'base' else 100
        paths = sorted((ROOT / 'eval/outputs').glob(
            f'{R.name}-{condition}-s{seed}-step{step:03d}-test-part*/predictions.jsonl'))
        assert len(paths) == 4
        rows = sorted([json.loads(line) for p in paths for line in p.read_text().splitlines()],
                      key=lambda x: x['id'])
        assert len(rows) == len({x['id'] for x in rows}) == 512
        reasons, titles, endings = collections.Counter(), collections.Counter(), collections.Counter()
        selected = set()
        for row in rows:
            g = row['grading']
            headings = [s[:-1] for s in row['raw'].splitlines() if HEADER.fullmatch(s)]
            expected = prior.labels(row, condition)
            if headings == expected:
                title_reason = 'fully_compliant'
            elif [s for s in headings if s != 'Trace'] == expected:
                title_reason = 'extra_Trace_heading_only'
            else:
                title_reason = 'other_title_noncompliance'
            titles[title_reason] += 1
            endings[row['finish_reason']] += 1
            reason = None
            if not g['strict']:
                z = g['legacy']
                if z['missing_or_multiple_answer']:
                    reason = reason_keys[0]
                elif g['extra_output']:
                    reason = reason_keys[1]
                elif g['operation_mismatch']:
                    reason = reason_keys[2]
                elif g['numeric_error']:
                    reason = reason_keys[3]
                elif not z['accuracy']:
                    reason = reason_keys[4]
                else:
                    raise AssertionError((condition, seed, row['id'], g))
                reasons[reason] += 1
            case_type = reason or (title_reason if title_reason != 'fully_compliant' else None)
            if seed != 'base' and case_type and case_type not in selected:
                selected.add(case_type)
                cases.append(dict(condition=condition, seed=seed, id=row['id'],
                                  category=case_type, input=row['x'], chain=row['chain'],
                                  raw=row['raw'], expected=target(row, condition), grading=g))
        assert sum(reasons.values()) == sum(not x['grading']['strict'] for x in rows)
        records.append(dict(condition=condition, seed=seed, step=step, n=512,
                            strict_failures=sum(reasons.values()), reasons=dict(reasons),
                            titles=dict(titles), endings=dict(endings)))

note = ('Exclusive descriptive priority: Answer count, unrecognized lines, operation sequence, '
        'local numeric step, final Answer only. Not chronological first-error attribution. '
        'Title compliance is separate and cannot be added to strict failures. '
        'Cases are the first ID per observed category/condition/seed, not prevalence estimates.')
write(R / 'analysis/error-details.json', dict(records=records, cases=cases, note=note))
lines = [f'# {R.name}：错误与标题核验', '',
         '以下只解释已保存输出，不改变严格主评分。互斥归类按Answer数量、未知行、操作序列、数字步骤、仅最终Answer的固定优先顺序进行；不是按时间定位首错。原始可重叠错误标志保存在analysis/results.json。', '',
         '| 条件/seed | 失败/512 | Answer数量 | 未知行 | 操作序列 | 数字步骤 | 仅最终Answer | 仅额外Trace标题 | 其他标题问题 | 截断 |',
         '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
for x in records:
    counts = [x['reasons'].get(k, 0) for k in reason_keys]
    counts += [x['titles'].get('extra_Trace_heading_only', 0),
               x['titles'].get('other_title_noncompliance', 0), x['endings'].get('length', 0)]
    lines.append(f'| {x["condition"]}/{x["seed"]} | {x["strict_failures"]} | ' +
                 ' | '.join(map(str, counts)) + ' |')
lines += ['', 'base为原始模型step0，其余为对应seed的step100。额外Trace标题可能与严格成功同时出现；它不代表新增工具调用。操作序列不匹配涵盖原始操作遗漏、增加、替换和顺序改变，不能直接反推遗漏了几次高层工具调用。EOS只说明主动结束，不保证执行完整。互斥优先级归类存在遮蔽：操作序列改善后，更多失败会落入数字错误类别；不能仅凭该类别计数增加就判断数字计算变差，应同时查看主报告中的可重叠数字错误标志。', '',
          '案例按每个条件/seed/错误类别的最小题目ID选取，展示原始与标准轨迹；类别频率以上表为准。', '']
for x in cases:
    lines += [f'## {x["condition"]} seed{x["seed"]} {x["id"]}：{x["category"]}', '',
              f'严格正确={x["grading"]["strict"]}；标题合规={x["grading"]["header_compliant"]}；输入={x["input"]}；工具索引={x["chain"]}。', '',
              '实际输出：', '```text', x['raw'], '```', '',
              '标准轨迹：', '```text', x['expected'], '```', '']
(R / 'CASE_REVIEW.md').write_text('\n'.join(lines) + '\n')
print(json.dumps(dict(task=R.name, groups=len(records), cases=len(cases)), indent=2))
