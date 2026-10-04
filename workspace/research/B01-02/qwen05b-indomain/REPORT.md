# Qwen2.5-0.5B in-domain label replication

Completed 2026-09-27 UTC. All evaluations use lengths supported by training. This round includes neither out-of-domain long sequences nor prompt-only controls.

## Research question and conclusion

Given four digits and a tool-call order, the model emits primitive operations, every intermediate state, and the final `Answer`. Strict success requires the complete correct operation sequence, all intermediate numbers, and the answer. Original 1.5B short-task scores were near perfect; this study tests whether the smaller same-family 0.5B model and progressively longer training tasks provide room for in-domain improvement.

**Main observation:** Maximum training length five first meets the revised, prespecified headroom threshold. Fixed aliases and original names outperform uniform step by 10.92 and 11.10 percentage points, respectively, with positive differences for all 20 paired seeds. Position indices score 6.23 points below step. **Differences concentrate at one/two calls; all four groups score 100% at four/five calls.** Evidence supports reduced short-task degradation under this sampling scheme, rather than better execution of five-call tasks themselves.

## Inherited settings

- Official Qwen2.5 Base; existing LoRA r16/alpha32/dropout0 and seven projection types; AdamW, LR 3e-4, and the original schedule. Use 512 optimization steps, microbatch 16 with accumulation 2, and 16384 example presentations per run. No test-based checkpoint selection.
- Fixed nine tools, four-digit operations, original prompt, Answer termination protocol, four label input/output formats, and fixed alias mapping. Label order: uniform step, position index, fixed alias, original tool name.
- Twenty paired training seeds: 11, 22, 33, and 100–116. A shared seed controls LoRA initialization and example shuffling. Greedy decoding, batch 32, and the existing strict complete-trajectory scorer.
- Maximum length two reuses the original 4096 training examples and 128 short IID tests verbatim. Existing models and historical results remain unchanged.

## Changes and freeze order

- The only model change is to `Qwen/Qwen2.5-0.5B` Base, revision `060db6499f32faf8b98477b0a26969ef7d8b9987`. Model/data hashes are in `analysis/delivery-audit.json` and length-specific manifests.
- The user rejected the original 99% saturation threshold before running. Before any 0.5B result, it was replaced by STEP mean strict success ≤90% across 20 seeds, with at least 15 seeds individually ≤95%. Original text and amendment remain in `REGISTRATION.md`. This identifies error headroom without guaranteeing identity-label gains.
- Freeze 4096 training examples separately for maximum lengths 3–5. Extend the original uniform-over-chains generator to lengths 1–L, with uniform digits and chain/input deduplication. Data seeds are 903/904/905. Retain the original 128 short tests and add 128 for each new length. L5 has 512 tests shared by all labels within each seed. Evaluate only training-supported lengths.
- Maximum L5 training target length is 269 tokens, exceeding the old 256-token assertion. Raise only that assertion to 512. Generation `max_new_tokens=256`, greedy decoding, parsing, and scoring are unchanged. Lengths 2–4 require no compatibility adjustment.

## STEP screening

| Maximum training call length | Test examples/seed | STEP mean ± seed sample SD | Decision |
|---:|---:|---:|---|
| 2 | 128 | 100.00% ± 0.00% | Still saturated; extend |
| 3 | 256 | 100.00% ± 0.00% | Still saturated; extend |
| 4 | 384 | 99.18% ± 0.13% | Still saturated; extend |
| 5 | 512 | 88.56% ± 3.35% | Headroom found; stop extending |

Length five first meets the threshold, so maximum lengths 6–8 were not trained. This baseline-based difficulty selection cannot be interpreted as a confirmatory analysis of a task fixed independently of selection or as post hoc selection for positive label results.

## Four-label primary comparison at maximum length five

| Output label | In-domain strict trajectory success, 20-seed mean ± SD | Paired difference from step, mean ± SD | Improved paired seeds |
|---|---:|---:|---:|
| Uniform step | 88.56% ± 3.35% | Baseline | — |
| Position index | 82.33% ± 4.96% | -6.23 ± 6.43 percentage points | 4/20 |
| Fixed alias | 99.48% ± 0.31% | +10.92 ± 3.41 percentage points | 20/20 |
| Original tool name | 99.67% ± 0.41% | +11.10 ± 3.34 percentage points | 20/20 |

Descriptive t intervals for paired seed differences (df=19): fixed alias versus STEP +9.32 to +12.52 points; original name +9.54 to +12.67; position index −9.24 to −3.22. Training data, test examples, and alias mapping are fixed. Intervals cover training-seed variation, not task or mapping variation.

### By call length

| Calls | Examples/seed | Uniform step | Position index | Fixed alias | Original name |
|---:|---:|---:|---:|---:|---:|
| 1 | 11 | 5.91% | 0.00% | 77.73% | 86.82% |
| 2 | 117 | 59.87% | 34.74% | 99.83% | 99.79% |
| 3 | 128 | 99.02% | 97.58% | 100.00% | 100.00% |
| 4 | 128 | 100.00% | 100.00% | 100.00% | 100.00% |
| 5 | 128 | 100.00% | 100.00% | 100.00% | 100.00% |

Length-specific denominators repeat the same examples across 20 seeds: 220 one-call outputs, 2340 two-call outputs, and 2560 at each other length. These are not independent fresh examples.

### Strict success by training seed

| Seed | Uniform step | Position index | Fixed alias | Original name | Alias−step | Original−step |
|---:|---:|---:|---:|---:|---:|---:|
| 11 | 88.87% | 77.54% | 99.41% | 99.22% | +10.55 | +10.35 |
| 22 | 89.65% | 90.23% | 99.41% | 100.00% | +9.77 | +10.35 |
| 33 | 84.96% | 78.71% | 100.00% | 99.22% | +15.04 | +14.26 |
| 100 | 92.38% | 83.59% | 99.02% | 100.00% | +6.64 | +7.62 |
| 101 | 88.87% | 80.08% | 99.61% | 100.00% | +10.74 | +11.13 |
| 102 | 85.74% | 82.42% | 99.41% | 100.00% | +13.67 | +14.26 |
| 103 | 90.43% | 75.00% | 99.22% | 98.63% | +8.79 | +8.20 |
| 104 | 90.04% | 75.98% | 99.41% | 100.00% | +9.38 | +9.96 |
| 105 | 89.65% | 86.72% | 99.61% | 99.41% | +9.96 | +9.77 |
| 106 | 90.04% | 86.52% | 99.80% | 100.00% | +9.77 | +9.96 |
| 107 | 89.06% | 89.84% | 100.00% | 100.00% | +10.94 | +10.94 |
| 108 | 86.52% | 88.67% | 99.80% | 99.02% | +13.28 | +12.50 |
| 109 | 88.48% | 78.52% | 99.22% | 99.61% | +10.74 | +11.13 |
| 110 | 77.93% | 88.09% | 99.22% | 99.61% | +21.29 | +21.68 |
| 111 | 83.98% | 77.54% | 99.61% | 100.00% | +15.62 | +16.02 |
| 112 | 91.60% | 77.34% | 99.02% | 100.00% | +7.42 | +8.40 |
| 113 | 91.02% | 78.12% | 99.22% | 99.41% | +8.20 | +8.40 |
| 114 | 90.43% | 81.64% | 99.22% | 99.80% | +8.79 | +9.38 |
| 115 | 91.21% | 83.20% | 100.00% | 99.41% | +8.79 | +8.20 |
| 116 | 90.43% | 86.91% | 99.41% | 100.00% | +8.98 | +9.57 |

## Data/scoring audits and interpretation limits

- The 4096 L5 training examples contain only 1/4/40/379/3672 examples at 1/2/3/4/5 calls, respectively. This follows directly from uniform sampling over all chains of length ≤L. Sparse short-task exposure may explain degradation of STEP and position indices, but the design does not independently test that mechanism.
- Training/test chain-input pairs do not overlap. Tests retain 128 old short examples and add 128 each at 3/4/5 calls. Removing headers yields identical operations and Answer targets across all L5 labels. Fixed aliases apply to both inputs and outputs.
- All 80 formal runs have 512 steps, 16384 example presentations, and identical model revision/trainable LoRA parameter count. All 40960 raw in-domain outputs are retained individually. The old scorer checks complete trajectories without requiring correct headers; a label-aware recheck yields identical strict success counts at every length.
- Differences mainly involve extra tool execution. For L5-trained STEP, the 207/939 failed one-/two-call seed outputs all have operation-sequence mismatches, with zero intermediate arithmetic errors. Position labels often continue with extra steps on short tasks. These observations do not identify internal mechanisms.
- Every group is perfect at four/five calls, so this round cannot establish identity-label improvements there; more seeds cannot create headroom at saturated lengths. L5 training is overwhelmingly five-call data, making short-task reliability a retention question under changed distribution weights.
- Only one training dataset, test set, and fixed alias mapping are used. Aliases and original names differ in input tokens and target lengths. Seed consistency does not establish consistency across mappings, datasets, or real-agent tasks. One-call training contains only one example and is not a well-learned one-call distribution.

## Costs and evidence

- Recorded post-loading GPU allocation for the 80 formal L5 runs totals 3.59 hours (sum of run durations, including inference/saving). Twenty STEP runs each at L2/3/4 are also complete. Outer durations for all 140 jobs total approximately 6.05 allocated GPU-hours, including loading and environment overhead. Eight local PRO6000 GPUs were used; all memory was empty at completion.
- Registration/amendments: `REGISTRATION.md`; data manifests: `data/L3/manifest.json`, `data/L4/manifest.json`, `data/L5/manifest.json`; seed/paired results: `analysis/scores-L5.json`; full original scores: `analysis/graded-L5.jsonl`; audit: `analysis/delivery-audit.json`.
- Runs are in `runs/L5-{condition}-s{seed}/`, retaining driver snapshots, configurations, 512-step logs, adapters, raw `predictions.jsonl`, `summary.json`, and completion markers. Dispatch exits: `analysis/dispatch-L5-*.json`.

Prompt-only controls and real-execution extensions remain future notes; neither was launched.
