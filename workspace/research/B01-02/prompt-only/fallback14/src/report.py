from common import *
import collections,datetime
from transformers import AutoTokenizer
selection=json.loads((R/'analysis/length-selection.json').read_text());lengths=selection['lengths']
tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True)
eos=json.loads((MODEL/'generation_config.json').read_text())['eos_token_id']
if isinstance(eos,int):eos=[eos]
seen={key(EXAMPLE):'example'};splits=collections.Counter()
for f in sorted((R/'data').glob('*.jsonl')):
 for x in readrows(f):
  k=key(x);assert k not in seen,(f,k,seen.get(k));seen[k]=f.name;splits[x['split']]+=1
checks=[];scores=[]
for L in lengths:
 manifest=json.loads((R/f'data/formal-L{L}-manifest.json').read_text());assert manifest['data_sha256']==sha(R/f'data/formal-L{L}.jsonl')
 rows=readrows(R/f'data/formal-L{L}.jsonl');assert len(rows)==512
 graded=readrows(R/f'analysis/graded-formal-L{L}.jsonl');assert len(graded)==2048
 for c in CONDITIONS:
  run=R/f'runs/formal-L{L}-{c}';rr=readrows(run/'predictions.jsonl');assert len(rr)==512
  assert [x['id'] for x in rr]==[x['id'] for x in rows]
  assert (run/'complete.json').exists()
  assert sha(R/f'prompts/{c}.txt')==manifest['prompts'][c]
  for x,y in zip(rr,rows):
   assert key(x)==key(y)
   ids=x['output_token_ids'];assert len(ids)==x['generated_tokens']
   assert tok.decode(ids,skip_special_tokens=True)==x['raw']
   assert x['max_new_tokens']==manifest['max_new_tokens']
   assert x['input_tokens']+manifest['max_new_tokens']<=manifest['context']
   if x['finish_reason']=='eos':assert ids[-1] in eos and all(i not in eos for i in ids[:-1])
   else:assert len(ids)==x['max_new_tokens'] and not any(i in eos for i in ids)
  checks.append(dict(length=L,condition=c,n=len(rr),predictions_sha256=sha(run/'predictions.jsonl')))
 scores.append(json.loads((R/f'analysis/scores-formal-L{L}.json').read_text()))
# Confirm all registered initial exploration lengths and selection rule using only STEP.
rates=selection['step_rates'];assert all(str(L) in rates for L in [2,5,10,15,20,30,40])
eligible=sorted(int(L) for L,r in rates.items() if .2<=r<=.9)
expected=sorted(set([eligible[0],eligible[-1]])) if eligible else [min(map(int,rates),key=lambda L:(abs(rates[str(L)]-.5),L))]
assert lengths==expected
sources={}
for L in lengths:
 manifest=json.loads((R/f'data/formal-L{L}-manifest.json').read_text())
 for name,h in manifest['source'].items():
  assert sha(R/'src'/name)==h,(name,'changed after formal freeze')
 sources[L]=manifest['source']
audit=dict(passed=True,formal_rows=2048*len(lengths),selected_lengths=lengths,disjoint_data_counts=dict(splits),raw_checks=checks,source_hashes=sources,verified_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
write(R/'analysis/completion-audit.json',audit)
lines=['# 纯 Prompt 下复述工具身份：正式结果','',f'模型：{json.loads((MODEL/"download-manifest.json").read_text())["repo"]} 原始权重，无adapter、无训练。主比较NAME−STEP；完整操作序列、全部中间状态及最终Answer均须正确。','', '## 选长与探索','', '正式长度只依据STEP选出：'+', '.join(map(str,lengths))+'。'+('没有20%–90%档位，按登记取最接近50%的已测长度；存在地板/饱和限制。' if selection['fallback'] else '取20%–90%范围内最短与最长档。'),'', '| 调用长度 | STEP | NAME |','|---:|---:|---:|']
for L in sorted(map(int,rates)):
 s=json.loads((R/f'analysis/scores-explore-L{L}.json').read_text())['results'];lines.append(f'| {L} | {s["STEP"]["correct"]}/32 ({s["STEP"]["rate"]:.2%}) | {s["NAME"]["correct"]}/32 ({s["NAME"]["rate"]:.2%}) |')
lines+=['','## 正式四组','', '| L | 标题 | 严格成功率 | 相对STEP配对差，95%区间（百分点） | 标题全符合 | 输出token/题 | 输入token/题 | generate秒 |','|---:|---|---:|---|---:|---:|---:|---:|']
for score in scores:
 L=score['length']
 for c in CONDITIONS:
  s=score['results'][c];p=score['paired_vs_STEP'].get(c)
  diff='—' if p is None else f'{100*p["difference"]:+.2f} [{100*p["ci95"][0]:+.2f}, {100*p["ci95"][1]:+.2f}]'
  lines.append(f'| {L} | {c} | {s["correct"]}/512 ({s["rate"]:.2%}) | {diff} | {s["header_compliance"]:.2%} | {s["mean_output_tokens"]:.2f} | {s["mean_input_tokens"]:.2f} | {s["generate_seconds"]:.2f} |')
lines+=['','每题每组仅一次贪心生成，四组共享底层题目。95%区间来自10,000次逐题配对bootstrap（seed740001），仅反映固定模型、Prompt及题目分布下的抽样不确定性。没有把重复推理当作seed；辅助比较不作多重校正后的确认性宣称。','', '## 主比较及成本','']
for score in scores:
 L=score['length'];s=score['results']['STEP'];n=score['results']['NAME'];p=score['paired_vs_STEP']['NAME']
 dt=n['mean_output_tokens']-s['mean_output_tokens'];ds=n['generate_seconds']-s['generate_seconds']
 lines.append(f'- L{L}：NAME−STEP {100*p["difference"]:+.2f}个百分点；仅NAME成功{p["better"]}题、仅STEP成功{p["worse"]}题。输出{dt:+.2f} token/题（{dt/s["mean_output_tokens"]:+.2%}）；批量generate总耗时{ds:+.2f}秒（{ds/s["generate_seconds"]:+.2%}）。')
lines+=['','## 首错与结束原因','', '| L | 条件 | 首错计数 | 结束原因 |','|---:|---|---|---|']
for score in scores:
 for c in CONDITIONS:
  s=score['results'][c];lines.append(f'| {score["length"]} | {c} | {json.dumps(s["first_errors"],ensure_ascii=False)} | {json.dumps(s["finish_reasons"])} |')
lines+=['','首错标签：numeric=数字计算/最终数字错误；tool_or_order=原始操作展开或顺序错误；omitted_call/extra_call=提前Answer、缺失/多出原始操作或可识别的整调用删除/插入；format=格式错误；none=没有严格轨迹错误。这里的遗漏/增加是可观测输出分类，并非模型内部原因；标题数量另有非互斥统计。标题不符合不自动计入主指标失败。','', '## 解释边界与证据','', '本实验只检验给定九工具和四位状态的合成执行任务；没有训练长度范围，不使用域内/域外术语。ALIAS同时更改输入输出名称，不能被解释成只改输出标题。标签词形、token化、Prompt及示例选择未做独立重复，不能唯一归因于身份信息或推断真实Agent收益。','', '输出token包括生成的EOS（另存text_tokens）；generate耗时为GPU同步后的批量墙钟，不能等同单题独立延迟。各卡并行负载和序列长度影响实际成本。调度台账另含加载、保存等分配GPU时长。','', '证据：REGISTRATION.md（顶层）；prompts/四组模板；data/冻结配置与题目；runs/原始文本、token IDs、停止原因与完整性标记；analysis/scores-*、graded-*、length-selection.json、completion-audit.json；logs/运行日志。跨模型验证与真实任务迁移留待后续，未对外发布。','']
(R/'REPORT.md').write_text('\n'.join(lines))
print(json.dumps(audit,ensure_ascii=False)[:1500])
