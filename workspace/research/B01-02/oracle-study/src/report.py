"""Render actual completed/interim oracle results, never invent completion status."""
import collections,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def main():
 audit=json.loads((R/'analysis/results-audit.json').read_text());groups=collections.defaultdict(collections.Counter)
 for x in audit['results']:
  key=(x['model'],x['condition'],x['mode'],x['split'],x['length']);groups[key].update(x['counts'])
 complete_runs=[p.parent.name for p in (R/'runs').glob('*/evaluation-complete.json')]
 lines=['# 第二阶段oracle消融结果\n',f'当前已审计{audit["records"]}条输出；{len(complete_runs)}/36项训练及对应评测有完成标记。完整性验收见COMPLETION_AUDIT.md；若计数尚未达到62400与36，此文件只是中间结果。\n',
 '模型均为Qwen2.5 Base；相同4096训练题、LoRA配置、512步、三个seed。三个条件可见文本相同，只改变loss mask；使用共同EndTool/Done协议。旧宏名称/step结果不能作为唯一同格式对照。\n',
 'joint：模型生成顺序和操作；order_oracle：程序提供正确名称，模型生成操作；operation_oracle：模型选择名称和结束，程序执行其实际选出的工具。程序部分不计预测能力。\n',
 '下表完整任务准确率：展开任务要求所有要求调用展开正确；顺序任务要求完整正确名称并正确结束。joint+oracle是同一个联合训练检查点在对应oracle环境评测，单任务+oracle则是只监督该部分的专用检查点。\n']
 def value(model,cond,mode,split,L):
  c=groups.get((model,cond,mode,split,L));return f'{100*c["complete"]/c["n"]:.2f}% (n={c["n"]})' if c else '待完成'
 for splitprefix in ['iid','ood','pressure','length']:
  for model in ['qwen1.5b','qwen3b','qwen7b','qwen32b']:
   label={'iid':'原测试：同分布短调用','ood':'原测试：未见长组合','pressure':'原测试：压力子集','length':'独立确认'}[splitprefix]
   lines+=['\n## '+model+' / '+label,'|调用数|联合自由执行|联合+顺序oracle|单任务+顺序oracle|联合+操作oracle|单任务+操作oracle|','|---|---:|---:|---:|---:|---:|']
   for L in ([1,2] if splitprefix=='iid' else [3,4,5,6,8] if splitprefix=='length' else [3,4,5]):
    split='length'+str(L) if splitprefix=='length' else splitprefix
    vals=[value(model,c,m,split,L) for c,m in [('joint','joint'),('joint','order_oracle'),('order_oracle','order_oracle'),('joint','operation_oracle'),('operation_oracle','operation_oracle')]]
    lines.append('| '+str(L)+' | '+' | '.join(vals)+' |')
 lines+=['\n## 边界与复现\n','不把oracle帮助后的能力等同于自主能力；不根据正结果选seed/题目；片段EOS/格式失败保留。不同条件监督token量不同，文件中分别记录。原自然输出的B仅覆盖实际输出调用，本次正确顺序oracle覆盖全部要求调用。','\n原始逐题轨迹见runs/各运行/evaluation-*.jsonl，包含所有人工/模型片段及token ID；独立重算见analysis/results-audit.json。环境、模型及输入哈希见infrastructure/与analysis/reproducibility-inputs.json，任务配置与源码冻结见analysis/formal-source-freeze.json。']
 (R/'REPORT.md').write_text('\n'.join(lines));print('Report updated from',audit['records'],'audited trajectories')
if __name__=='__main__':main()
