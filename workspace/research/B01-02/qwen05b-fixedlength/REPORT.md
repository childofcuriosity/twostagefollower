# Qwen2.5-0.5B fixed-length in-domain label replication

Completed 2026-09-27/28. The question is whether emitting current tool identity before each operation segment improves strict complete-trajectory success when training and testing **both contain exactly L calls**. Inputs supply four digits and a tool chain; the model emits primitives and intermediate states by tool, then `Answer`. No out-of-domain long-sequence or prompt-only controls were run.

## Main results

Exploration followed registered L=10,15,20,25,30 and five-step extensions 35,40. L40 first met the candidate criterion: STEP in 10%–90%, original names at least five points higher, and at least 2/3 seeds improving. **L40 was selected from exploration.** Formal replication uses the prespecified 20 new seeds 200–219 and 512 newly generated tests disjoint from exploration. Four conditions share the same underlying L40 training and formal-test examples.

| Label, ordered by information presentation | Formal L40 strict success, 20-seed mean ± sample SD | Same-seed difference from STEP, mean ± SD | Improved seeds |
|---|---:|---:|---:|
| Uniform step | 72.01% ± 10.76% | Baseline | — |
| Position index | 19.33% ± 23.46% | −52.69 ± 26.39 percentage points | 2/20 |
| Fixed alias | 99.67% ± 0.25% | +27.66 ± 10.77 percentage points | 20/20 |
| Original tool name | 99.69% ± 0.27% | +27.68 ± 10.70 percentage points | 20/20 |

Descriptive paired-seed t intervals (df=19): fixed alias versus STEP **+22.62 to +32.70** points, original names **+22.67 to +32.69**, and position indices **−65.03 to −40.34**. Intervals cover training-seed variation only, with one training set, test set, mapping, and selected length. The 0.02-point alias/original-name gap does not distinguish the two identity word forms.

### Complete exploration record

Each level uses 4096 training and 512 exploratory test examples with exactly L calls. STEP and original names each have three paired seeds (11,22,33).

| L | STEP mean | Original-name mean | Original−STEP |
|---:|---:|---:|---:|
| 10 | 99.93% | 100.00% | +0.07 percentage points |
| 15 | 100.00% | 100.00% | 0.00 percentage points |
| 20 | 98.89% | 99.67% | +0.78 percentage points |
| 25 | 99.02% | 99.35% | +0.33 percentage points |
| 30 | 96.48% | 99.80% | +3.32 percentage points |
| 35 | 92.90% | 99.93% | +7.03 percentage points |
| 40 | 74.02% | 98.96% | +24.93 percentage points |

L40 exploratory STEP-s11 and original-name-s11 ran out of memory near step 20 under microbatch16/accum2. Failed files remain. Both completed in new `-retry1` directories with microbatch8/accum4; the other four retained 16/2. Exploratory L40 mixes implementations and serves only length selection. All 80 formal runs **uniformly use 8/4**, preserving effective batch 32.

## Inherited settings and changes

Inherited: official Qwen2.5-0.5B Base revision `060db6499f32faf8b98477b0a26969ef7d8b9987`, nine tools/four-digit operations, input/output templates, fixed alias mapping, LoRA r16/alpha32/dropout0 across seven projections, AdamW, original 3e-4 schedule, 512 steps, 16,384 example presentations per run, greedy decoding, and old strict trajectory scoring. Underlying training/test examples are paired across conditions.

Here, every chain has exactly L calls, with independently uniform tool and digit draws. There are 4096 training and 512 test examples, deduplicated by chain/input. Formal L40 shares exploratory training data but uses fresh tests with zero training/exploration overlap. Formal seeds 200–219 are disjoint from exploratory 11/22/33. All formal L40 training capacity assertions and `max_new_tokens` are 1536, fitting correct targets. Memory adjustment is uniformly microbatch8/accum4, without changing steps/effective batch. Input/target lengths still differ by label; token lengths are not matched.

## Error and cost audits

Counts below use 20×512=10,240 formal outputs per label; categories can overlap. Missing/extra tools compare output header-segment count to the required 40. Expansion errors use the first primitive-sequence mismatch under the old strict scorer. Arithmetic is checked against emitted intermediate states. Generation-cap counts include outputs reaching 1536 tokens.

| Label | Missing tools | Extra tools | Expansion errors | Arithmetic errors | Generation cap | Mean output tokens/example |
|---|---:|---:|---:|---:|---:|---:|
| Uniform step | 19 | 94 | 2,842 | 15 | 0 | 1,112.18 |
| Position index | 2 | 0 | 8,256 | 25 | 0 | 1,182.34 |
| Fixed alias | 18 | 14 | 31 | 0 | 0 | 1,151.37 |
| Original tool name | 9 | 23 | 31 | 0 | 0 | 1,111.37 |

Position labels almost always produce 40 headers but frequently expand the wrong operations. Correct segment counts alone do not establish complete execution. Both identity labels substantially improve fixed-length in-domain success on this task, but identity information is not uniquely identified: word forms, input/output tokenization, and supervised lengths differ. Fixed synthetic tool composition does not establish real-agent benefits or internal attention mechanisms.

All 80 formal runs exited 0 with 512 steps, 16,384 examples, identical model revision, and finite losses. The old strict scorer evaluated 40,960 raw outputs. Label-aware rescoring gives identical group success counts: 7,374 / 1,979 / 10,206 / 10,208. Training, exploration, and formal-test chain/input pairs are unique within and disjoint across sets. Training/formal-test hashes are `75640d4ffae269e6eec061318c30ac36027152afcd2182752cf744374fb27038` and `db9b546831cc923c14a3c934b9bcfc401cd71d271039d9fa5a15fa7e47c92ea4`. Summed outer formal-job duration is **22.98 allocated GPU-hours**, including loading, training, inference, and saving, not kernel-active time. Only the eight local `.69` PRO6000 GPUs were used; memory was idle at completion.

## Evidence

- Prerun rules, candidate freeze, memory adjustment, and resource changes: `REGISTRATION.md`.
- Data/capacity manifests: `data/L40/explore-manifest.json`, `data/L40/formal/formal-manifest.json`; all lengths retained under `data/L*/`.
- Formal seed scores, paired differences, errors, tokens, and time: `analysis/scores-formal-L40.json`; example-level strict scores: `analysis/graded-formal-L40.jsonl`.
- Exploration: `analysis/scores-explore-L*.json`; L40 failures and retries in corresponding `runs/explore-L40-*-s11/` and `-retry1/` directories.
- Raw outputs, logs, adapters, configurations, and source snapshots: `runs/formal-L40-{condition}-s{seed}/`. Dispatch exits: `analysis/dispatch-formal-L40-flat-position-alias-macro.json`.

Prompt-only controls, real-task extensions, and paper submission remain later-stage work; none was launched here.
