import json,statistics,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
main=json.loads((ROOT/'analysis/results.json').read_text())
second=json.loads((ROOT/'secondary/analysis/results.json').read_text())
cost=json.loads((ROOT/'analysis/compute-cost.json').read_text())
secjobs=json.loads((ROOT/'secondary/analysis/completed.json').read_text())
assert len(secjobs)==6 and all(r['returncode']==0 for r in secjobs)
cost['reserved_gpu_hours_by_phase']['secondary']=sum(r['wall_seconds'] for r in secjobs)/3600
cost['total']=sum(cost['reserved_gpu_hours_by_phase'].values())
(ROOT/'analysis/compute-cost.json').write_text(json.dumps(cost,indent=2))
def mean(c,split,world='original',tag=''):
 return statistics.mean(json.loads((ROOT/f'runs/{c}-{world}-s{s}{tag}/summary.json').read_text())['evaluation']['groups'][split]['accuracy'] for s in [11,22,33])
def pc(x):return f'{100*x:.2f}%'
comparison=main['primary_comparisons']['macro-vs-flat']
sec_table='\n'.join(f"| {c} | {pc(statistics.mean(second['conditions'][c]['iid']))} | {' / '.join(pc(x) for x in second['conditions'][c]['ood'])} | {pc(statistics.mean(second['conditions'][c]['ood']))} | {pc(statistics.mean(second['conditions'][c]['pressure']))} |" for c in ['flat','macro'])
core_table='\n'.join(f"| {c} | {pc(mean(c,'iid'))} | {pc(mean(c,'ood'))} |" for c in ['flat','macro','natural','shuffled'])
files=list((ROOT/'runs').glob('*/predictions.jsonl'))+list((ROOT/'secondary/runs').glob('*/predictions.jsonl'))+list((ROOT/'analysis/routing-probe').glob('*.jsonl'))
raw_count=sum(sum(1 for _ in p.open()) for p in files)
report=f'''# B01-02 results review

Status: mechanism analysis and experiments for this round are complete, awaiting consolidated user review. Generated at (UTC): {time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}.

## Judgment

**A repeatable training-representation effect is observed, but learning to innovate is not established. Do not yet promote this topic to the main paper direction; retain the mechanism observation and experimental assets.**

The primary experiment passes the prespecified three-point screen. Macro-name-organized traces outperform information- and training-token-matched flat traces by **{comparison['mean_difference']*100:.2f} percentage points**. Failures mainly concern long-chain organization/early stopping; external stepwise routing brings both groups to 100%, and existing content-addressing/compositional-generalization work is close. Large score gains do not directly establish novel abstraction discovery. Additional literature review lowered the novelty assessment during the experiment; that change remains documented.

## What was run

- Base: Qwen/Qwen2.5-1.5B, revision `8faed761d45a263340a0528343f099c05c9a4323`; update 18,464,768 LoRA parameters, rank 16/alpha 32. This is not full-parameter pretraining or complete SPEE replication.
- Each formal run: 512 steps, batch 32, 16,384 example presentations (four passes over 4,096 examples), seeds 11/22/33. Each original primary run has 2,430,112 nonpadding input tokens, including 1,055,432 supervised targets.
- All runs use project `.training-venv`: torch 2.7.1+cu128, transformers 4.51.3, peft 0.15.2. Independent jobs use separate local RTX PRO6000 Blackwell GPUs; NCCL distributed-training acceptance is not claimed.
- Twelve primary runs, six name/semantic interventions, six post hoc alignment controls, and six second-environment replications: 30 formal training runs. Also one calibration, two frozen baselines, and seven external-routing diagnostics. Checkpoints/failure logs remain.
- Retained **{raw_count:,} raw example-level records**, including repeated evaluations across models/seeds rather than equally many independent tests.

## Primary results

Train macro-composition depth 1–2 and test 3–5. Tests omit macro definitions while sharing primitive instructions. OOD has 384 examples from only 96 programs, each with four inputs. Exact affine signatures exclude test functions equivalent to training.

| Condition | Mean IID | Mean unseen-composition OOD |
|---|---:|---:|
{core_table}

Macro OOD scores are 30.73%, 37.76%, 20.83%; flat scores are 0.26%, 0%, 0%. All paired differences are positive, averaging 29.69 points, with a three-training-seed t interval approximately **8.60–50.78 points**. Descriptive program-clustered bootstrap conditional on the three checkpoints gives approximately 22.13–37.15 points. These intervals differ in meaning; the latter does not replace more training seeds.

Actual cumulative input tokens, supervised tokens, and example counts match exactly across flat/macro/shuffled. Natural has more supervised tokens (1,312,060) and is secondary. Every group has a 256-token inference cap, but mean actual generation differs: approximately 67.1 for flat and 90.7 for macro. **Total inference compute is not matched.**

## What theory and interventions show

1. **Information equivalence.** Flat/macro share expanded primitives, every state, answers, and group boundaries. Macro labels are deterministically recoverable from input call order. Differences concern representation organization/optimization under finite training, not added supervision information.
2. **Executing modules does not guarantee organizing long chains.** Of 383 original flat seed-11 OOD failures, 375 stop after correct prefixes. An external loop requests macros in the supplied order using only preceding model outputs, without oracle states. Flat/macro score 100% across all three seeds (96 independent programs each); frozen base scores 0%. This post hoc diagnostic changes inference procedure/cost and does not replace autonomous OOD scores.
3. **Renaming does not establish strict invariance.** After cyclic name permutation, mean macro OOD is {pc(mean('macro','ood','renamed'))}, versus original {pc(mean('macro','ood'))}, with substantial seed variation. Results exclude dependence on one fixed name assignment but do not establish full name invariance.
4. **Behavior follows trained semantics.** On 550 examples with different old/new answers, semantically permuted models score 45.09%–70.00% against new semantics and 0% against old semantics across all seeds. Behavior depends on new training definitions, but permutation also changes some expansion lengths, so cross-world differences do not isolate semantics.
5. **Alignment remains an alternative.** Additional paired training with shared call-tags inputs gives mean OOD for stable macro labels {pc(mean('macro','ood',tag='-tagged-stable'))}, versus per-example random call labels {pc(mean('macro','ood',tag='-tagged-call'))}. Random labels lack a fixed output-label-to-macro mapping yet transfer partly, with large seed variation. Neither equivalence nor a definitive winner is established. Shared inputs change, preventing a direct single-factor comparison with original flat.

See [MECHANISM.md](MECHANISM.md) for derivations, identifiability limits, and the 480-function closure. Finite input/output evidence cannot uniquely determine internal neural algorithms. No activation interventions or neural concept localization were performed.

## Second independent generator: post hoc replication

Variable-length a/b strings use independently implemented primitives/verifier. Train input lengths 3–6, stress-test 7–8; OOD still has 96 programs × four inputs. Reuse model-proposed macro structures but train separately under new semantics; **this is not zero-shot domain transfer**. Affine reconstruction of every macro is checked over all binary strings of lengths 3–8.

| Condition | Mean IID | OOD seeds 11/22/33 | Mean OOD | Longer-input stress |
|---|---:|---|---:|---:|
{sec_table}

Mean macro−flat difference in this environment is {second['mean_difference']*100:.2f} percentage points. Short strings allow chance-correct answers, so inspect exact primitive sequences and the fraction of programs correct on all four inputs in [second-environment statistics](secondary/analysis/results.json). That fraction is 0% for all flat seeds and 29.17%, 13.54%, 22.92% for macro, so chance matches do not explain all gains. Macro scores only 6.94% on longer-input stress, indicating weak length generalization. This artificial DSL does not substitute for natural code/math tasks.

## Why this is not yet a paper recommendation

Initial self-discovery evidence is weak: one success in 128 inverse-solving attempts; 17 format-valid outputs among 160 proposals, yielding nine distinct nonidentity functions. First lines fail protocol parsing in 132 proposals and 11 have wrong lengths, mixing capability with base-model instruction-format failures. Eight selected positive compression scores are measured against frequencies in traces containing wrong solutions, not actual learning utility.

The nine macros omit ends and generate a closure of only 480 functions. The library is fixed once before training, without showing better useful-abstraction proposals in new domains after iteration. Large-scale base training, natural-task transfer, cross-family replication, and discovery-policy learning comparisons are not yet complete.

Nearby work is close: [Notes to Self](https://arxiv.org/html/2607.20372v1) and [SPEE](https://arxiv.org/html/2608.02139v1) study experience abstraction/internalization; [From Reasoning Traces to Reusable Modules](https://arxiv.org/html/2606.18089v1) studies compositional modules/training interventions; [Your Context Is Not an Array](https://arxiv.org/html/2408.05506v1) studies content-addressing markers/alignment in length generalization. Current macro-label effects do not yet establish a distinct contribution.

**Recommendation: do not expand to large models or costly RL, or frame this round as AI learning innovation. Retain the reproducible separation between module execution and autonomous routing for future topic selection. Continuing requires a question beyond existing content-addressing/routing work and a separate metric for useful abstractions in unseen domains. Further direction awaits review.**

## Failures, verification, and costs

- Retain slow installation/network requests, initial synchronous Tavily failure from earlier smoke checks, frozen-baseline argument launch failures, and inadequate initial test semantic capacity. Chronological revisions: [amendments.md](analysis/amendments.md).
- Frozen no-library baselines often continue text or emit multiple Answer lines and are not strong baselines. Strict whole-line answer audits find no inflated correctness from loose parsing in trained primary groups; see [parser-audit-final.json](analysis/parser-audit-final.json).
- Independently recompute truth, data separation, and actual training-token matching, recording base/adapter SHA256. See [artifact-verification.json](analysis/artifact-verification.json) and second-environment [verification.json](secondary/analysis/verification.json).
- Device reservation estimated from summed job wall time is approximately **{cost['total']:.2f} GPU-hours**, including baselines, interventions, added controls, routing, second environment, discovery, and calibration. It excludes installation/download waits and is not kernel-active time. The original 48–120 GPU-hour estimate was rough; actual short-sequence LoRA screening uses far less. Experiments are not expanded merely to spend the budget. See [compute-cost.json](analysis/compute-cost.json).

## Review and reproduction

- [Complete tables](analysis/RESULT_TABLES.md), [primary statistics](analysis/results.json), [second-environment statistics](secondary/analysis/results.json).
- [Prerun protocol](PROTOCOL.md), [mechanism analysis](MECHANISM.md), [amendments/post hoc declarations](analysis/amendments.md).
- `runs/*/predictions.jsonl` and `secondary/runs/*/predictions.jsonl` contain raw example outputs; run directories retain `config.json`, `train.jsonl`, `summary.json`, and `adapter/`.
- `data/discovery-traces.jsonl` and `data/proposals.jsonl` retain actual solving/proposals including failures; `analysis/routing-probe/` contains all external-routing calls.
- Root `training-env.sh`, `install-training-env.sh`, and `training-requirements.lock.txt` preserve the project environment. Follow README scripts; official EvoSkills remain in the original installation. All new environments, models, caches, and results stay in the root. No paper has been published/submitted.
'''
(ROOT/'REPORT.md').write_text(report)
print('Wrote report',len(report),'characters;',raw_count,'raw records;',cost['total'],'reserved GPU-hours')
