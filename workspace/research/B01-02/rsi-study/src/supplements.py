from common import *
import statistics
coverage=json.loads((ROOT/'analysis/coverage-results.json').read_text());length=json.loads((ROOT/'analysis/length-results.json').read_text());curve=json.loads((ROOT/'analysis/timecourse-results.json').read_text());inf=json.loads((ROOT/'analysis/loop-inference.json').read_text())
def pc(x):return f'{x*100:.2f}%'
def pp(x):return f'{x*100:+.2f}'
c=coverage['coverage']['instruction-t1.0-k16'];table=[]
for m,d in length['summary'].items():table.append(f"| {m} | {pc(d['base']['mean'])} | {pc(d['flat']['mean'])} | {pc(d['macro']['mean'])} |")
times=[]
for step,r in curve['summary'].items():times.append(f"| {step} | {pc(r['iid_accuracy'])} | {pc(r['ood_accuracy'])} | {pc(r['proposal_compression'])} |")
branches=[]
gradient_rows=[]
gradient_summary={}
for step in [0,16,64,128,256,512]:
 rs=[r for p in (ROOT/'runs').glob('gradient-original-*/results.json') for r in json.loads(p.read_text())['records'] if r['step']==step]
 assert len(rs)==9
 g=dict(mean_cosine=statistics.mean(r['cosine'] for r in rs),negative_batches=sum(r['cosine']<0 for r in rs),batches=len(rs),proposal_surrogate_nll=statistics.mean(r['proposal_surrogate_loss'] for r in rs))
 gradient_summary[step]=g
 gradient_rows.append(f"| {step} | {g['mean_cosine']:+.4f} | {g['negative_batches']}/9 | {g['proposal_surrogate_nll']:.4f} |")
(ROOT/'analysis/original-gradient-summary.json').write_text(json.dumps(gradient_summary,indent=2))
for domain,d in inf['posthoc_legacy_comparisons'].items():
 for source,stats in d.items():
  for split,x in stats.items():branches.append(f"| {domain} | {source} | {split} | {pp(x['mean'])} | {' / '.join(pp(v) for v in x['seed_differences'])} | {' 至 '.join(pp(v) for v in x['t_interval_95'])} |")
text=f'''# 补充控制与训练时间轴

这些实验均在部分主结果已知后登记并运行，不冒充原预注册结果。原结果与失败保留。

## 缺少原语是否解释退化

原9个宏没有ends，新的测试家族有31/48隐含模式含ends，测试程序83.11%含ends，因此这是实质性混淆。固定人工覆盖干预把brown=inc,inc,inc替换为ends,inc,inc，其余调用链/输入/步数不变。三个seed真实累计训练输入和监督token逐项与原macro相同。

主提案设置：base {pc(c['base'])}，原macro {pc(c['original_macro'])}，补齐覆盖 {pc(c['compression'])}。提案包含ends比例恢复到{pc(c['contains_ends'])}；覆盖补齐相对原macro差{pp(c['coverage_minus_original_macro']['mean'])}个百分点，家族bootstrap区间{' 至 '.join(pp(x) for x in c['coverage_minus_original_macro']['family_bootstrap_95'])}。不能把这点均值改善宣称为显著恢复，但它仍明显低于base。因此缺少一个原语不是充分解释；没有排除更广泛的训练分布狭窄。

## 候选停止长度控制

主实验允许长度2–3，3B模型训练后更偏好较短输出。追加每个家族固定8条长度2、8条长度3的语法配额，提示、T=1和选库器不变。

| 模型 | base | flat | macro |
|---|---:|---:|---:|
{chr(10).join(table)}

完整seed差与区间见[length-results.json](analysis/length-results.json)。这是新解码条件，不能把数值直接当原采样分布的替换成绩。

## 原训练配方的完整时间轴

重新执行原宏训练三个seed，优化器和数据顺序保持，在固定步数插入只读评测，未根据测试分数选早停。

| 优化步 | IID执行 | 未见组合执行 | 新家族提案净压缩 |
|---|---:|---:|---:|
{chr(10).join(times)}

最终权重与原训练逐seed哈希一致检查：{json.dumps(curve['final_weight_matches'],ensure_ascii=False)}。一致才可将曲线解释为同一确定性训练轨迹的检查点观察。

![训练时间轴](figures/training-timecourse.png)

这里时间轴的采样随机数路径与主稳健性作业不同，所以最终提案净压缩10.37%与主表9.06%不是同一批提案；执行任务、最终模型权重相同。第16步提案效用已从40.26%降到20.78%，第64步约9.48%，下降不只出现在训练末期。

## 原配方梯度诊断

以下探针直接使用上述原配方检查点和执行数据，与主报告中闭环配方的诊断分开。每个检查点为三个seed各三个固定小批次；初始化检查点相同，九批不能当作九个独立模型。

| 步数 | 平均梯度余弦 | 负余弦批次 | 提案替代目标NLL |
|---|---:|---:|---:|
{chr(10).join(gradient_rows)}

更新后多处出现局部梯度冲突，支持继续考察目标之间的干扰。但是第16步提案替代NLL比初始化更好，实际采样效用却已明显降低；因此该NLL不是提案效用的充分代理。梯度余弦既没有包含AdamW预条件的完整更新方向，也不构成长期退化的因果证明。闭环配方同样出现过负余弦而提案未持续下降，不能把“检测到负余弦”直接等同于RSI瓶颈。

## 退化提案者压力干预

主闭环中的提案者未必退化，因此另用第一轮确实退化的数字macro适配器作为外部提案者。学习器仍从同一个shared轮1检查点开始，提案支持、选库、执行器和128步训练保持；两个执行域均采用同一来源的原语序列提案。它检验人为引入退化提案源的总效应，**不是自然闭环自行陷入退化的证据**。

表中正数表示base/updated来源优于legacy来源；起点相同，因此是下一轮学习增益差。

| 域 | 比较 | 评测 | 差（百分点） | 三seed差 | 95% t区间 |
|---|---|---|---:|---|---|
{chr(10).join(branches)}

每个来源实际产生的宏库、训练长度、语义覆盖及支持/保留程序压缩见[curriculum-rows.jsonl](analysis/curriculum-rows.jsonl)。提案源会改变课程长度和训练token数；这些比较是相同样本/步数下的总效应，不是等token的纯提案质量效应。抽象压缩P是候选代理指标，只有观察到后续学习变化G才与改进能力建立联系；二者不能互相代称。
'''
(ROOT/'SUPPLEMENT.md').write_text(text)
report=ROOT/'REPORT.md';s=report.read_text();s+='\n\n## 补充控制与时间轴\n\n详见[SUPPLEMENT.md](SUPPLEMENT.md)：原语覆盖、候选长度配额、原训练检查点曲线及事后退化提案者压力分支。所有结果与原预注册实验分开。\n';report.write_text(s);print('Supplement generated')
