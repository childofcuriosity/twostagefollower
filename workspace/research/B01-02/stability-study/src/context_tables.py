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
labels={'JJ':'Joint / joint','SJ':'Sequence specialist / joint','JE':'Joint / operation specialist','SE':'Sequence specialist / operation specialist'}
lines=['# Context controls: two subtasks in actual outputs',
       'Every column comes from the same actual execution without correct-answer assistance. Correct sequence requires all names in order and correct termination. All generated operations correct requires correct expansion of every emitted call; missing calls fail the sequence column.',
       'This differs from oracle tests where a program supplies the correct other component; see ORACLE_PREDICTION_CHECK.md. Products below are computed by seed before averaging and do not prove internal independence.',
       'Three seeds per condition;480 earlier examples per seed and 400 new-program examples per seed. Repeating the same examples across seeds/conditions does not create that many independent programs.']
for directory,title in [('context-intervention','Existing program set'),('fresh-confirmation','Preregistered frozen new program set')]:
    lines += ['', '## '+title, '', '|Model|Name writer / operation writer|Operation context|Tools|Correct sequence|All generated operations correct|Product of both columns|Full-task success|',
              '|---|---|---|---|---:|---:|---:|---:|']
    for length in ['all',3,4,5,6,8]:
        for row in records:
            if row['dataset']!=directory or row['length']!=length:continue
            m=row['mean'];values='|'.join(f'{100*m[k]:.2f}%' for k in ['sequence','all_emitted_operations','product','complete'])
            scope='Full history' if row['context']=='full' else 'Current tool + actual state'
            lines.append(f'|{row["model"]}|{labels[row["route"]]}|{scope}|{length}|{values}|')
(R/'CONTEXT_SUBTASKS.md').write_text('\n'.join(lines)+'\n');print('Context subtask table cells:',len(records))
