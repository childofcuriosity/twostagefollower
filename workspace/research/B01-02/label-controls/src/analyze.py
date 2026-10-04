from common import *
from grading import grade
import collections,time,numpy as np
jobs=json.loads((R/'analysis/jobs.json').read_text());pre=json.loads((R/'analysis/preflight.json').read_text())

launch=json.loads((R/'analysis/launch.json').read_text())
for f,h in launch['generation_sources_sha256'].items():assert sha(R/f)==h,('Generation code changed',f)
assert sha(R/'REGISTRATION.md')==launch['registration_sha256']
assert sha(R/'src/grading.py')==launch['sources']['src/grading.py'], 'Scoring implementation changed since launch'
for p,h in pre['frozen_source_data_hashes'].items():assert sha(B/p)==h,('Source/data mutated',p)
for p,h in json.loads((R/'analysis/baseline-freeze.json').read_text())['files'].items():assert sha(B/p)==h,('Baseline mutated',p)
records=[];hashes={};training=[]
for model,root in ROOTS.items():
 for condition in ['flat','macro','position','alias']:
  for seed in [11,22,33]:
   if condition in ['flat','macro']:
    paths={'main':root/f'runs/{condition}-original-s{seed}/predictions.jsonl','independent':S/f'extended/{model}/{condition}-s{seed}.jsonl'}
   else:
    base=R/f'runs/{model}-{condition}-s{seed}';done=json.loads((base/'complete.json').read_text());legacy=Path(done['legacy_output'])
    assert (base/'driver_snapshot.py').read_text()==code(model), 'Training driver differs from prescribed legacy wrapper'
    paths={'main':legacy/'predictions.jsonl','independent':base/'independent.jsonl'}
    log=[json.loads(l) for l in (legacy/'train.jsonl').read_text().splitlines()];assert len(log)==512 and log[-1]['examples']==16384
    assert all(np.isfinite(x['loss']) and np.isfinite(x['grad_norm']) for x in log)

    cfg=json.loads((legacy/'config.json').read_text());old=json.loads((root/f'runs/macro-original-s{seed}/config.json').read_text())
    for k in ['torch','cuda','gpu','model_revision','trainable_parameters','total_parameters']:assert cfg[k]==old[k],(model,condition,seed,k)
    for k in ['steps','microbatch','accum','seed','world']:assert cfg['args'][k]==old['args'][k],(model,condition,seed,k)
    assert cfg['training']['counts']['target_tokens']==271656*4

    if model in ['qwen7b','qwen32b']:
     old_initial=root/f'runs/macro-original-s{seed}/checkpoints/step0000/adapter/adapter_model.safetensors'
     new_initial=legacy/'checkpoints/step0000/adapter/adapter_model.safetensors'
     assert sha(old_initial)==sha(new_initial),('Initial adapter mismatch',model,condition,seed)
    training.append(dict(model=model,condition=condition,seed=seed,steps=512,examples=16384,target_tokens=log[-1]['target_tokens'],first_loss=log[0]['loss'],last_loss=log[-1]['loss'],seconds=done['seconds'],trainable_parameters=done['summary']['trainable_parameters']))
   for dataset,path in paths.items():
    raw=[json.loads(l) for l in path.read_text().splitlines()];assert len(raw)==(560 if dataset=='main' else 480)
    ref=[json.loads(l) for l in ((root/'data/test.jsonl') if dataset=='main' else S/'data/extended-test.jsonl').read_text().splitlines()]
    assert [(r['id'],r['x'],r['chain']) for r in raw]==[(r['id'],r['x'],r['chain']) for r in ref]
    hashes[str(path.relative_to(B))]=sha(path)
    for row in raw:
     g=grade(row,condition)
     records.append(dict(model=model,condition=condition,seed=seed,dataset=dataset,source=str(path.relative_to(B)),id=row['id'],split=row['split'],length=len(row['chain']),chain=row['chain'],x=row['x'],metrics=g))
assert len(records)==49920
(R/'analysis/graded.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in records))
metrics=['strict_trace','accuracy','label_sequence_correct','all_emitted_segments_correct','label_aware_complete','correct_prefix_early_answer','exact_two_tools_early_answer','internal_short_any','numeric_step_error','budget_hit']
summary=[];lookup=collections.defaultdict(list)
for row in records:lookup[row['model'],row['condition'],row['seed'],row['dataset']].append(row)
def select(rows,dataset,group):
 if group=='all':return rows
 if isinstance(group,int):return [x for x in rows if x['length']==group]
 return [x for x in rows if x['split']==group]
for model in ROOTS:
 for dataset in ['main','independent']:
  groups=(['all']+sorted({x['split'] for x in lookup[model,'flat',11,dataset]})) if dataset=='main' else ['all',3,4,5,6,8]
  for condition in ['flat','macro','position','alias']:
   for group in groups:
    seeds=[]
    for seed in [11,22,33]:
     rs=select(lookup[model,condition,seed,dataset],dataset,group);assert rs
     counts={m:sum(x['metrics'][m] for x in rs) for m in metrics}
     seeds.append(dict(seed=seed,n=len(rs),counts=counts,rates={k:v/len(rs) for k,v in counts.items()}))
    summary.append(dict(model=model,dataset=dataset,condition=condition,group=group,seeds=seeds,mean={m:sum(x['rates'][m] for x in seeds)/3 for m in metrics}))
comparisons=[];rng=np.random.default_rng(2026092602)
for model in ROOTS:
 for dataset in ['main','independent']:
  groups=sorted({x['split'] for x in lookup[model,'flat',11,dataset]}) if dataset=='main' else ['all',3,4,5,6,8]
  for group in groups:
   for a,b in [('position','flat'),('alias','flat'),('position','macro'),('alias','macro'),('alias','position')]:
    seeds=[];programs=collections.defaultdict(lambda:[0,0])
    for seed in [11,22,33]:
     ar=select(lookup[model,a,seed,dataset],dataset,group);br=select(lookup[model,b,seed,dataset],dataset,group)
     assert [x['id'] for x in ar]==[x['id'] for x in br]
     ac=sum(x['metrics']['strict_trace'] for x in ar);bc=sum(x['metrics']['strict_trace'] for x in br)
     gain=loss=0
     for x,y in zip(ar,br):
      d=x['metrics']['strict_trace']-y['metrics']['strict_trace'];key=tuple(x['chain']);programs[key][0]+=d;programs[key][1]+=1;gain+=d==1;loss+=d==-1
     seeds.append(dict(seed=seed,n=len(ar),a_correct=ac,b_correct=bc,delta=(ac-bc)/len(ar),gain=gain,loss=loss))
    v=np.array(list(programs.values()),dtype=float);idx=rng.integers(0,len(v),(3000,len(v)));vv=v[idx].sum(axis=1);boot=vv[:,0]/vv[:,1]
    comparisons.append(dict(model=model,dataset=dataset,group=group,a=a,b=b,seeds=seeds,mean_delta=sum(s['delta'] for s in seeds)/3,conditional_program_bootstrap95=np.quantile(boot,[.025,.975]).tolist(),programs=len(v)))
write(R/'analysis/results.json',dict(summary=summary,comparisons=comparisons,notes='Original strict trajectory endpoint preserved; labels separately graded. Bootstrap resamples programs holding the three trained seeds fixed, not a seed-population guarantee. Existing datasets reused, no new blind test.'))
write(R/'analysis/completion-audit.json',dict(complete=True,formal_records=len(records),new_formal_records=24960,reused_records=24960,new_training_jobs=len(training),source_sha256=hashes,training=training,source_data_frozen=True,legacy_scoring_equivalent=True))
labels={'flat':'原STEP','macro':'原名称','position':'新增位置编号','alias':'新增固定改名'}
lines=['# 标签对照完整结果','全部新训练固定512步。四尺度×三seed×两新增条件=24训练，原两条件只读复用。主要评分沿原指定操作/每步数字/最终Answer正确，标签序列单列，不把新增标签身份要求混入旧主指标。','', '## 旧独立480题：完整轨迹成功','', '|模型|工具数|原STEP|原名称|位置编号|固定改名|','|---|---|---:|---:|---:|---:|']
for model in ROOTS:
 for group in ['all',3,4,5,6,8]:
  vals=[next(x for x in summary if (x['model'],x['dataset'],x['condition'],x['group'])==(model,'independent',c,group))['mean']['strict_trace'] for c in labels]
  lines.append('|'+model+'|'+str(group)+'|'+'|'.join(f'{v*100:.2f}%' for v in vals)+'|')
lines+=['','## 所有原测试子集与子任务指标','','“已输出段操作全对”按该段在要求列表中的位置核对操作，不假设STEP具有身份；漏段由标签序列/完整轨迹指标体现。它不是oracle全部要求操作能力。内部提前结束指已输出段是该位置要求操作的非空正确短前缀，是行为描述非因果归因。','','|模型|集合|子集/长度|条件|完整轨迹|最终答案|标签序列|已输出段操作全对|正确前缀早答|内部短段|','|---|---|---|---|---:|---:|---:|---:|---:|---:|']
for x in summary:
 m=x['mean'];lines.append('|'+ '|'.join([x['model'],x['dataset'],str(x['group']),labels[x['condition']]]+[f'{m[k]*100:.2f}%' for k in ['strict_trace','accuracy','label_sequence_correct','all_emitted_segments_correct','correct_prefix_early_answer','internal_short_any']])+'|')
lines+=['','## 配对比较：不隐藏负向seed','','|模型|集合|子集/长度|新增/对照|平均差pp|三seed差pp|程序bootstrap95%pp|','|---|---|---|---|---:|---|---|']
for x in comparisons:
 lo,hi=x['conditional_program_bootstrap95'];lines.append('|'+ '|'.join([x['model'],x['dataset'],str(x['group']),labels[x['a']]+' − '+labels[x['b']],f'{100*x["mean_delta"]:+.2f}',' / '.join(f'{100*s["delta"]:+.2f}' for s in x['seeds']),f'[{100*lo:+.2f}, {100*hi:+.2f}]'])+'|')
lines+=['','总样本49,920含新24,960与复用24,960，不是独立题目数。Bootstrap未校正多重比较，不能替代更多训练seed。主矩阵与所有seed完成不等于具体机制已证实。','运行成本与完整训练日志在analysis/completion-audit.json及各run；最终科学判断由人工复核后写CONCLUSIONS.md。']
(R/'REPORT.md').write_text('\n'.join(lines)+'\n');print('Analysis complete',len(records),'rows,',len(comparisons),'paired comparisons',flush=True)

import subprocess,sys
subprocess.run([sys.executable,str(R/"src/delivery.py")],check=True)
plot_python=B.parents[2]/".analysis-venv/bin/python"
subprocess.run([str(plot_python),str(R/"src/plots.py")],check=True)

subprocess.run([sys.executable,str(R/"src/boundary_diagnostics.py")],check=True)

subprocess.run([sys.executable,str(R/"src/auxiliary.py")],check=True)
