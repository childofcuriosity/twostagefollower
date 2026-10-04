# Supplementary controls and training timeline

These experiments were registered and run after some primary results were known. They are not original preregistered results. Original findings and failures are retained.

## Does missing primitive coverage explain degradation?

The original nine macros omit ends, whereas 31/48 hidden patterns in fresh test families contain ends and 83.11% of test programs use it. This is a substantive confound. A fixed manual coverage intervention replaces brown=inc, inc, inc with ends, inc, inc while preserving other call chains, inputs, and steps. Actual cumulative input and supervised tokens match original macro training exactly for all three seeds.

Primary proposal setting: base 39.01%, original macro 9.06%, restored coverage 12.93%. The fraction of proposals containing ends recovers to 47.53%; restored coverage minus original macro: +3.88 percentage points, family-bootstrap interval -1.32 to +10.76. This mean improvement cannot be claimed as significant recovery, and performance remains well below base. Missing one primitive is therefore insufficient as an explanation, while broader training-distribution narrowness remains possible.

## Candidate stopping-length control

The primary experiment permits lengths 2–3; trained 3B models prefer shorter outputs. The added grammar quota fixes eight length-2 and eight length-3 proposals per family, preserving prompts, T=1, and selection.

| Model | Base | Flat | Macro |
|---|---:|---:|---:|
| qwen1.5b | 38.64% | 4.08% | 14.49% |
| qwen3b | 40.97% | 3.25% | 8.05% |
| smol1.7b | 36.43% | 7.39% | 9.72% |

Complete seed differences and intervals are in [length-results.json](analysis/length-results.json). This is a new decoding condition, not a replacement estimate for the original sampling distribution.

## Complete original-recipe training timeline

Repeat original macro training for three seeds with unchanged optimizer and data order, inserting read-only evaluations at fixed steps without test-based early stopping.

| Optimization step | IID execution | Unseen-composition execution | Fresh-family net proposal compression |
|---|---:|---:|---:|
| 0 | 0.78% | 0.00% | 40.26% |
| 16 | 3.65% | 1.22% | 20.78% |
| 64 | 98.96% | 23.09% | 9.48% |
| 128 | 99.48% | 28.21% | 10.93% |
| 256 | 100.00% | 30.30% | 10.53% |
| 512 | 100.00% | 29.77% | 10.37% |

Final-weight hash agreement with original training by seed: [{"seed": 33, "matches_original_final_weights": true}, {"seed": 22, "matches_original_final_weights": true}, {"seed": 11, "matches_original_final_weights": true}]. Agreement is required to interpret checkpoints as observations from the same deterministic training trajectory.

![Training timeline](figures/training-timecourse.png)

The timeline uses a different proposal-sampling random path from primary robustness jobs. Its final 10.37% net compression and primary-table 9.06% therefore use different proposal samples, despite identical execution tasks and final weights. Proposal utility falls from 40.26% to 20.78% by step 16 and approximately 9.48% by step 64, rather than declining only at the end.

## Original-recipe gradient diagnostics

These probes directly use original-recipe checkpoints and execution data, separately from closed-loop diagnostics in the main report. Each checkpoint uses three fixed minibatches per seed across three seeds. Initialization checkpoints are identical; nine batches do not represent nine independent models.

| Step | Mean gradient cosine | Negative-cosine batches | Proposal surrogate NLL |
|---|---:|---:|---:|
| 0 | +0.0944 | 0/9 | 2.6724 |
| 16 | -0.0470 | 8/9 | 1.1325 |
| 64 | -0.0080 | 5/9 | 1.4112 |
| 128 | -0.0382 | 6/9 | 1.4898 |
| 256 | -0.0427 | 7/9 | 1.4897 |
| 512 | -0.0438 | 8/9 | 1.5311 |

Local gradient conflicts occur at several post-update points, motivating further study of objective interference. At step 16, however, proposal surrogate NLL improves over initialization while sampled utility has already fallen substantially. NLL is therefore not a sufficient utility proxy. Gradient cosine omits the full AdamW-preconditioned update direction and does not establish long-term causal degradation. The loop recipe also exhibits negative cosines without sustained proposal decline; detecting a negative cosine is not itself an RSI bottleneck.

## Degraded-proposer stress intervention

Because closed-loop proposers do not necessarily degrade, an additional intervention uses the demonstrably degraded first-round numeric macro adapter as an external proposer. Learners still start at the same shared round-1 checkpoint, with unchanged support, selector, executor, and 128-step training. Both execution domains receive primitive-sequence proposals from this same source. This tests the total effect of deliberately introducing a degraded proposer, **not spontaneous degradation within a natural loop**.

Positive values favor base/updated sources over legacy. Identical starts make these next-round learning-gain differences.

| Domain | Comparison | Evaluation | Difference (percentage points) | Three seed differences | 95% t interval |
|---|---|---|---:|---|---|
| digits | base-legacy | short | +0.52 | +0.00 / +0.00 / +1.56 | -1.72 to +2.76 |
| digits | base-legacy | family | +6.25 | +0.00 / +10.16 / +8.59 | -7.34 to +19.84 |
| digits | base-legacy | pressure | +6.77 | +0.00 / +12.50 / +7.81 | -8.92 to +22.46 |
| digits | updated-legacy | short | -0.52 | +0.00 / +0.00 / -1.56 | -2.76 to +1.72 |
| digits | updated-legacy | family | +7.03 | +3.12 / +10.94 / +7.03 | -2.67 to +16.73 |
| digits | updated-legacy | pressure | +6.77 | +3.12 / +10.94 / +6.25 | -3.00 to +16.54 |
| strings | base-legacy | short | -3.12 | -3.12 / -6.25 / +0.00 | -10.89 to +4.64 |
| strings | base-legacy | family | +1.82 | -8.59 / +9.38 / +4.69 | -21.33 to +24.98 |
| strings | base-legacy | pressure | +0.52 | -6.25 / +7.81 / +0.00 | -16.98 to +18.02 |
| strings | updated-legacy | short | -1.56 | -4.69 / +0.00 / +0.00 | -8.29 to +5.16 |
| strings | updated-legacy | family | -2.86 | -13.28 / +9.38 / -4.69 | -31.28 to +25.55 |
| strings | updated-legacy | pressure | +2.08 | +1.56 / +9.38 / -4.69 | -15.42 to +19.59 |

Actual macro libraries, training lengths, semantic coverage, and support/held-out program compression by source are in [curriculum-rows.jsonl](analysis/curriculum-rows.jsonl). Proposal sources alter curriculum lengths and training-token counts. These comparisons estimate total effects at equal examples/steps, not pure proposal-quality effects at equal tokens. Abstraction compression P is a candidate proxy; only observed subsequent learning changes G connect it to improvement capability. The two cannot substitute for each other.
