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
lines = [f'# {R.name}: error and heading checks', '',
         'The analysis below interprets saved outputs without changing the strict primary score. Mutually exclusive categories follow a fixed priority: Answer count, unknown lines, operation sequence, numerical steps, and final Answer only. This is not temporal first-error attribution. Original overlapping error flags are retained in analysis/results.json.', '',
         '| Condition/seed | Failures/512 | Answer count | Unknown lines | Operation sequence | Numerical steps | Final Answer only | Extra Trace heading only | Other heading issues | Truncation |',
         '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
for x in records:
    counts = [x['reasons'].get(k, 0) for k in reason_keys]
    counts += [x['titles'].get('extra_Trace_heading_only', 0),
               x['titles'].get('other_title_noncompliance', 0), x['endings'].get('length', 0)]
    lines.append(f'| {x["condition"]}/{x["seed"]} | {x["strict_failures"]} | ' +
                 ' | '.join(map(str, counts)) + ' |')
lines += ['', 'base denotes the original model at step0; other rows are seed-specific step100 results. Extra Trace headings can occur alongside strict success and do not indicate additional tool calls. Operation-sequence mismatches include omitted, added, substituted, and reordered raw operations; they cannot directly identify how many high-level tool calls were omitted. EOS indicates voluntary stopping, not necessarily complete execution. Priority-based categories can mask other errors: once operation sequences improve, more failures may be categorized as numerical errors. An increased count in that category alone does not establish worse numerical computation; also consult the overlapping numerical-error flags in the main report.', '',
          'Examples are selected by the smallest example ID within each condition/seed/error category, showing raw and reference trajectories. Use the table above for category frequencies.', '']
for x in cases:
    lines += [f'## {x["condition"]} seed{x["seed"]} {x["id"]}：{x["category"]}', '',
              f'Strictly correct={x["grading"]["strict"]}; heading compliant={x["grading"]["header_compliant"]}; input={x["input"]}; tool indices={x["chain"]}。', '',
              'Actual output:', '```text', x['raw'], '```', '',
              'Reference trajectory:', '```text', x['expected'], '```', '']
(R / 'CASE_REVIEW.md').write_text('\n'.join(lines) + '\n')
print(json.dumps(dict(task=R.name, groups=len(records), cases=len(cases)), indent=2))
