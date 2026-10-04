"""Expose both subtask columns for all model sizes and task lengths."""
import json
from common import R,write

records=[]
for directory,key in [('context-intervention','metrics'),('fresh-confirmation','scores')]:
    data=json.loads((R/directory/'analysis/comparisons.json').read_text())['records']
    for row in data:
        if row['a_route']!=row['b_route'] or row['a_context']!='local' or row['b_context']!='full':continue
        for scope,column in [('full','b'),('local','a')]:
            seeds=[]
            for s in row['seeds']:
                a=s[key]['sequence_correct'][column];b=s[key]['all_expansions_correct'][column]
                seeds.append(dict(seed=s['seed'],n=s['n'],sequence=a,all_emitted_operations=b,
                                  product=a*b,complete=s[key]['complete'][column]))
            records.append(dict(dataset=directory,model=row['model'],route=row['a_route'],context=scope,length=row['length'],seeds=seeds,
                                mean={k:sum(s[k] for s in seeds)/3 for k in ['sequence','all_emitted_operations','product','complete']}))
assert len(records)==144,len(records)
write(R/'analysis/context-subtasks.json',dict(records=records,note='These two columns are measured on actual no-oracle trajectories, not correct-other-component tests. Missing calls fail sequence; all-emitted-operations does not count ungenerated calls as additional body errors. Products are calculated within seed before averaging.'))
labels={'JJ':'一起训练 / 一起训练','SJ':'只训顺序 / 一起训练','JE':'一起训练 / 只训操作','SE':'只训顺序 / 只训操作'}
lines=['# 上下文对照：实际输出中的两个子任务',
       '所有列都来自同一次无正确答案帮助的真实执行。顺序正确指完整名称顺序及结束正确；操作全对指全部实际生成调用都正确展开，未生成调用由顺序列判错。',
       '这与“程序给正确另一部分”的oracle测试口径不同，后者见ORACLE_PREDICTION_CHECK.md。下面的乘积先按seed计算再平均；不能用它证明内部独立。',
       '每条件三个seed；旧题每seed480题、新程序每seed400题。相同题在不同seed/条件重复执行，不能视作同样数量的独立程序。']
for directory,title in [('context-intervention','已有程序集'),('fresh-confirmation','预先冻结的新程序集')]:
    lines += ['', '## '+title, '', '|模型|谁写名称 / 谁写操作|操作上下文|工具数|顺序正确|已生成操作全对|两列乘积|整题成功|',
              '|---|---|---|---|---:|---:|---:|---:|']
    for length in ['all',3,4,5,6,8]:
        for row in records:
            if row['dataset']!=directory or row['length']!=length:continue
            m=row['mean'];values='|'.join(f'{100*m[k]:.2f}%' for k in ['sequence','all_emitted_operations','product','complete'])
            scope='完整历史' if row['context']=='full' else '当前工具＋实际状态'
            lines.append(f'|{row["model"]}|{labels[row["route"]]}|{scope}|{length}|{values}|')
(R/'CONTEXT_SUBTASKS.md').write_text('\n'.join(lines)+'\n');print('Context subtask table cells:',len(records))
