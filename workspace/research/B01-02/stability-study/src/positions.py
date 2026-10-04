"""Where the first operation error appears under correct-name assistance."""
import collections,json
from pathlib import Path
from common import R,write


def main():
    data=json.loads((R/'analysis/results.json').read_text())
    jobs={j['id']:j for j in json.loads((R/'analysis/jobs.json').read_text())}
    groups=collections.defaultdict(collections.Counter)
    for source in data['sources']:
        j=jobs[source['job']]
        if source['split']!='independent' or j['kind']!='curve' or source['mode']!='order_oracle':continue
        for row in map(json.loads,Path(source['source']).read_text().splitlines()):
            clean=True
            for pos,call in enumerate(row['calls'],1):
                counts=groups[j['model'],j['condition'],j['seed'],source['step'],len(row['chain']),pos]
                good=call.get('body',{}).get('correct',False)
                counts['reached']+=1;counts['correct']+=good
                counts['previous_calls_correct']+=clean
                if clean:
                    counts['correct_given_clean_previous_calls']+=good
                    counts['first_operation_error']+=not good
                clean=clean and good
    records=[dict(model=k[0],condition=k[1],seed=k[2],step=k[3],length=k[4],position=k[5],counts=dict(v)) for k,v in sorted(groups.items())]
    write(R/'analysis/operation-positions.json',dict(records=records,note=(
        'Correct-name oracle only: operations are model-generated, state is not repaired. '
        'Reached and clean-prefix denominators are distinct. Missing subsequent calls are not silently '
        'counted as observed successful calls. Position associations do not establish context-length causality.')))
    pooled=collections.defaultdict(collections.Counter)
    for row in records:
        if row['step']==512 and row['length']==8:
            pooled[row['model'],row['condition'],row['position']].update(row['counts'])
    lines=['# Where do operation errors occur when correct names are supplied?',
           'This is a diagnostic test, not unassisted actual execution. Operations can be wrong even with correct names. Current state always follows actual generation and is not corrected by the program.',
           'Previously all correct counts only examples reaching a position with no earlier operation errors, separating newly occurring errors from behavior after an error. This is not randomized grouping and does not support causal claims.',
           '', '|Model|Training|Tool position|Reached|Operations correct among reached|Previously all correct|Current correct given previously all correct|',
           '|---|---|---:|---:|---:|---:|---:|']
    for (model,condition,pos),counts in sorted(pooled.items()):
        label='Joint training' if condition=='joint' else 'Operation-only training'
        lines.append(f'|{model}|{label}|{pos}|{counts["reached"]}|{counts["correct"]}|{counts["previous_calls_correct"]}|{counts["correct_given_clean_previous_calls"]}|')
    (R/'OPERATION_ERROR_POSITIONS.md').write_text('\n'.join(lines)+'\n')
    print('Operation position cells:',len(records))


if __name__=='__main__':main()
