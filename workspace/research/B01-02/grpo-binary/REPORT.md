# B01-02: label comparison under binary-reward GRPO

Qwen2.5-14B-Instruct at the original revision, fixed L2; the nine tools and STEP/NAME prompts match the previous study; BF16 base + LoRA, with no additional SFT. Reward is strict full-trajectory 0/1, with no heading reward. Each of 6 runs has 100 updates, using 16 examples x 8 candidates per update.

## Fresh test endpoints (512 examples)

| seed | STEP step0 to 100 | STEP gain | NAME step0 to 100 | NAME gain | NAME-STEP endpoint difference |
|---:|---:|---:|---:|---:|---:|
| 301 | 51.17%→97.46% | +46.29 pp | 49.61%→99.41% | +49.80 pp | +1.95 pp |
| 302 | 51.17%→99.61% | +48.44 pp | 49.61%→98.83% | +49.22 pp | -0.78 pp |
| 303 | 51.17%→99.22% | +48.05 pp | 49.61%→99.22% | +49.61 pp | +0.00 pp |

STEP: step100 = 98.76% ± 1.14% (3-seed mean +/- sample SD); mean gain over the condition-specific step0 = +47.59 percentage points.

NAME: step100 = 99.15% ± 0.30% (3-seed mean +/- sample SD); mean gain over the condition-specific step0 = +49.54 percentage points.

Mean paired NAME-STEP endpoint difference: +0.39 ± 1.41 percentage points; 1/3 seeds are positive. Mean difference in learning gains: +1.95 percentage points. Three seeds provide preliminary replication; seed x example counts are not treated as many independent model replications.

step0 uses the same original policy: fresh validation/test outputs are generated once per condition and explicitly referenced by three seeds. Each run retains its own paired LoRA initialization checkpoint. The fresh test set is scored only at the scheduled step0 and 100, with no best-checkpoint selection.

## Validation thresholds and complete learning curves

| Condition | seed | First 60% | First 70% | First 80% | First 90% | Mean curve success (trapezoidal area/100) |
|---|---:|---:|---:|---:|---:|---:|
| STEP | 301 | 20 | 30 | 40 | 50 | 82.46% |
| NAME | 301 | 20 | 20 | 30 | 40 | 87.30% |
| STEP | 302 | 30 | 30 | 40 | 40 | 85.33% |
| NAME | 302 | 20 | 20 | 30 | 40 | 86.88% |
| STEP | 303 | 20 | 30 | 30 | 40 | 85.25% |
| NAME | 303 | 20 | 30 | 30 | 40 | 86.80% |

Thresholds record the first fixed evaluation point at step0/10/.../100 that reaches the target. Exact crossing times between checkpoints are not inferred, and unreached thresholds receive no arbitrary update count. Complete per-seed curves and actual training tokens/GPU time at every point are in analysis/results.json.

![Validation success by update](figures/validation-vs-updates.png)

![Validation success by actual compute](figures/validation-vs-compute.png)

## Sampling, optimization, and costs

| Condition | seed | Candidates | Output tokens | Mixed-reward group fraction | Duplicate candidate fraction | Maximum KL | Allocated training GPU-hours |
|---|---:|---:|---:|---:|---:|---:|---:|
| STEP | 301 | 12800 | 852147 | 17.56% | 82.65% | 0.67958 | 2.314 |
| NAME | 301 | 12800 | 852997 | 14.25% | 75.77% | 0.08572 | 2.349 |
| STEP | 302 | 12800 | 849840 | 13.94% | 83.27% | 0.17419 | 2.303 |
| NAME | 302 | 12800 | 848139 | 16.19% | 76.36% | 0.30949 | 2.334 |
| STEP | 303 | 12800 | 849667 | 14.25% | 83.48% | 0.15370 | 2.310 |
| NAME | 303 | 12800 | 849794 | 14.50% | 76.45% | 0.10238 | 2.339 |

Duplicate fractions are measured within the 8 outputs for each example. All-0/all-1 groups are retained with zero task advantage, though KL gradients may remain. Equal update budgets do not imply equal compute. Compute curves accumulate sampling and update wall time across both ranks. Allocated training GPU time additionally includes loading, saving, and waiting; it is not active GPU-kernel time. Evaluation and precheck/recovery costs must be listed separately in the completion audit.

## Headings, errors, and stopping reasons (step100 fresh test)

| Condition | seed | Fully compliant headings | Operation-sequence mismatch | Numerical error | Early prefix stop | Extra raw operations | Extra format lines | Truncation |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| STEP | 301 | 100.00% | 0 | 12 | 0 | 0 | 0 | 0 |
| NAME | 301 | 100.00% | 0 | 3 | 0 | 0 | 0 | 0 |
| STEP | 302 | 100.00% | 1 | 1 | 0 | 0 | 0 | 0 |
| NAME | 302 | 90.43% | 0 | 6 | 0 | 0 | 0 | 0 |
| STEP | 303 | 100.00% | 0 | 4 | 0 | 0 | 0 | 0 |
| NAME | 303 | 99.22% | 0 | 4 | 0 | 0 | 0 | 0 |

Error flags can overlap. Numerical errors are checked against the preceding output state; expansion mismatches include extra/missing operations. Extra raw operations are not directly counted as extra tool calls. Heading compliance is reported separately and excluded from binary rewards. Per-example raw outputs, token IDs, and EOS/cap evidence are retained in eval/outputs/.

## Evidence and scope of interpretation

Frozen configurations: config/frozen.json and freeze-manifest.json; data: data/manifest.json; prechecks: analysis/precheck-complete.json; fixed checkpoints and candidates: runs/v1-*; complete curves/pairing/costs: analysis/results.json; implementation definitions: METHOD.md. See [CONCLUSIONS.md](CONCLUSIONS.md) for final interpretation and [COMPLETION_AUDIT.md](COMPLETION_AUDIT.md) for complete checks and cost accounting.

This study compares whether label structure helps train execution under a supplied plan. It adds no internal/local rewards and does not establish transfer to real mathematics or agents, cross-model generalization, or novelty. Method gains are distinguished from hypotheses about internal mechanisms.

## Error changes throughout training (fixed validation set)

The figure covers every prespecified checkpoint. Curves show the mean error-flag fractions over 3 seeds. Flags can overlap. A numerical error means that the current raw operation is computed incorrectly given the preceding output state. Numerical errors and tool-expansion/order errors are counted separately and must not be added into a total error rate.

![Complete error curves](figures/validation-error-curves.png)

| Update | STEP expansion errors/256 | NAME expansion errors/256 | STEP numerical errors/256 | NAME numerical errors/256 | STEP heading compliance | NAME heading compliance |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 59.00 | 39.00 | 84.00 | 112.00 | 100.00% | 97.27% |
| 10 | 56.33 | 33.00 | 77.33 | 102.33 | 99.48% | 97.14% |
| 20 | 46.00 | 7.00 | 62.00 | 68.00 | 99.09% | 94.79% |
| 30 | 13.67 | 2.67 | 39.00 | 35.67 | 99.87% | 92.97% |
| 40 | 3.33 | 2.00 | 23.67 | 15.67 | 100.00% | 92.06% |
| 50 | 1.67 | 0.67 | 13.67 | 7.33 | 100.00% | 90.10% |
| 60 | 1.00 | 0.00 | 8.33 | 3.00 | 100.00% | 91.41% |
| 70 | 0.33 | 0.00 | 6.33 | 3.00 | 100.00% | 93.23% |
| 80 | 0.33 | 0.00 | 4.33 | 2.33 | 100.00% | 96.22% |
| 90 | 0.33 | 0.33 | 4.00 | 2.33 | 100.00% | 95.70% |
| 100 | 0.67 | 0.33 | 2.33 | 2.67 | 100.00% | 97.92% |

All error flags, EOS/truncation information, and per-seed raw data are in analysis/results.json, analysis/error-curves.json, and eval/outputs.

See [CASE_REVIEW.md](CASE_REVIEW.md) for supplementary heading and final-Answer checks: all 53 NAME endpoint heading violations are extra `Trace:` headings, with correct tool names and order. STEP seed301 also has 1 case with entirely correct intermediate states but an incorrectly copied final Answer. The primary score is unchanged.
