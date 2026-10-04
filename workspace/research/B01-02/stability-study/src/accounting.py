"""Observed training exposure, parameter storage, and inference job wall time."""
import collections, json
from common import R, O, write


def main():
    training = []
    for model in ['qwen3b', 'qwen32b']:
        for seed in [11, 22, 33]:
            by_condition = {}
            for condition in ['joint', 'operation_oracle', 'order_oracle']:
                root = O/'runs'/f'{model}-{condition}-s{seed}'
                complete = json.loads((root/'training-complete.json').read_text())
                logs = [json.loads(line) for line in (root/'train.jsonl').read_text().splitlines()]
                by_condition[condition] = logs
                for step in [64, 128, 256, 512]:
                    item = logs[step-1]
                    assert item['step'] == step
                    training.append(dict(model=model, seed=seed, condition=condition, step=step,
                                         **{k: item[k] for k in ['examples', 'input_tokens', 'supervised_tokens', 'seconds']},
                                         trainable_parameters=complete['trainable_parameters'],
                                         gpu=complete['config']['gpu']))
            # All conditions see the same text; masks partition the joint target.
            for step in [64, 128, 256, 512]:
                j, s, e = [by_condition[c][step-1] for c in ['joint', 'operation_oracle', 'order_oracle']]
                assert j['examples'] == s['examples'] == e['examples']
                assert j['input_tokens'] == s['input_tokens'] == e['input_tokens']
                assert j['supervised_tokens'] == s['supervised_tokens'] + e['supervised_tokens']
    jobs = []
    for stage,root in [('main',R),('context',R/'context-intervention'),('fresh',R/'fresh-confirmation'),
                       ('initial_calibration',R/'calibration-attempts/v1')]:
        for p in sorted((root/'analysis').glob('*-status.json')):
            d = json.loads(p.read_text())
            if 'job' not in d or 'end' not in d:
                continue
            jobs.append(dict(stage=stage,id=d['job']['id'], kind=d['job']['kind'], model=d['job']['model'],
                             wall_seconds=d['end']-d['start'], returncode=d['returncode'], source=str(p)))
    write(R/'analysis/resource-accounting.json', dict(training=training, completed_jobs=jobs,
          completed_job_gpu_hours=sum(x['wall_seconds'] for x in jobs)/3600,
          note='One assigned GPU per inference job; duration includes loading and CPU gaps, not active kernel time. '
          'Includes archived calibration attempts, including failed attempts. '
          'Training seconds are original sunk training cost, not new training in this study. '
          'Equal summed optimizer steps do not equal total adapter parameters or supervised tokens.'))
    lines = ['# 训练暴露与资源口径',
             '本轮复用已训练权重，没有为主矩阵重新训练。下表是原训练的实际计数；每条件完整512步看16384条样本。',
             '|模型|seed|一起训练512步监督tokens|顺序占比|操作占比|各专用256步监督tokens合计|单adapter可训练参数|',
             '|---|---:|---:|---:|---:|---:|---:|']
    for model in ['qwen3b', 'qwen32b']:
        for seed in [11, 22, 33]:
            z = {(r['condition'], r['step']): r for r in training if r['model']==model and r['seed']==seed}
            j = z['joint',512]; s = z['operation_oracle',512]; e = z['order_oracle',512]
            combined = z['operation_oracle',256]['supervised_tokens'] + z['order_oracle',256]['supervised_tokens']
            lines.append(f'|{model}|{seed}|{j["supervised_tokens"]}|{100*s["supervised_tokens"]/j["supervised_tokens"]:.2f}%|{100*e["supervised_tokens"]/j["supervised_tokens"]:.2f}%|{combined}|{j["trainable_parameters"]}|')
    lines += ['', '一起训练按有效目标token平均损失；专用模型按各自被监督部分平均。顺序占比是目标token数量占比，不是实测梯度贡献比例，不能单凭它证明梯度冲突或学习稀释。',
              '两专用各256步与一起训练512步，累计样本/优化步数相同，但训练样本的重复分配、监督token数量及参数存储不同。两个专用adapter参数总量为一个的两倍。仍需权重平衡或容量匹配实验才能排除这些解释。',
              f'当前已结束的新评测作业合计分配GPU墙钟时间：{sum(x["wall_seconds"] for x in jobs)/3600:.2f} GPU小时（包含加载、首轮归档校准及失败作业，不包含尚未结束作业；不是GPU内核活跃时间）。',
              '', '|阶段|已结束作业数|分配GPU小时|', '|---|---:|---:|']
    for stage in ['main','context','fresh','initial_calibration']:
        selected=[j for j in jobs if j['stage']==stage]
        lines.append(f'|{stage}|{len(selected)}|{sum(j["wall_seconds"] for j in selected)/3600:.2f}|')
    (R/'RESOURCE_ACCOUNTING.md').write_text('\n'.join(lines)+'\n')
    print('Accounting training rows:', len(training), 'completed jobs:', len(jobs))


if __name__ == '__main__':
    main()
