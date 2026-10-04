"""Deterministic result digest; requires scientific review, never marks goal complete."""
from common import *
import collections,time,random
D=json.loads((R/'analysis/results.json').read_text());summary=D['summary'];comp=D['comparisons']
labels={'flat':'原STEP','macro':'原名称','position':'位置编号','alias':'固定改名'}
def cell(model,c,group='all'):
 return next(x for x in summary if (x['model'],x['dataset'],x['condition'],x['group'])==(model,'independent',c,group))
lines=['# 位置与身份对照：自动汇总（待最终科学复核）',
'本轮动机是区分进度信息、稳定工具身份及名称形式的作用。旧两组未重训；新两组沿用旧训练与Answer协议。以下为固定512步/旧独立480题的已计算结果，完整反例与原测试见REPORT.md。',
'','|模型|原STEP|原名称|位置编号|固定改名|','|---|---:|---:|---:|---:|']
for model in ROOTS:lines.append('|'+model+'|'+'|'.join(f'{100*cell(model,c)["mean"]["strict_trace"]:.2f}%' for c in labels)+'|')
lines+=['','## 各尺度配对证据','']
for model in ROOTS:
 lines+=['### '+model,'','|比较|平均差pp|三个训练seed差pp|','|---|---:|---|']
 for x in comp:
  if (x['model'],x['dataset'],x['group'])!=(model,'independent','all'):continue
  lines.append('|'+labels[x['a']]+' − '+labels[x['b']]+'|'+f'{100*x["mean_delta"]:+.2f}'+'|'+' / '.join(f'{100*s["delta"]:+.2f}' for s in x['seeds'])+'|')
 lines+=['','这里的正负是观测方向，不能用均值掩盖负向seed，也不能把三seed当成充分的训练随机性覆盖。','']
lines+=['## 解释边界','',
'- 两个新增条件的输出监督token数相同，每轮271656；原名称每轮263858。新标签比旧多约2.96%，不引入填充或更改原配置来掩盖差异。alias输入提示也更长。',
'- 位置step3及以后是未在训练出现的标签组合，尽管数字token本身在数字状态中见过；失败不能单独否定位置信息。',
'- alias与原名称均为输入输出同名，不能直接检验同名vs不同名。若alias较弱，词形区分性、共同tool前缀、分词/预训练表示与学习难度都是合理解释，不能宣称注意力因果机制已证明。',
'- 一个固定映射跨所有seed/规模使用，本轮没有多映射复现。旧测试被使用过，不是全新盲测。',
'- 原严格主指标检查规定操作与答案，不强制标签身份正确；另报标签序列和标签感知完整率，防止悄悄改变旧评分标准。',
'- 本任务顺序已给，不是自主规划或真实Agent中途停止的直接验证；任何应用迁移均尚未测试。',
'','全量49920条主/独立轨迹（新增24960、复用24960）独立评分，数据及源码冻结核验见analysis/completion-audit.json。所有生成失败保留在分母。系统goal槽仍是旧暂停任务，本轮GOAL.json只在最终人工复核和交付后标完成。']
(R/'RESULT_DIGEST.md').write_text('\n'.join(lines)+'\n')
# Fixed random gains AND losses for all new-vs-old comparisons, selected after complete coverage.
rows=[json.loads(l) for l in (R/'analysis/graded.jsonl').read_text().splitlines()];lookup={(x['model'],x['condition'],x['seed'],x['dataset'],str(x['id'])):x for x in rows}
rng=random.Random(2026092603);selected=[];raw_cache={}
for model in ROOTS:
 for c in ['position','alias']:
  for baseline in (['flat','macro','position'] if c=='alias' else ['flat','macro']):
   for kind in ['gain','loss']:
    pool=[]
    for x in rows:
     if (x['model'],x['condition'],x['dataset'])!=(model,c,'independent'):continue
     y=lookup[model,baseline,x['seed'],x['dataset'],str(x['id'])];diff=x['metrics']['strict_trace']-y['metrics']['strict_trace']
     if diff==(1 if kind=='gain' else -1):pool.append((x,y))
    cases=rng.sample(pool,min(3,len(pool)))
    for x,y in cases:
     sources=[]
     for z in [x,y]:
      src=z['source']
      if src not in raw_cache:raw_cache[src]={str(t['id']):t for t in map(json.loads,(B/src).read_text().splitlines())}
      sources.append(dict(source=src,grade=z['metrics'],raw=raw_cache[src][str(z['id'])]))
     selected.append(dict(model=model,new=c,baseline=baseline,change=kind,population=len(pool),seed=x['seed'],id=x['id'],pair=sources))
write(R/'analysis/paired-cases.json',dict(selection='Fixed seed 2026092603, up to three from every gain AND loss stratum; illustrative, not denominator for success rates.',cases=selected))
write(R/'analysis/delivery-assembled.json',dict(time=time.time(),note='Digest and random paired cases assembled; agent must review before completion.'))
print('Digest and paired cases assembled:',len(selected),flush=True)

allocation=json.loads((R/'analysis/dispatch.json').read_text())['results']
assert len(allocation)==24 and all(x['returncode']==0 for x in allocation)
cost=[]
for model in ROOTS:
 rs=[x for x in allocation if x['job']['model']==model]
 cost.append(dict(model=model,jobs=len(rs),allocated_gpu_hours=sum(x['seconds'] for x in rs)/3600))
write(R/'analysis/resource-accounting.json',dict(per_model=cost,total_allocated_gpu_hours=sum(x['allocated_gpu_hours'] for x in cost),note='Sum of whole single-GPU process wall times, including loading, training, in-training evaluation and final evaluations; not kernel-active hours or pure optimization hours. Original baseline training sunk cost excluded.'))
lines=['# 复现与资源口径','', '本轮只使用已有项目训练/分析环境与本机PRO6000。逐run config.json、driver_snapshot.py、train.jsonl、模型适配器和输出均保留在runs。analysis/preflight.json及baseline-freeze.json记录数据/原源码/旧输出哈希，analysis/launch.json记录生成包装器版本；大模型初始adapter与原同seed初始adapter逐文件hash核验。','', '正常运行检查频率一小时一次，进程完成事件自动衔接，不按分钟扫描GPU。失败日志若有会保留，不覆盖重跑。源码调用目标构造函数以外的训练算法沿原文件，具体diff见TRAINER_DIFF.md。','', '|模型|新作业数|单GPU进程墙钟合计小时|','|---|---:|---:|']
for x in cost:lines.append(f'|{x["model"]}|{x["jobs"]}|{x["allocated_gpu_hours"]:.2f}|')
lines+=['',f'合计{sum(x["allocated_gpu_hours"] for x in cost):.2f} GPU小时。含模型加载、训练、开发集/正式推理，不等于GPU内核活跃时间或纯训练时间，不包含旧基准的历史训练成本。',
'', '在项目根目录，完成后可重新做离线评分/统计（会刷新派生报告，不重训或覆盖原始输出）：', '', '```bash','source training-env.sh','python workspace/research/B01-02/label-controls/src/analyze.py','```','',
'新训练使用worker.py --job INDEX，配置来自analysis/jobs.json，调度记录见analysis/dispatch.json。worker拒绝覆盖已有run；需要真正重做时应先建立独立的同层实验目录并保留原始记录，不直接删除现有runs。完整基座与旧控制组依赖原项目路径，本目录不是脱离项目即可独立运行的软件包。']
(R/'REPRODUCTION_AND_COST.md').write_text('\n'.join(lines)+'\n')
