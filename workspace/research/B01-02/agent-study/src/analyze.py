from pathlib import Path
import collections,hashlib,json,statistics
R=Path(__file__).resolve().parents[1];manifest=json.loads((R/'analysis/task-manifest.json').read_text());lookup={};hashes={}
for p in sorted((R/'runs').glob('main-*/*/summary.json')):
 x=json.loads(p.read_text());key=(x['task'],x['condition']);assert key not in lookup;lookup[key]=x
 for source in [p,p.parent/'trajectory.jsonl',p.parent/'messages.json']:hashes[str(source.relative_to(R))]=hashlib.sha256(source.read_bytes()).hexdigest()
missing=[(t,c) for t in manifest['main_ids'] for c in ['plan','reminder','identity','todo'] if (t,c) not in lookup]
summaries=[]
for family in ['all','files','data','code']:
 for length in ['all',4,12]:
  for c in ['plan','reminder','identity','todo']:
   rs=[x for x in lookup.values() if x['condition']==c and (family=='all' or x['family']==family) and (length=='all' or x['n_requirements']==length)]
   if not rs:continue
   summaries.append(dict(family=family,length=length,condition=c,n=len(rs),complete_rate=statistics.mean(x['grade']['complete'] for x in rs),premature_finish_rate=statistics.mean(x['category']=='incomplete_voluntary_finish' for x in rs),requirement_fraction=statistics.mean(x['grade']['completed_requirements']/x['grade']['total_requirements'] for x in rs),mean_generated_tokens=statistics.mean(x['generated_tokens'] for x in rs),mean_input_tokens=statistics.mean(x['input_tokens'] for x in rs),mean_turns=statistics.mean(x['turns'] for x in rs),mean_wall_seconds=statistics.mean(x['wall_seconds'] for x in rs),categories=dict(collections.Counter(x['category'] for x in rs))))
casefile=R/'analysis/cases.jsonl';casefile.write_text(''.join(json.dumps(x)+'\n' for x in lookup.values()))
paired=[]
for control in ['plan','reminder','todo']:
 pairs=[(lookup[(t,'identity')],lookup[(t,control)]) for t in manifest['main_ids'] if (t,'identity') in lookup and (t,control) in lookup]
 paired.append(dict(control=control,n=len(pairs),identity_only_complete=sum(a['grade']['complete'] and not b['grade']['complete'] for a,b in pairs),control_only_complete=sum(b['grade']['complete'] and not a['grade']['complete'] for a,b in pairs),both_complete=sum(a['grade']['complete'] and b['grade']['complete'] for a,b in pairs)))
result=dict(records=len(lookup),missing=missing,summary=summaries,paired=paired,source_sha256=hashes,note='Development smoke, three task-generator families; no confirmatory significance claim. Greedy trajectories are not repeated decoding seeds. Tool returns are user-role messages in a custom JSON action harness, not a production agent SDK.')
(R/'analysis/results.json').write_text(json.dumps(result,indent=2));print('Analyzed',len(lookup),'trajectories; missing',len(missing),flush=True)
lines=['# 真实文件/数据/代码Agent冒烟结果','',f'已完成 {len(lookup)}/96 条主轨迹。这是开发冒烟，不是确认性实验。','', '| 条件 | 完成率 | 未完成主动结束 | 平均输出token | 平均工具/结束轮次 |','|---|---:|---:|---:|---:|']
for x in summaries:
 if x['family']=='all' and x['length']=='all':lines.append(f"| {x['condition']} | {100*x['complete_rate']:.1f}% | {100*x['premature_finish_rate']:.1f}% | {x['mean_generated_tokens']:.0f} | {x['mean_turns']:.1f} |")
lines += ['','各任务家族、长度、配对差及原始路径见analysis/results.json，所有逐题判定见analysis/cases.jsonl。结论须经原始轨迹审计后填写，不自动把名称条件的任何差异归因于注意力或记忆机制。']
(R/'REPORT.md').write_text('\n'.join(lines)+'\n')
# These audits execute only after all registered jobs exist; failures remain visible.
if not missing:
 import subprocess,sys
 subprocess.run([sys.executable,str(R/'src/audit.py')],check=True)
 subprocess.run([sys.executable,str(R/'src/replay.py')],check=True)
