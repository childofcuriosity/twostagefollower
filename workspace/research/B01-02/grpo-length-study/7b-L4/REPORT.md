# B01-02: label comparison under binary-reward GRPO

Qwen2.5-7B-Instruct at the original revision, fixed L4; the nine tools and STEP/NAME prompts match the previous study; BF16 base + LoRA, with no additional SFT. Reward is strict full-trajectory 0/1, with no heading reward. Each of 6 runs has 100 updates, using 16 examples x 8 candidates per update.

## Fresh test endpoints (512 examples)

| seed | STEP step0 to 100 | STEP gain | NAME step0 to 100 | NAME gain | NAME-STEP endpoint difference |
|---:|---:|---:|---:|---:|---:|
| 301 | 0.78%→0.78% | +0.00 pp | 2.93%→3.91% | +0.98 pp | +3.12 pp |
| 302 | 0.78%→0.98% | +0.20 pp | 2.93%→4.10% | +1.17 pp | +3.12 pp |
| 303 | 0.78%→0.98% | +0.20 pp | 2.93%→4.49% | +1.56 pp | +3.52 pp |

STEP: step100 = 0.91% ± 0.11% (3-seed mean +/- sample SD); mean gain over the condition-specific step0 = +0.13 percentage points.

NAME: step100 = 4.17% ± 0.30% (3-seed mean +/- sample SD); mean gain over the condition-specific step0 = +1.24 percentage points.

Mean paired NAME-STEP endpoint difference: +3.26 ± 0.23 percentage points; 3/3 seeds are positive. Mean difference in learning gains: +1.11 percentage points. Three seeds provide preliminary replication; seed x example counts are not treated as many independent model replications.

step0 uses the same original policy: fresh validation/test outputs are generated once per condition and explicitly referenced by three seeds. Each run retains its own paired LoRA initialization checkpoint. The fresh test set is scored only at the scheduled step0 and 100, with no best-checkpoint selection.

## Validation thresholds and complete learning curves

| Condition | seed | First 60% | First 70% | First 80% | First 90% | Mean curve success (trapezoidal area/100) |
|---|---:|---:|---:|---:|---:|---:|
| STEP | 301 | Not reached | Not reached | Not reached | Not reached | 0.90% |
| NAME | 301 | Not reached | Not reached | Not reached | Not reached | 4.53% |
| STEP | 302 | Not reached | Not reached | Not reached | Not reached | 0.82% |
| NAME | 302 | Not reached | Not reached | Not reached | Not reached | 4.41% |
| STEP | 303 | Not reached | Not reached | Not reached | Not reached | 1.00% |
| NAME | 303 | Not reached | Not reached | Not reached | Not reached | 4.28% |

Thresholds record the first fixed evaluation point at step0/10/.../100 that reaches the target. Exact crossing times between checkpoints are not inferred, and unreached thresholds receive no arbitrary update count. Complete per-seed curves and actual training tokens/GPU time at every point are in analysis/results.json.

![Validation success by update](figures/validation-vs-updates.png)

![Validation success by actual compute](figures/validation-vs-compute.png)

## Sampling, optimization, and costs

| Condition | seed | Candidates | Output tokens | Mixed-reward group fraction | Duplicate candidate fraction | Maximum KL | Training-segment GPU-hours |
|---|---:|---:|---:|---:|---:|---:|---:|
| STEP | 301 | 12800 | 1513663 | 0.94% | 9.59% | 0.01920 | 1.842 |
| NAME | 301 | 12800 | 1480897 | 5.25% | 15.80% | 0.25310 | 1.767 |
| STEP | 302 | 12800 | 1517688 | 0.69% | 8.88% | 0.00549 | 1.832 |
| NAME | 302 | 12800 | 1486521 | 3.94% | 14.85% | 0.01553 | 1.763 |
| STEP | 303 | 12800 | 1515677 | 1.00% | 9.23% | 0.00854 | 1.831 |
| NAME | 303 | 12800 | 1474478 | 5.06% | 16.02% | 0.00994 | 1.774 |

Duplicate fractions are measured within the 8 outputs for each example. All-0/all-1 groups are retained with zero task advantage, though KL gradients may remain. Equal update budgets do not imply equal compute. Compute curves accumulate sampling and update wall time across both ranks. Training-segment GPU time is run wall time after NCCL initialization x2, including model loading, saving, and waiting, but excluding earlier process/NCCL startup; it is not active GPU-kernel time. Full job occupancy, evaluation, and precheck/recovery costs are listed separately in the combined cost audit. These nested timings must not be added together.

## Headings, errors, and stopping reasons (step100 fresh test)

| Condition | seed | Fully compliant headings | Operation-sequence mismatch | Numerical error | Early prefix stop | Extra raw operations | Extra format lines | Truncation |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| STEP | 301 | 68.16% | 452 | 467 | 40 | 183 | 19 | 0 |
| NAME | 301 | 87.11% | 318 | 450 | 51 | 75 | 30 | 0 |
| STEP | 302 | 68.55% | 456 | 467 | 36 | 179 | 16 | 0 |
| NAME | 302 | 87.70% | 301 | 457 | 47 | 74 | 21 | 0 |
| STEP | 303 | 66.21% | 453 | 471 | 48 | 170 | 18 | 0 |
| NAME | 303 | 89.65% | 290 | 455 | 38 | 68 | 23 | 0 |

Error flags can overlap. Numerical errors are checked against the preceding output state; expansion mismatches include extra/missing operations. Extra raw operations are not directly counted as extra tool calls. Heading compliance is reported separately and excluded from binary rewards. Per-example raw outputs, token IDs, and EOS/cap evidence are retained in eval/outputs/.

## Evidence and scope of interpretation

Frozen configurations: config/frozen.json and freeze-manifest.json; data: data/manifest.json; prechecks: analysis/precheck-complete.json; fixed checkpoints and candidates: runs/v1-*; complete curves/pairing/costs: analysis/results.json. Implementation definitions are in the parent REGISTRATION.md. See the parent REPORT.md and COMPLETION_AUDIT.md for combined interpretation and acceptance checks.

This study compares whether label structure helps train execution under a supplied plan. It adds no internal/local rewards and does not establish transfer to real mathematics or agents, cross-model generalization, or novelty. Method gains are distinguished from hypotheses about internal mechanisms.

See [CASE_REVIEW.md](CASE_REVIEW.md) for supplementary mutually exclusive error categories, heading boundaries, and raw/reference trajectory examples. These categories interpret outputs without changing scores; heading noncompliance is distinct from tool-identity error.
