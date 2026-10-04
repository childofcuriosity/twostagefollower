"""Distinguish unseen tool sequences from unseen terminal affine functions."""
import collections,hashlib,json
from common import R,write
from protocol import read,LIB
import dsl

def signature(chain):return dsl.signature(dsl.expand(chain,LIB))

training={signature(row['chain']) for row in read('train')}
prior={signature(row['chain']) for split in ['train','dev','test','independent'] for row in read(split)}
programs=[];summary=[]
for label,path in [('old',R/'data/independent.jsonl'),('fresh',R/'fresh-confirmation/data/independent.jsonl')]:
    rows=list(map(json.loads,path.read_text().splitlines()));chains=sorted({tuple(row['chain']) for row in rows})
    for chain in chains:
        s=signature(chain)
        programs.append(dict(dataset=label,chain=list(chain),length=len(chain),
                             signature_sha256=hashlib.sha256(json.dumps(s).encode()).hexdigest(),
                             equivalent_to_training_function=s in training,
                             equivalent_to_any_prior_function=s in prior,
                             has_adjacent_repeat=any(a==b for a,b in zip(chain,chain[1:]))))
    for length in ['all',3,4,5,6,8]:
        selected=[p for p in programs if p['dataset']==label and (length=='all' or p['length']==length)]
        summary.append(dict(dataset=label,length=length,programs=len(selected),
                            unique_terminal_functions=len({p['signature_sha256'] for p in selected}),
                            training_function_overlap=sum(p['equivalent_to_training_function'] for p in selected),
                            any_prior_function_overlap=sum(p['equivalent_to_any_prior_function'] for p in selected),
                            adjacent_repeat_programs=sum(p['has_adjacent_repeat'] for p in selected)))
write(R/'analysis/dataset-semantics.json',dict(programs=programs,summary=summary,note=(
    'Original extended set was selected for terminal-function novelty; fresh confirmation registration '
    'excludes exact tool sequences, not equivalent terminal functions. The affine signature is exact for this DSL. '
    'All 400 frozen fresh rows remain in primary evaluation; no outcome-based filtering. Old any-prior overlap '
    'includes the old set itself and must not be interpreted as training overlap.')))
old=next(x for x in summary if x['dataset']=='old' and x['length']=='all')
new=next(x for x in summary if x['dataset']=='fresh' and x['length']=='all')
lines=['# 确认集的数据边界',
       '原有480题的生成器按最终仿射函数去重，并排除此前训练/开发/测试函数；本轮新确认集按工具名称序列排重，与登记一致。两种条件不同，不能把“新工具序列”自动叫作“新最终函数”。',
       f'新确认集有100个不同工具序列、400道题，对应{new["unique_terminal_functions"]}个不同最终函数。其中{new["training_function_overlap"]}个序列的最终函数与训练集中的函数等价，{new["any_prior_function_overlap"]}个与本阶段此前任一输入集（含旧独立集）中的函数等价。',
       '这不表示这些长工具序列或完整操作轨迹出现在训练中；本任务严格评分要求全部规定的操作和逐步状态正确，单纯得到相同末状态不够。它限制的是“新函数迁移”这一说法。',
       '主分析保留全部预先冻结的400题，两批题目分别报告。数据不因输出成绩重新挑选。程序级标签及每长度计数见上一级analysis/dataset-semantics.json。',
       '该数据范围核查发生在新确认集部分作业已完成之后，未修改数据、方法或评分。']
(R/'fresh-confirmation/DATASET_SCOPE.md').write_text('\n\n'.join(lines)+'\n')
print('Old profile:',old);print('Fresh profile:',new)
