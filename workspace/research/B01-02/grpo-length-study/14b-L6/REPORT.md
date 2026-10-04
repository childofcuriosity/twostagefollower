# B01-02: label comparison under binary-reward GRPO

Qwen2.5-14B-Instruct at the original revision, fixed L6; the nine tools and STEP/NAME prompts match the previous study; BF16 base + LoRA, with no additional SFT. Reward is strict full-trajectory 0/1, with no heading reward. Each of 6 runs has 100 updates, using 16 examples x 8 candidates per update.

## Fresh test endpoints (512 examples)

| seed | STEP step0 to 100 | STEP gain | NAME step0 to 100 | NAME gain | NAME-STEP endpoint difference |
|---:|---:|---:|---:|---:|---:|
| 301 | 2.93%→4.10% | +1.17 pp | 5.66%→29.10% | +23.44 pp | +25.00 pp |
| 302 | 2.93%→4.49% | +1.56 pp | 5.66%→30.27% | +24.61 pp | +25.78 pp |
| 303 | 2.93%→5.08% | +2.15 pp | 5.66%→56.84% | +51.17 pp | +51.76 pp |

STEP: step100 = 4.56% ± 0.49% (3-seed mean +/- sample SD); mean gain over the condition-specific step0 = +1.63 percentage points.

NAME: step100 = 38.74% ± 15.69% (3-seed mean +/- sample SD); mean gain over the condition-specific step0 = +33.07 percentage points.

Mean paired NAME-STEP endpoint difference: +34.18 ± 15.23 percentage points; 3/3 seeds are positive. Mean difference in learning gains: +31.45 percentage points. Three seeds provide preliminary replication; seed x example counts are not treated as many independent model replications.

step0 uses the same original policy: fresh validation/test outputs are generated once per condition and explicitly referenced by three seeds. Each run retains its own paired LoRA initialization checkpoint. The fresh test set is scored only at the scheduled step0 and 100, with no best-checkpoint selection.

## Validation thresholds and complete learning curves

| Condition | seed | First 60% | First 70% | First 80% | First 90% | Mean curve success (trapezoidal area/100) |
|---|---:|---:|---:|---:|---:|---:|
| STEP | 301 | Not reached | Not reached | Not reached | Not reached | 4.65% |
| NAME | 301 | Not reached | Not reached | Not reached | Not reached | 16.13% |
| STEP | 302 | Not reached | Not reached | Not reached | Not reached | 4.94% |
| NAME | 302 | Not reached | Not reached | Not reached | Not reached | 16.80% |
| STEP | 303 | Not reached | Not reached | Not reached | Not reached | 4.84% |
| NAME | 303 | Not reached | Not reached | Not reached | Not reached | 27.01% |

Thresholds record the first fixed evaluation point at step0/10/.../100 that reaches the target. Exact crossing times between checkpoints are not inferred, and unreached thresholds receive no arbitrary update count. Complete per-seed curves and actual training tokens/GPU time at every point are in analysis/results.json.

![Validation success by update](figures/validation-vs-updates.png)

![Validation success by actual compute](figures/validation-vs-compute.png)

## Sampling, optimization, and costs

| Condition | seed | Candidates | Output tokens | Mixed-reward group fraction | Duplicate candidate fraction | Maximum KL | Training-segment GPU-hours |
|---|---:|---:|---:|---:|---:|---:|---:|
| STEP | 301 | 12800 | 2266100 | 5.56% | 26.09% | 0.03348 | 4.392 |
| NAME | 301 | 12800 | 2230535 | 19.50% | 42.71% | 0.15948 | 4.132 |
| STEP | 302 | 12800 | 2280695 | 5.50% | 24.88% | 0.05895 | 4.336 |
| NAME | 302 | 12800 | 2226662 | 22.38% | 43.09% | 0.13564 | 4.110 |
| STEP | 303 | 12800 | 2271855 | 5.75% | 24.13% | 0.06589 | 4.336 |
| NAME | 303 | 12800 | 2234128 | 28.69% | 47.13% | 0.15393 | 4.119 |

Duplicate fractions are measured within the 8 outputs for each example. All-0/all-1 groups are retained with zero task advantage, though KL gradients may remain. Equal update budgets do not imply equal compute. Compute curves accumulate sampling and update wall time across both ranks. Training-segment GPU time is run wall time after NCCL initialization x2, including model loading, saving, and waiting, but excluding earlier process/NCCL startup; it is not active GPU-kernel time. Full job occupancy, evaluation, and precheck/recovery costs are listed separately in the combined cost audit. These nested timings must not be added together.

## Headings, errors, and stopping reasons (step100 fresh test)

| Condition | seed | Fully compliant headings | Operation-sequence mismatch | Numerical error | Early prefix stop | Extra raw operations | Extra format lines | Truncation |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| STEP | 301 | 74.02% | 353 | 417 | 64 | 168 | 5 | 0 |
| NAME | 301 | 79.49% | 123 | 301 | 51 | 36 | 1 | 0 |
| STEP | 302 | 76.76% | 360 | 420 | 50 | 181 | 3 | 0 |
| NAME | 302 | 79.49% | 137 | 290 | 46 | 58 | 3 | 0 |
| STEP | 303 | 77.93% | 344 | 409 | 46 | 179 | 3 | 0 |
| NAME | 303 | 72.66% | 77 | 165 | 19 | 33 | 0 | 0 |

Error flags can overlap. Numerical errors are checked against the preceding output state; expansion mismatches include extra/missing operations. Extra raw operations are not directly counted as extra tool calls. Heading compliance is reported separately and excluded from binary rewards. Per-example raw outputs, token IDs, and EOS/cap evidence are retained in eval/outputs/.

## Evidence and scope of interpretation

Frozen configurations: config/frozen.json and freeze-manifest.json; data: data/manifest.json; prechecks: analysis/precheck-complete.json; fixed checkpoints and candidates: runs/v1-*; complete curves/pairing/costs: analysis/results.json. Implementation definitions are in the parent REGISTRATION.md. See the parent REPORT.md and COMPLETION_AUDIT.md for combined interpretation and acceptance checks.

This study compares whether label structure helps train execution under a supplied plan. It adds no internal/local rewards and does not establish transfer to real mathematics or agents, cross-model generalization, or novelty. Method gains are distinguished from hypotheses about internal mechanisms.

See [CASE_REVIEW.md](CASE_REVIEW.md) for supplementary mutually exclusive error categories, heading boundaries, and raw/reference trajectory examples. These categories interpret outputs without changing scores; heading noncompliance is distinct from tool-identity error.
