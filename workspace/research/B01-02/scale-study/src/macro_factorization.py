"""Offline whole-macro success and adjacent dependence, preserving missingness."""
import json,collections,hashlib,math
from pathlib import Path
R=Path(__file__).resolve().parents[1]
rows=[json.loads(l) for l in (R/'analysis/subtask-factorization-segments.jsonl').read_text().splitlines()]
old=json.loads((R/'analysis/subtask-factorization.json').read_text())
pred=[]
for family,model,seed,L in sorted({(r['family'],r['model'],r['seed'],r['length']) for r in rows}):
 rs=[r for r in rows if (r['family'],r['model'],r['seed'],r['length'])==(family,model,seed,L)]
 for f in range(5):
  tr=[s for r in rs if r['fold']!=f for s in r['slots']]
  p=sum(s['J'] for s in tr)/len(tr)
  for r in rs:
   if r['fold']==f:pred.append(dict(family=family,model=model,seed=seed,length=L,id=r['id'],prediction=p**L,actual=r['decomposed_success']))
summary=[]
for family,model,L in sorted({(r['family'],r['model'],r['length']) for r in rows}):
 rs=[r for r in rows if (r['family'],r['model'],r['length'])==(family,model,L)];slots=[s for r in rs for s in r['slots']];ps=[r for r in pred if (r['family'],r['model'],r['length'])==(family,model,L)]
 c=collections.Counter();bypos=collections.defaultdict(collections.Counter)
 for r in rs:
  for i,s in enumerate(r['slots']):
   present=i<len(r['segments']);c['present']+=present;c['missing']+=not present
   if i==0:continue
   prev=r['slots'][i-1];prevpresent=i-1<len(r['segments'])
   group='prev_ok' if prev['J'] else 'prev_bad'
   c[group+'_all_n']+=1;c[group+'_all_current_bad']+=not s['J']
   if prevpresent:
    c[group+'_prevpresent_n']+=1;c[group+'_next_missing']+=not present
   if present and prevpresent:
    c[group+'_present_n']+=1;c[group+'_present_current_bad']+=not s['J']
    bypos[i][group+'_n']+=1;bypos[i][group+'_bad']+=not s['J']
 # Direct standardization to positions with both predecessor outcomes, descriptive only.
 common=[]
 for i,cc in bypos.items():
  if cc['prev_ok_n'] and cc['prev_bad_n']:
   common.append((cc['prev_ok_n']+cc['prev_bad_n'],cc['prev_ok_bad']/cc['prev_ok_n'],cc['prev_bad_bad']/cc['prev_bad_n']))
 std=None
 if common:
  n=sum(x[0] for x in common);std={'positions':len(common),'after_ok':sum(w*a for w,a,b in common)/n,'after_bad':sum(w*b for w,a,b in common)/n}
 z=next(z for z in old['aggregate'] if (z['family'],z['model'],z['length'])==(family,model,L))
 summary.append(dict(family=family,model=model,length=L,n=len(rs),macro_correct=sum(s['J'] for s in slots),macro_total=len(slots),macro_accuracy=sum(s['J'] for s in slots)/len(slots),macro_product=sum(p['prediction'] for p in ps)/len(ps),separate_AB_product=z['pooled_product'],actual=z['actual'],flat=z['flat_strict'],counts=dict(c),position_standardized=std))
out={'definition':'Whole macro J: correct name at required position AND complete correct expansion of that emitted name with locally valid arithmetic. Missing=incorrect. Prediction per model/seed/length: p(J)^L estimated on other four program folds. Conditional adjacency restricted to both segments actually emitted excludes missing-tail failures. Correlation descriptive, no causal mimicry claim; difficult programs and positions can confound. Position standardized rates use overlap positions only, still not program/seed adjusted.','source_sha256':hashlib.sha256((R/'analysis/subtask-factorization-segments.jsonl').read_bytes()).hexdigest(),'summary':summary}
(R/'analysis/macro-factorization.json').write_text(json.dumps(out,indent=2))
(R/'analysis/macro-factorization-predictions.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in pred))
lines=['# Macro整体粒度的已有轨迹统计\n',out['definition'],'\n独立确认集：每行288条轨迹，来自24程序×4输入×3seed。所有预测为按程序分组的交叉预测。\n']
for model in ['qwen1.5b','qwen3b','qwen7b','qwen32b']:
 lines+=['\n## '+model,'|长度|单macro正确率|macro连乘预测|原A/B分开连乘|实际整题|前macro正确后当前出错|前macro错误后当前出错|','|---|---:|---:|---:|---:|---:|---:|']
 for z in summary:
  if z['family']!='independent' or z['model']!=model:continue
  c=z['counts'];rates=[]
  for g in ['prev_ok','prev_bad']:
   n=c.get(g+'_present_n',0);bad=c.get(g+'_present_current_bad',0);rates.append(f'{100*bad/n:.2f}% ({bad}/{n})' if n else '无样本')
  lines.append('| '+str(z['length'])+' | '+' | '.join(f'{100*z[k]:.2f}%' for k in ['macro_accuracy','macro_product','separate_AB_product','actual'])+' | '+' | '.join(rates)+' |')
lines+=['\n后两列仅统计相邻两个macro都实际输出的情况，缺失不混入。它们是条件相关性，不控制程序难度；前一macro错误会使后续位置持续错位，也不等于复制错误。JSON另保留缺失与逐位置标准化结果。','\n原3–5调用集全部逐长度数据也保存在analysis/macro-factorization.json。']
(R/'MACRO_FACTORIZATION.md').write_text('\n'.join(lines));print('\n'.join(lines))
