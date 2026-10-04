# B01-02: label comparison under binary-reward GRPO

Qwen2.5-14B-Instruct at the original revision, fixed L5; the nine tools and STEP/NAME prompts match the previous study; BF16 base + LoRA, with no additional SFT. Reward is strict full-trajectory 0/1, with no heading reward. Each of 6 runs has 100 updates, using 16 examples x 8 candidates per update.

## Fresh test endpoints (512 examples)

| seed | STEP step0 to 100 | STEP gain | NAME step0 to 100 | NAME gain | NAME-STEP endpoint difference |
|---:|---:|---:|---:|---:|---:|
| 301 | 5.47%→24.41% | +18.95 pp | 10.55%→53.71% | +43.16 pp | +29.30 pp |
| 302 | 5.47%→32.23% | +26.76 pp | 10.55%→78.32% | +67.77 pp | +46.09 pp |
| 303 | 5.47%→42.19% | +36.72 pp | 10.55%→80.27% | +69.73 pp | +38.09 pp |

STEP: step100 = 32.94% ± 8.91% (3-seed mean +/- sample SD); mean gain over the condition-specific step0 = +27.47 percentage points.

NAME: step100 = 70.77% ± 14.80% (3-seed mean +/- sample SD); mean gain over the condition-specific step0 = +60.22 percentage points.

Mean paired NAME-STEP endpoint difference: +37.83 ± 8.40 percentage points; 3/3 seeds are positive. Mean difference in learning gains: +32.75 percentage points. Three seeds provide preliminary replication; seed x example counts are not treated as many independent model replications.

step0 uses the same original policy: fresh validation/test outputs are generated once per condition and explicitly referenced by three seeds. Each run retains its own paired LoRA initialization checkpoint. The fresh test set is scored only at the scheduled step0 and 100, with no best-checkpoint selection.

## Validation thresholds and complete learning curves

| Condition | seed | First 60% | First 70% | First 80% | First 90% | Mean curve success (trapezoidal area/100) |
|---|---:|---:|---:|---:|---:|---:|
| STEP | 301 | Not reached | Not reached | Not reached | Not reached | 16.15% |
| NAME | 301 | Not reached | Not reached | Not reached | Not reached | 34.08% |
| STEP | 302 | Not reached | Not reached | Not reached | Not reached | 10.92% |
| NAME | 302 | 70 | 90 | Not reached | Not reached | 41.13% |
| STEP | 303 | Not reached | Not reached | Not reached | Not reached | 17.25% |
| NAME | 303 | 70 | 80 | Not reached | Not reached | 44.71% |

Thresholds record the first fixed evaluation point at step0/10/.../100 that reaches the target. Exact crossing times between checkpoints are not inferred, and unreached thresholds receive no arbitrary update count. Complete per-seed curves and actual training tokens/GPU time at every point are in analysis/results.json.

![Validation success by update](figures/validation-vs-updates.png)

![Validation success by actual compute](figures/validation-vs-compute.png)

## Sampling, optimization, and costs

| Condition | seed | Candidates | Output tokens | Mixed-reward group fraction | Duplicate candidate fraction | Maximum KL | Training-segment GPU-hours |
|---|---:|---:|---:|---:|---:|---:|---:|
| STEP | 301 | 12800 | 1962589 | 19.50% | 43.24% | 0.27417 | 3.832 |
| NAME | 301 | 12800 | 1902796 | 30.06% | 55.88% | 0.38294 | 3.645 |
| STEP | 302 | 12800 | 1967216 | 15.50% | 40.62% | 0.08399 | 3.796 |
| NAME | 302 | 12800 | 1902983 | 27.31% | 59.50% | 0.14438 | 3.631 |
| STEP | 303 | 12800 | 1943132 | 21.69% | 43.40% | 0.13106 | 3.754 |
| NAME | 303 | 12800 | 1906171 | 30.38% | 59.30% | 10.13671 | 3.623 |

Duplicate fractions are measured within the 8 outputs for each example. All-0/all-1 groups are retained with zero task advantage, though KL gradients may remain. Equal update budgets do not imply equal compute. Compute curves accumulate sampling and update wall time across both ranks. Training-segment GPU time is run wall time after NCCL initialization x2, including model loading, saving, and waiting, but excluding earlier process/NCCL startup; it is not active GPU-kernel time. Full job occupancy, evaluation, and precheck/recovery costs are listed separately in the combined cost audit. These nested timings must not be added together.

## Headings, errors, and stopping reasons (step100 fresh test)

| Condition | seed | Fully compliant headings | Operation-sequence mismatch | Numerical error | Early prefix stop | Extra raw operations | Extra format lines | Truncation |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| STEP | 301 | 96.48% | 266 | 228 | 17 | 194 | 17 | 1 |
| NAME | 301 | 93.16% | 52 | 208 | 16 | 19 | 0 | 0 |
| STEP | 302 | 97.66% | 211 | 224 | 26 | 126 | 4 | 0 |
| NAME | 302 | 94.92% | 45 | 71 | 15 | 16 | 0 | 0 |
| STEP | 303 | 96.88% | 114 | 236 | 21 | 43 | 2 | 0 |
| NAME | 303 | 97.07% | 54 | 57 | 10 | 36 | 0 | 0 |

Error flags can overlap. Numerical errors are checked against the preceding output state; expansion mismatches include extra/missing operations. Extra raw operations are not directly counted as extra tool calls. Heading compliance is reported separately and excluded from binary rewards. Per-example raw outputs, token IDs, and EOS/cap evidence are retained in eval/outputs/.

## Evidence and scope of interpretation

Frozen configurations: config/frozen.json and freeze-manifest.json; data: data/manifest.json; prechecks: analysis/precheck-complete.json; fixed checkpoints and candidates: runs/v1-*; complete curves/pairing/costs: analysis/results.json. Implementation definitions are in the parent REGISTRATION.md. See the parent REPORT.md and COMPLETION_AUDIT.md for combined interpretation and acceptance checks.

This study compares whether label structure helps train execution under a supplied plan. It adds no internal/local rewards and does not establish transfer to real mathematics or agents, cross-model generalization, or novelty. Method gains are distinguished from hypotheses about internal mechanisms.

See [CASE_REVIEW.md](CASE_REVIEW.md) for supplementary mutually exclusive error categories, heading boundaries, and raw/reference trajectory examples. These categories interpret outputs without changing scores; heading noncompliance is distinct from tool-identity error.
