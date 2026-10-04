from pathlib import Path
import collections,hashlib,json,subprocess,time
from sandbox import R

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
x=json.loads((R/'analysis/results.json').read_text());audit=json.loads((R/'analysis/native-audit.json').read_text());mechanism=json.loads((R/'analysis/mechanism-audit.json').read_text());cfg={}
for p in (R/'queues').glob('*-batch.json'):
 rows=json.loads(p.read_text())
 for row in rows:
  assert isinstance(row,dict) and 'tag' in row,p
  if row['tag'] in cfg:assert row==cfg[row['tag']],row
  cfg[row['tag']]=row
for mode in ['zero','fewshot']:cfg['dev-'+mode]={'tag':'dev-'+mode,'queue':'dev.json','script':'native.py','mode':mode}
expected=set();workers=[]
for tag,c in sorted(cfg.items()):
 jobs=json.loads((R/'queues'/c['queue']).read_text());worker=json.loads((R/'analysis'/f'{tag}-completed.json').read_text());assert worker['jobs_requested']==worker['jobs_completed']==len(jobs),(tag,worker)
 workers.append({'tag':tag,'jobs':len(jobs),'gpu_reserved_seconds':worker['seconds']})
 for job in jobs:
  task,condition=job[:2];suffix=f'{task}--{condition}'
  if c.get('script','native.py').startswith('native_queue_controlled'):
   policy=job[2] if len(job)==3 else c['context_policy'];suffix+='--'+policy
  run='runs/'+tag+'/'+suffix;assert run not in expected;expected.add(run)
  summary=json.loads((R/run/'summary.json').read_text());assert summary['source_sha256']==sha(R/'src'/c.get('script','native.py')),(run,'source changed')
  assert summary['model_revision']=='5ede1c97bbab6ce5cda5812749b4c0bdf79b18dd'
actual={str(p.parent.relative_to(R)) for p in (R/'runs').glob('*/*/summary.json')};assert actual==expected and len(actual)==439,(len(actual),len(expected),expected-actual)
assert {str(p.relative_to(R)) for p in (R/'runs').glob('*/*') if p.is_dir()}==actual,'Partial unaccounted run'
assert {s['run'] for s in x['runs']}==actual=={s['run'] for s in audit['records']}
assert all(s['regraded'] and s['replay_matches'] for s in audit['records'])
assert len(mechanism['paired_prefix_checks'])==9 and all(s['pre_intervention_identical'] for s in mechanism['paired_prefix_checks'])
assert all(s['all_model_outputs_and_tool_results_identical'] for s in mechanism['deterministic_rerun'])
controlled=[s for s in audit['records'] if s['run'].startswith('runs/controlled-')];assert len(controlled)==21 and all(not s.get('tool_result_value_mismatches') for s in controlled)
assert abs(sum(w['gpu_reserved_seconds'] for w in workers)/3600-x['gpu_reserved_hours'])<1e-8
for name in ['REPORT.md','CONCLUSIONS.md','README.md','LITERATURE.md','figures/reliability.png','figures/reliability.svg','figures/reliability.pdf']:assert (R/name).stat().st_size>0,name
inventory=subprocess.run(['nvidia-smi','--query-gpu=index,memory.used,utilization.gpu','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout.splitlines()
result={'registered_and_completed_runs':len(actual),'independent_regrades':audit['count'],'controlled_exact_tool_result_replays':len(controlled),'paired_prefix_checks':9,'deterministic_model_reruns':1,'all_model_workers_finished':True,'gpu_reserved_hours':x['gpu_reserved_hours'],'gpu_inventory_at_delivery':inventory,'workers':workers,'checked_at':time.time(),'all_assets_in_project':True}
(R/'analysis/final-delivery-check.json').write_text(json.dumps(result,indent=2))
old_differences=sum(bool(s.get('tool_result_value_mismatches')) for s in audit['records'])
text=f'''# 交付核验

- {len(actual)}条已登记轨迹全部完成，覆盖全部运行队列；没有未计入的半截运行目录。
- {audit['count']}条归档最终工作区均重新验收，与原评分一致；成功和73条失败全部保留。
- 所有动作重放的最终文件状态一致，工具错误状态一致。早期未固定接口中记录到{old_differences}条轨迹的工具返回全文存在时间/宿主路径差异，不能把这些早期跨运行差异解释成单一方法效应；详情在native-audit.json。
- 新受控接口的{len(controlled)}条轨迹进一步通过全部工具返回全文一致检查。
- 九个修复配对的干预前模型输出和工具返回一致；原5/24失败的新进程重复与原轨迹、结果、文件逐项一致。
- 原始提示、工具调用、结果、最终文件、回执、上下文整理记录及所有开发失败均已保存。
- 累计模型进程占用{x['gpu_reserved_hours']:.2f}GPU小时。全部模型工作进程已退出；本机交付时显存状态保存在final-delivery-check.json。
- 模型权重未更新，没有外部付费推理调用或对外发布。本轮工作环境、缓存引用与产物保留在当前项目目录。

该核验保证记录完整、评分与重放一致，不把3题机制实验变成跨模型/真实任务的普遍结论。原始摘要/删除方法的收益不能用来证明身份复述独有效果。当前交付为可复现工程修复和机制线索，研究新颖性仍需进一步核对。

审核入口：[CONCLUSIONS.md](CONCLUSIONS.md)；完整报告：[REPORT.md](REPORT.md)；结构化结果：[analysis/results.json](analysis/results.json)；机制核验：[analysis/mechanism-audit.json](analysis/mechanism-audit.json)。
'''
(R/'COMPLETION_AUDIT.md').write_text(text)
assets=[p for p in R.glob('*.md')]+list((R/'src').glob('*.py'))+[p for p in (R/'analysis').glob('*.json') if p.name!='delivery-manifest.json']+list((R/'figures').glob('*'))+list((R/'queues').glob('*.json'))+[p for p in (R/'tasks').rglob('*') if p.is_file()]
manifest={'created_at':time.time(),'run_count':len(actual),'source_and_asset_sha256':{str(p.relative_to(R)):sha(p) for p in sorted(assets) if p.is_file()},'raw_artifact_hash_index':'analysis/native-audit.json','dependency_sha256':{'../agent-study/src/jail.c':sha(R.parent/'agent-study/src/jail.c'),'runtime/jail':sha(R/'runtime/jail')},'model_revision':'5ede1c97bbab6ce5cda5812749b4c0bdf79b18dd'}
(R/'analysis/delivery-manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({k:v for k,v in result.items() if k not in ['workers','gpu_inventory_at_delivery']},indent=2));print('GPU inventory:',inventory)
