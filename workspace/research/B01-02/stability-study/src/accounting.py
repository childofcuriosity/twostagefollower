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
    lines = ['# Training exposure and resource accounting',
             'This study reuses trained weights, with no retraining for the main matrix. The table gives actual counts from the original training; each full 512-step condition sees 16384 examples.',
             '|Model|Seed|Joint 512-step supervised tokens|Sequence fraction|Operation fraction|Total supervised tokens for two 256-step specialists|Trainable parameters per adapter|',
             '|---|---:|---:|---:|---:|---:|---:|']
    for model in ['qwen3b', 'qwen32b']:
        for seed in [11, 22, 33]:
            z = {(r['condition'], r['step']): r for r in training if r['model']==model and r['seed']==seed}
            j = z['joint',512]; s = z['operation_oracle',512]; e = z['order_oracle',512]
            combined = z['operation_oracle',256]['supervised_tokens'] + z['order_oracle',256]['supervised_tokens']
            lines.append(f'|{model}|{seed}|{j["supervised_tokens"]}|{100*s["supervised_tokens"]/j["supervised_tokens"]:.2f}%|{100*e["supervised_tokens"]/j["supervised_tokens"]:.2f}%|{combined}|{j["trainable_parameters"]}|')
    lines += ['', 'Joint training averages loss over valid target tokens; specialists average over their own supervised components. Sequence fraction is a target-token count fraction, not measured gradient contribution, and alone does not establish gradient conflict or diluted learning.',
              'Two 256-step specialists and one 512-step joint model have equal cumulative example exposure/optimizer steps, but differ in repeated-example allocation, supervised-token counts, and parameter storage. Two specialist adapters contain twice the parameters of one adapter. Weight-balanced or capacity-matched experiments are still needed to exclude these explanations.',
              f'Total allocated GPU wall time for completed new evaluation jobs: {sum(x["wall_seconds"] for x in jobs)/3600:.2f} GPU-hours, including loading, initial archived calibration, and failed jobs, but excluding unfinished jobs. This is not active GPU-kernel time.',
              '', '|Stage|Completed jobs|Allocated GPU-hours|', '|---|---:|---:|']
    for stage in ['main','context','fresh','initial_calibration']:
        selected=[j for j in jobs if j['stage']==stage]
        lines.append(f'|{stage}|{len(selected)}|{sum(j["wall_seconds"] for j in selected)/3600:.2f}|')
    (R/'RESOURCE_ACCOUNTING.md').write_text('\n'.join(lines)+'\n')
    print('Accounting training rows:', len(training), 'completed jobs:', len(jobs))


if __name__ == '__main__':
    main()
