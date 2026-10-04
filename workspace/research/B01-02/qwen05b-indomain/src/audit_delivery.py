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
labels={'flat':'Uniform step','position':'Position index','alias':'Fixed alias','macro':'Original tool name'}
lines=[]
def add(x=''):lines.append(x)
add('# Qwen2.5-0.5B in-domain label replication')
add()
add('Completed 2026-09-27 UTC. All evaluations use lengths supported by training. This round includes neither out-of-domain long sequences nor prompt-only controls.')
add()
add('## Research question and conclusion')
add()
add('Given four digits and a tool-call order, the model emits primitive operations, every intermediate state, and the final `Answer`. Strict success requires the complete correct operation sequence, all intermediate numbers, and the answer. Original 1.5B short-task scores were near perfect; this study tests whether the smaller same-family 0.5B model and progressively longer training tasks provide room for in-domain improvement.')
add()
add('**Main observation:** Maximum training length five first meets the revised, prespecified headroom threshold. Fixed aliases and original names outperform uniform step by 10.92 and 11.10 percentage points, respectively, with positive differences for all 20 paired seeds. Position indices score 6.23 points below step. **Differences concentrate at one/two calls; all four groups score 100% at four/five calls.** Evidence supports reduced short-task degradation under this sampling scheme, rather than better execution of five-call tasks themselves.')
add()
add('## Inherited settings')
add()
add('- Official Qwen2.5 Base; existing LoRA r16/alpha32/dropout0 and seven projection types; AdamW, LR 3e-4, and the original schedule. Use 512 optimization steps, microbatch 16 with accumulation 2, and 16384 example presentations per run. No test-based checkpoint selection.')
add('- Fixed nine tools, four-digit operations, original prompt, Answer termination protocol, four label input/output formats, and fixed alias mapping. Label order: uniform step, position index, fixed alias, original tool name.')
add('- Twenty paired training seeds: 11, 22, 33, and 100–116. A shared seed controls LoRA initialization and example shuffling. Greedy decoding, batch 32, and the existing strict complete-trajectory scorer.')
add('- Maximum length two reuses the original 4096 training examples and 128 short IID tests verbatim. Existing models and historical results remain unchanged.')
add()
add('## Changes and freeze order')
add()
add(f'- The only model change is to `Qwen/Qwen2.5-0.5B` Base, revision `{audit["model_revision"]}`. Model/data hashes are in `analysis/delivery-audit.json` and length-specific manifests.')
add('- The user rejected the original 99% saturation threshold before running. Before any 0.5B result, it was replaced by STEP mean strict success ≤90% across 20 seeds, with at least 15 seeds individually ≤95%. Original text and amendment remain in `REGISTRATION.md`. This identifies error headroom without guaranteeing identity-label gains.')
add('- Freeze 4096 training examples separately for maximum lengths 3–5. Extend the original uniform-over-chains generator to lengths 1–L, with uniform digits and chain/input deduplication. Data seeds are 903/904/905. Retain the original 128 short tests and add 128 for each new length. L5 has 512 tests shared by all labels within each seed. Evaluate only training-supported lengths.')
add('- Maximum L5 training target length is 269 tokens, exceeding the old 256-token assertion. Raise only that assertion to 512. Generation `max_new_tokens=256`, greedy decoding, parsing, and scoring are unchanged. Lengths 2–4 require no compatibility adjustment.')
add()
add('## STEP screening')
add()
add('| Maximum training call length | Test examples/seed | STEP mean ± seed sample SD | Decision |')
add('|---:|---:|---:|---|')
for L in range(2,6):
    s=json.loads((R/f'analysis/scores-L{L}.json').read_text())
    v=s['scores']['flat']
    add(f'| {L} | {len(s["test_ids"])} | {p(v["mean"])} ± {p(v["sample_sd"])} | {"Headroom found; stop extending" if L==5 else "Still saturated; extend"} |')
add()
add('Length five first meets the threshold, so maximum lengths 6–8 were not trained. This baseline-based difficulty selection cannot be interpreted as a confirmatory analysis of a task fixed independently of selection or as post hoc selection for positive label results.')
add()
add('## Four-label primary comparison at maximum length five')
add()
add('| Output label | In-domain strict trajectory success, 20-seed mean ± SD | Paired difference from step, mean ± SD | Improved paired seeds |')
add('|---|---:|---:|---:|')
for c in order:
    if c=='flat':delta='Baseline';wins='—'
    else:
        z=scores['paired_vs_flat'][c]
        delta=f'{z["mean"]*100:+.2f} ± {z["sample_sd"]*100:.2f} percentage points'
        wins=f'{z["positive_seeds"]}/20'
    add(f'| {labels[c]} | {p(means[c])} ± {p(sds[c])} | {delta} | {wins} |')
add()
add('Descriptive t intervals for paired seed differences (df=19): fixed alias versus STEP +9.32 to +12.52 points; original name +9.54 to +12.67; position index −9.24 to −3.22. Training data, test examples, and alias mapping are fixed. Intervals cover training-seed variation, not task or mapping variation.')
add()
add('### By call length')
add()
add('| Calls | Examples/seed | Uniform step | Position index | Fixed alias | Original name |')
add('|---:|---:|---:|---:|---:|---:|')
for d in range(1,6):
    add(f'| {d} | {depth[d]["flat"][1]//20} | '+ ' | '.join(p(depth[d][c][2]) for c in order)+' |')
add()
add('Length-specific denominators repeat the same examples across 20 seeds: 220 one-call outputs, 2340 two-call outputs, and 2560 at each other length. These are not independent fresh examples.')
add()
add('### Strict success by training seed')
add()
add('| Seed | Uniform step | Position index | Fixed alias | Original name | Alias−step | Original−step |')
add('|---:|---:|---:|---:|---:|---:|---:|')
lookups={c:{x['seed']:x['rate'] for x in scores['scores'][c]['seeds']} for c in order}
for seed in SEEDS:
    vals=[lookups[c][seed] for c in order]
    add(f'| {seed} | '+ ' | '.join(p(v) for v in vals)+f' | {(vals[2]-vals[0])*100:+.2f} | {(vals[3]-vals[0])*100:+.2f} |')
add()
add('## Data/scoring audits and interpretation limits')
add()
add('- The 4096 L5 training examples contain only 1/4/40/379/3672 examples at 1/2/3/4/5 calls, respectively. This follows directly from uniform sampling over all chains of length ≤L. Sparse short-task exposure may explain degradation of STEP and position indices, but the design does not independently test that mechanism.')
add('- Training/test chain-input pairs do not overlap. Tests retain 128 old short examples and add 128 each at 3/4/5 calls. Removing headers yields identical operations and Answer targets across all L5 labels. Fixed aliases apply to both inputs and outputs.')
add('- All 80 formal runs have 512 steps, 16384 example presentations, and identical model revision/trainable LoRA parameter count. All 40960 raw in-domain outputs are retained individually. The old scorer checks complete trajectories without requiring correct headers; a label-aware recheck yields identical strict success counts at every length.')
add('- Differences mainly involve extra tool execution. For L5-trained STEP, the 207/939 failed one-/two-call seed outputs all have operation-sequence mismatches, with zero intermediate arithmetic errors. Position labels often continue with extra steps on short tasks. These observations do not identify internal mechanisms.')
add('- Every group is perfect at four/five calls, so this round cannot establish identity-label improvements there; more seeds cannot create headroom at saturated lengths. L5 training is overwhelmingly five-call data, making short-task reliability a retention question under changed distribution weights.')
add('- Only one training dataset, test set, and fixed alias mapping are used. Aliases and original names differ in input tokens and target lengths. Seed consistency does not establish consistency across mappings, datasets, or real-agent tasks. One-call training contains only one example and is not a well-learned one-call distribution.')
add()
add('## Costs and evidence')
add()
add(f'- Recorded post-loading GPU allocation for the 80 formal L5 runs totals {audit["total_recorded_gpu_hours"]:.2f} hours (sum of run durations, including inference/saving). Twenty STEP runs each at L2/3/4 are also complete. Outer durations for all 140 jobs total approximately 6.05 allocated GPU-hours, including loading and environment overhead. Eight local PRO6000 GPUs were used; all memory was empty at completion.')
add('- Registration/amendments: `REGISTRATION.md`; data manifests: `data/L3/manifest.json`, `data/L4/manifest.json`, `data/L5/manifest.json`; seed/paired results: `analysis/scores-L5.json`; full original scores: `analysis/graded-L5.jsonl`; audit: `analysis/delivery-audit.json`.')
add('- Runs are in `runs/L5-{condition}-s{seed}/`, retaining driver snapshots, configurations, 512-step logs, adapters, raw `predictions.jsonl`, `summary.json`, and completion markers. Dispatch exits: `analysis/dispatch-L5-*.json`.')
add()
add('Prompt-only controls and real-execution extensions remain future notes; neither was launched.')
(R/'REPORT.md').write_text('\n'.join(lines)+'\n')
print(f'audited {audit["run_count"]} runs / {audit["decoded_predictions"]} predictions; wrote REPORT.md')
