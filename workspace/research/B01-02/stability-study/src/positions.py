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
    lines=['# 正确名称已给定时，操作错误出现在什么位置',
           '这是诊断测试，不能当作无帮助的实际执行。即使名称正确，操作仍可能写错；当前状态始终来自实际生成，程序不修正。',
           '“此前全对”只统计到达该位置且前面没有操作错误的题，用于区分新发生错误与已经出错之后的表现。它不是随机分组，不能据此声称因果。',
           '', '|模型|训练方式|第几个工具|到达数|其中操作正确|此前全对数|此前全对时本次正确|',
           '|---|---|---:|---:|---:|---:|---:|']
    for (model,condition,pos),counts in sorted(pooled.items()):
        label='一起训练' if condition=='joint' else '只训练操作'
        lines.append(f'|{model}|{label}|{pos}|{counts["reached"]}|{counts["correct"]}|{counts["previous_calls_correct"]}|{counts["correct_given_clean_previous_calls"]}|')
    (R/'OPERATION_ERROR_POSITIONS.md').write_text('\n'.join(lines)+'\n')
    print('Operation position cells:',len(records))


if __name__=='__main__':main()
