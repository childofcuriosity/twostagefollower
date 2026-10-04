"""All completed curve/compose trajectories, grouped without checkpoint selection."""
import collections,json,hashlib,math
from common import *
from protocol import LIB

def first_error(row):
    for i,c in enumerate(row['calls']):
        if i>=len(row['chain']) or c['tool']!=row['chain'][i]:return 'wrong_name',i+1
        b=c.get('body',{})
        if not b.get('correct',False):
            ops=b.get('ops');truth=LIB[c['tool']]
            if ops is None:return 'unparsed_body',i+1
            if ops!=truth:return ('early_EndTool' if len(ops)<len(truth) and ops==truth[:len(ops)] else 'wrong_ops'),i+1
            return 'numeric_error',i+1
    if len(row['calls'])<len(row['chain']):return 'early_Done_or_stop',len(row['calls'])+1
    return row['stop'],len(row['calls'])

def main():
    out=[];sources=[];training=[]
    for p in sorted((R/'runs').glob('*/complete.json')):
        d=json.loads(p.read_text());j=d['job']
        if j['kind']=='control':continue
        for e in d['summary']:
            src=Path(e['source']);records=list(map(json.loads,src.read_text().splitlines()));assert len(records)==e['n']
            groups=collections.defaultdict(collections.Counter)
            for row in records:
                c=groups[row['split'],len(row['chain'])];c['n']+=1
                for key in ['complete','sequence_correct','all_expansions_correct','requested','emitted','local_correct']:c[key]+=row['grade'][key]
                c['model_tokens']+=row['generated_tokens'];c['stop:'+row['stop']]+=1
                if not row['grade']['complete']:
                    label,pos=first_error(row);c['first_error:'+label]+=1;c['first_error_position:'+str(pos)]+=1
            for (split,L),c in groups.items():out.append(dict(model=j['model'],seed=j['seed'],kind=j['kind'],condition=j.get('condition'),step=e['step'],mode=e['mode'],split=split,length=L,counts=dict(c)))
            sources.append(dict(job=j['id'],step=e['step'],mode=e['mode'],split=e['split'],source=str(src),reuse=e['reuse'],n=len(records),sha256=hashlib.sha256(src.read_bytes()).hexdigest()))
    for model in ['qwen3b','qwen32b']:
        for condition in ['joint','order_oracle','operation_oracle']:
            for seed in [11,22,33]:
                log=list(map(json.loads,(O/'runs'/f'{model}-{condition}-s{seed}'/'train.jsonl').read_text().splitlines()))
                for step in [64,128,256,512]:
                    z=log[max(0,step-32):step];training.append(dict(model=model,condition=condition,seed=seed,step=step,mean_previous32_loss=sum(x['loss'] for x in z)/len(z),last_loss=z[-1]['loss']))
    write(R/'analysis/results.json',dict(results=out,sources=sources,training=training,covered=sum(x['n'] for x in sources),new=sum(x['n'] for x in sources if not x['reuse'])))
    lines=['# 检查点与实际组合结果','只展示已完成作业，未完成矩阵不能作为goal完成。原始输出与模式/检查点映射见analysis/results.json。名称：J=一起训练，S=只训练顺序，E=只训练操作；SE表示实际由S写名称、E写操作，没有程序正确答案。']
    groups=collections.defaultdict(collections.Counter)
    for x in out:groups[x['model'],x['kind'],x['condition'],x['step'],x['mode'],x['split'],x['length']].update(x['counts'])
    def val(model,kind,cond,step,mode,split,L):
        c=groups.get((model,kind,cond,step,mode,split,L));return f'{100*c["complete"]/c["n"]:.2f}% (n={c["n"]})' if c else '待完成'
    for model in ['qwen3b','qwen32b']:
        lines+=['\n## '+model+'：完整执行','|步数|工具数|一起训练 J/J|只替换顺序 S/J|只替换操作 J/E|两项都专用 S/E|','|---|---:|---:|---:|---:|---:|']
        for st in [64,128,256,512]:
            for L in [3,4,5,6,8]:
                v=[val(model,'curve','joint',st,'joint','length'+str(L),L)]+[val(model,'compose',None,st,m,'length'+str(L),L) if st in [256,512] else '未安排' for m in ['SJ','JE','SE']]
                lines.append(f'|{st}|{L}|'+'|'.join(v)+'|')
        lines+=['\n### 子任务和短题曲线','|步数|测试|J自主|J测操作|E测操作|J测顺序|S测顺序|','|---|---|---:|---:|---:|---:|---:|']
        for st in [64,128,256,512]:
            for split,L in [('dev',1),('dev',2)]+[('length'+str(x),x) for x in [3,4,5,6,8]]:
                v=[val(model,'curve',c,st,m,split,L) for c,m in [('joint','joint'),('joint','order_oracle'),('order_oracle','order_oracle'),('joint','operation_oracle'),('operation_oracle','operation_oracle')]]
                lines.append(f'|{st}|{split}/{L}|'+'|'.join(v)+'|')
    (R/'REPORT.md').write_text('\n'.join(lines)+'\n');print('Analyzed covered/new:',sum(x['n'] for x in sources),sum(x['n'] for x in sources if not x['reuse']))
if __name__=='__main__':main()
