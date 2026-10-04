"""Descriptive subtask columns and oracle-product versus real execution; no selection."""
import collections, json
from common import R, write


def main():
    data = json.loads((R/'analysis/results.json').read_text())
    index = collections.defaultdict(collections.Counter)
    for row in data['results']:
        if not row['split'].startswith('length'):
            continue
        label = row['mode'] if row['kind'] == 'compose' else row['condition'] + ':' + row['mode']
        for length in [row['length'], 'all']:
            index[row['model'], row['seed'], row['step'], label, length].update(row['counts'])
    records = []
    for model in ['qwen3b', 'qwen32b']:
        for step in [256, 512]:
            for length in ['all', 3, 4, 5, 6, 8]:
                for label in ['joint:joint', 'SJ', 'JE', 'SE']:
                    seeds = []
                    for seed in [11, 22, 33]:
                        counts = index.get((model, seed, step, label, length))
                        if not counts:
                            continue
                        n = counts['n']
                        a = counts['sequence_correct']/n
                        b = counts['all_expansions_correct']/n
                        seeds.append(dict(seed=seed, n=n, sequence=a, all_emitted_bodies=b,
                                          product=a*b, complete=counts['complete']/n))
                    if len(seeds) != 3:
                        continue
                    avg = {k: sum(s[k] for s in seeds)/3 for k in
                           ['sequence', 'all_emitted_bodies', 'product', 'complete']}
                    record = dict(model=model, step=step, length=length, route=label,
                                  seeds=seeds, mean=avg)
                    if label == 'SE':
                        oracle = []
                        for seed in [11, 22, 33]:
                            a = index.get((model, seed, step, 'operation_oracle:operation_oracle', length))
                            b = index.get((model, seed, step, 'order_oracle:order_oracle', length))
                            if a and b:
                                pa, pb = a['complete']/a['n'], b['complete']/b['n']
                                oracle.append(dict(seed=seed, order_with_correct_operations=pa,
                                                   operations_with_correct_order=pb, product=pa*pb))
                        record['oracle_seeds'] = oracle
                        if len(oracle) == 3:
                            record['oracle_product_mean'] = sum(s['product'] for s in oracle)/3
                    records.append(record)
    write(R/'analysis/decomposition.json', dict(records=records, note=(
        'A: full name sequence correct. B: all emitted calls expand correctly; missing calls fail A, '
        'not B. Product is computed within each seed before averaging. Oracle products use separate '
        'correct-context evaluations, are predictions only, and are not actual no-oracle composition.')))
    lines = ['# Two actual-execution subtasks and full success',
             'Correct sequence means the entire task name list is correct. All operations correct means every actually generated call is expanded correctly; missing calls fail the sequence column.',
             'Products are computed within each training seed and then averaged. A product close to full-task success indicates compatible aggregate rates, not proven statistical independence.',
             'The separately listed correct-context product comes from two tests where a program supplies the correct other component; it is not actual execution performance.',
             '|Model|Training steps|Tools|Name writer / operation writer|Correct sequence|All generated operations correct|Product of both columns|Actual full-task success|Correct-context product|',
             '|---|---:|---|---|---:|---:|---:|---:|---:|']
    labels = {'joint:joint': 'Joint / joint', 'SJ': 'Sequence specialist / joint',
              'JE': 'Joint / operation specialist', 'SE': 'Sequence specialist / operation specialist'}
    for row in records:
        v = row['mean']
        cells = [f'{100*v[k]:.2f}%' for k in ['sequence', 'all_emitted_bodies', 'product', 'complete']]
        p = row.get('oracle_product_mean')
        cells.append('—' if p is None else f'{100*p:.2f}%')
        lines.append(f'|{row["model"]}|{row["step"]}|{row["length"]}|{labels[row["route"]]}|'+'|'.join(cells)+'|')
    (R/'SUBTASKS_AND_EXECUTION.md').write_text('\n'.join(lines)+'\n')
    print('Decomposition cells:', len(records))


if __name__ == '__main__':
    main()
