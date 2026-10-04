"""Audit frozen L5 runs and produce a reproducible, descriptive report."""
from common import R, B, MODEL, CONDITIONS, SEEDS, WORLD, ALIASES, sha, write, target, dsl
import collections
import json
import math
import statistics
from transformers import AutoTokenizer
import sys
import importlib.util
spec = importlib.util.spec_from_file_location('label_control_grading',B/'label-controls/src/grading.py')
label_grading = importlib.util.module_from_spec(spec)
sys.path.insert(0,str(B/'label-controls/src'))
sys.modules.pop('common',None)
spec.loader.exec_module(label_grading)
grade=label_grading.grade

manifest = json.loads((R/'data/L5/manifest.json').read_text())
train = [json.loads(x) for x in (R/'data/L5/train.jsonl').read_text().splitlines()]
test = [json.loads(x) for x in (R/'data/L5/test.jsonl').read_text().splitlines()]
assert sha(R/'data/L5/train.jsonl') == manifest['sha256']['train']
assert sha(R/'data/L5/test.jsonl') == manifest['sha256']['test']
assert len(train) == 4096 and len(test) == 512
assert len({(tuple(x['chain']),tuple(x['x'])) for x in train+test}) == len(train)+len(test)
assert [x['id'] for x in test[:128]] == [json.loads(x)['id'] for x in (B/'data/test.jsonl').read_text().splitlines() if json.loads(x)['split']=='iid']
assert sha(B/'src/run.py') == manifest['source_sha256']
assert sha(B/'data/worlds.json') == manifest['worlds_sha256']
tok = AutoTokenizer.from_pretrained(MODEL, local_files_only=True)
base_targets = [target(x,WORLD['library'],'flat',WORLD['names']) for x in train]
def operations_and_answer(s):
    return '\n'.join(line for line in s.splitlines() if not line.endswith(':') or line.startswith('Answer:'))
assert all(operations_and_answer(base_targets[i]) == operations_and_answer(target(row,WORLD['library'],c,ALIASES if c=='alias' else WORLD['names']))
           for c in CONDITIONS for i,row in enumerate(train))
scores = json.loads((R/'analysis/scores-L5.json').read_text())
assert set(scores['scores']) == set(CONDITIONS)
audit = {'run_count':0,'each_condition_runs':{},'source_sha256':sha(B/'src/run.py'),
         'score_source_sha256':sha(R/'src/score.py'),
         'model_revision':json.loads((MODEL/'download-manifest.json').read_text())['revision'],
         'model_file_sha256':sha(MODEL/'model.safetensors'),
         'train_sha256':manifest['sha256']['train'],'test_sha256':manifest['sha256']['test'],
         'test_rows':len(test),'train_rows':len(train),
         'train_depth_counts':manifest['train_depth_counts'],
         'test_depth_counts':manifest['test_depth_counts'],
         'train_test_exact_overlap':0,'decoded_predictions':0,
         'total_recorded_gpu_hours':0,'training_sequence_cap':manifest['training_sequence_cap'],
         'generation_cap':manifest['generation_cap'],
         'compatibility_adjustments':manifest['compatibility_adjustments']}
label_aware = collections.defaultdict(lambda: collections.Counter())
for c in CONDITIONS:
    same=[]
    for seed in SEEDS:
        run=R/f'runs/L5-{c}-s{seed}'
        assert (run/'complete.json').exists() and not (run/'failed.json').exists()
        q=run/'runs'/f'{c}-original-s{seed}'
        meta=json.loads((q/'summary.json').read_text())
        log=[json.loads(x) for x in (q/'train.jsonl').read_text().splitlines()]
        assert len(log)==512 and [x['step'] for x in log]==list(range(1,513))
        assert all(math.isfinite(x['loss']) and math.isfinite(x['grad_norm']) for x in log)
        assert meta['args']['seed']==seed and meta['args']['condition']==c
        assert meta['args']['steps']==512 and meta['args']['microbatch']==16 and meta['args']['accum']==2
        assert meta['training']['counts']['examples']==16384
        assert meta['model_revision']==audit['model_revision']
        assert meta['trainable_parameters']==8798208
        predictions=[json.loads(x) for x in (q/'predictions.jsonl').read_text().splitlines()]
        assert len(predictions)==len(test)
        for row in predictions:
            # Run grade with the original label-control common module, not this run's wrapper.
            graded=grade(row,c)
            d=str(len(row['chain']))
            label_aware[c][d+'_strict']+=graded['strict_trace']
            label_aware[c][d+'_aware']+=graded['label_aware_complete']
            label_aware[c][d+'_n']+=1
        assert (q/'adapter/adapter_model.safetensors').exists()
        audit['decoded_predictions']+=len(test)
        audit['total_recorded_gpu_hours']+=meta['gpu_hours']
        same.append(sha(run/'driver_snapshot.py'))
    assert len(set(same))==1
    audit['each_condition_runs'][c]={'count':len(SEEDS),'driver_sha256':same[0]}
    audit['run_count']+=len(SEEDS)
assert audit['run_count']==80 and audit['decoded_predictions']==40960
audit['label_aware_by_depth']={c:dict(x) for c,x in label_aware.items()}
for c in CONDITIONS:
    for d in range(1,6):
        assert label_aware[c][str(d)+'_strict']==label_aware[c][str(d)+'_aware']
write(R/'analysis/delivery-audit.json',audit)

means = {c: scores['scores'][c]['mean'] for c in CONDITIONS}
sds = {c: scores['scores'][c]['sample_sd'] for c in CONDITIONS}
depth = {}
for d in range(1,6):
    depth[d]={}
    for c in CONDITIONS:
        ss=scores['scores'][c]['seeds']
        n=sum(x['by_depth'][str(d)]['n'] for x in ss)
        k=sum(x['by_depth'][str(d)]['correct'] for x in ss)
        depth[d][c]=(k,n,k/n)
def p(x):return f'{x*100:.2f}%'
order=['flat','position','alias','macro']
labels={'flat':'统一 step','position':'位置编号','alias':'固定改名','macro':'原工具名称'}
lines=[]
def add(x=''):lines.append(x)
add('# Qwen2.5-0.5B 域内标签复核')
add()
add('完成时间：2026-09-27 UTC。所有结果是训练支持长度内的评测；本轮没有运行域外长序列或纯 prompt 对照。')
add()
add('## 研究问题与结论')
add()
add('输入为四位数字和给定的工具调用顺序，模型逐工具输出原始操作、每步状态和最终 `Answer`。严格成功要求完整操作序列、全部中间数字和最终答案正确。原1.5B短题近乎满分；本轮检验更小的同系列0.5B及逐级加长训练任务能否提供域内改善空间。')
add()
add('**主要观察：**首次达到预先修订改善空间门槛的是最大长度5。该档固定改名与原工具名称分别比统一 step 高10.92和11.10个百分点，20/20配对seed均为正；位置编号比统一 step 低6.23个百分点。**但差异集中在1–2次调用，4–5次调用四组均100%。**因此证据支持身份标签在该采样下减少短任务退化，不支持“提升五次调用本身”的主张。')
add()
add('## 继承的设置')
add()
add('- 官方Qwen2.5 Base、旧LoRA r16/alpha32/dropout0与七种投影、AdamW、LR3e-4及原学习率日程。512优化步，microbatch16、累积2，单run暴露16384题；不按测试选择检查点。')
add('- 固定9工具、四位数字操作、旧prompt、Answer结束协议、四种标签的输入输出及固定改名映射；标签顺序为统一 step、位置编号、固定改名、原工具名称。')
add('- 20个配对训练seed：11、22、33、100–116；相同seed控制LoRA初始化和训练样本打乱。贪心解码，batch32，严格完整轨迹旧评分器。')
add('- 长度2档逐字使用旧4096条训练题与旧128条IID短测试题；旧模型与历史结果保持不动。')
add()
add('## 本轮差异与冻结顺序')
add()
add(f'- 仅把模型换为`Qwen/Qwen2.5-0.5B` Base，revision `{audit["model_revision"]}`。模型与数据hash见`analysis/delivery-audit.json`、各档manifest。')
add('- 运行前用户否决原99%饱和门槛；在任一0.5B结果出现前改为：STEP 20 seed平均严格成功率≤90%，且至少15个seed各自≤95%。旧文字和修订均留在`REGISTRATION.md`。此门槛只决定哪档有错误空间，不能保证身份标签会赢。')
add('- 长度3–5分别冻结4096训练题；按旧生成器的链均匀采样规则扩展到1–L，四位数均匀、链+输入去重。数据seed为903/904/905。测试逐档保留旧128短题，新增每个长度128题；长度5共512题、每seed四标签同题。只评测训练支持的长度。')
add('- 长度5目标训练序列实际最大269 token，旧训练器的256序列断言不再容纳目标，因此只把该断言提高到512；生成`max_new_tokens=256`、贪心、解析和评分均未改。长度2–4无需兼容调整。')
add()
add('## STEP筛查')
add()
add('| 训练最大调用长度 | 测试题/seed | STEP均值±seed样本SD | 判断 |')
add('|---:|---:|---:|---|')
for L in range(2,6):
    s=json.loads((R/f'analysis/scores-L{L}.json').read_text())
    v=s['scores']['flat']
    add(f'| {L} | {len(s["test_ids"])} | {p(v["mean"])} ± {p(v["sample_sd"])} | {"有改善空间，停止升级" if L==5 else "仍饱和，升级"} |')
add()
add('长度5是第一个满足门槛的档位，因此未训练最大长度6–8。这是按基线选择任务难度，不能用为阳性结果做事后挑选的确证解释。')
add()
add('## 长度5四标签主比较')
add()
add('| 输出标签 | 域内严格完整轨迹成功率，20 seed均值±SD | 相对统一step的配对差，均值±SD | 配对改善seed |')
add('|---|---:|---:|---:|')
for c in order:
    if c=='flat':delta='基线';wins='—'
    else:
        z=scores['paired_vs_flat'][c]
        delta=f'{z["mean"]*100:+.2f} ± {z["sample_sd"]*100:.2f}个百分点'
        wins=f'{z["positive_seeds"]}/20'
    add(f'| {labels[c]} | {p(means[c])} ± {p(sds[c])} | {delta} | {wins} |')
add()
add('配对seed差的描述性t区间（df=19）：固定改名相对STEP为+9.32至+12.52个百分点，原工具名称为+9.54至+12.67，位置编号为−9.24至−3.22。训练数据、测试题和改名映射固定，区间只覆盖训练seed波动；任务与映射变化未纳入。')
add()
add('### 按调用长度')
add()
add('| 调用长度 | 每seed题数 | 统一step | 位置编号 | 固定改名 | 原工具名称 |')
add('|---:|---:|---:|---:|---:|---:|')
for d in range(1,6):
    add(f'| {d} | {depth[d]["flat"][1]//20} | '+ ' | '.join(p(depth[d][c][2]) for c in order)+' |')
add()
add('这里逐长度分母是20 seed重复评测同一批题：一次调用220条、两次调用2340条、其余各2560条输出；它们不是相互独立的新题。')
add()
add('### 每个训练seed的严格成功率')
add()
add('| seed | 统一step | 位置编号 | 固定改名 | 原工具名称 | 改名−step | 原名−step |')
add('|---:|---:|---:|---:|---:|---:|---:|')
lookups={c:{x['seed']:x['rate'] for x in scores['scores'][c]['seeds']} for c in order}
for seed in SEEDS:
    vals=[lookups[c][seed] for c in order]
    add(f'| {seed} | '+ ' | '.join(p(v) for v in vals)+f' | {(vals[2]-vals[0])*100:+.2f} | {(vals[3]-vals[0])*100:+.2f} |')
add()
add('## 数据与评分审计、解释边界')
add()
add('- 长度5训练4096题：1/2/3/4/5次调用分别只有1/4/40/379/3672题；这是旧“所有长度≤L的调用链等概率”采样规则在L=5下的直接结果。短题供给变稀可能解释STEP和位置编号的短题退化，但现有设计没有单独验证这一机制。')
add('- 训练/测试的链+输入组合没有重复；测试包含旧128短题与新增的3/4/5次调用各128题。长度5所有标签训练目标去掉标题后操作和Answer逐题一致；固定改名在输入输出中同步生效。')
add('- 80个正式run全部512步、16384样本暴露、相同模型revision和LoRA可训练参数数；40960条原始域内输出逐题保留。旧严格评分器核对完整轨迹；旧评分不要求标题本身正确，另用标签感知评分复核后本轮各长度严格成功计数相同。')
add('- 差异主要是多做了工具：长度5的STEP在一次/两次调用失败207/939条seed输出，均出现操作序列不符；逐步数字错误计数为0。位置编号在短题常继续输出额外step。不能由此断定模型内部机制。')
add('- 四五次调用四组都满分，因此本轮无法证明身份标签提高这些长度的域内表现；更多seed也不能给已满分长度创造提升空间。长度5训练几乎全是五次调用，短长度的可靠性属于分布权重变化下的保持能力。')
add('- 本轮只使用一份训练数据、一套测试题和一套固定改名映射。固定改名与原名的输入token、目标长度不同；seed稳定性不等于跨映射、跨数据或真实Agent任务稳定性。长度1训练只有1题，不能把它的成绩看成充分学习过的一次调用分布。')
add()
add('## 成本与证据位置')
add()
add(f'- 本轮正式L5 80个run记录模型加载后的GPU分配时间合计{audit["total_recorded_gpu_hours"]:.2f}小时（每run总耗时求和，含推理与保存）；L2/3/4各20个STEP run也已完成。按全部140个job的外层运行时长求和约6.05分配GPU小时，含模型加载与环境开销。使用本机8张PRO6000；结束时GPU显存均为空。')
add('- 登记及修订：`REGISTRATION.md`；数据冻结清单：`data/L3/manifest.json`、`data/L4/manifest.json`、`data/L5/manifest.json`；逐seed和配对结果：`analysis/scores-L5.json`；全量逐题旧评分：`analysis/graded-L5.jsonl`；审计：`analysis/delivery-audit.json`。')
add('- 每个run位于`runs/L5-{condition}-s{seed}/`，保留driver快照、配置、512步训练日志、LoRA adapter、原始`predictions.jsonl`、`summary.json`及完成标记；分发退出记录在`analysis/dispatch-L5-*.json`。')
add()
add('后续纯prompt对照与真实执行任务拓展仍只是备忘，本轮没有启动。')
(R/'REPORT.md').write_text('\n'.join(lines)+'\n')
print(f'audited {audit["run_count"]} runs / {audit["decoded_predictions"]} predictions; wrote REPORT.md')
