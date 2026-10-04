# B01-02: label comparison under binary-reward GRPO

Qwen2.5-7B-Instruct at the original revision, fixed L3; the nine tools and STEP/NAME prompts match the previous study; BF16 base + LoRA, with no additional SFT. Reward is strict full-trajectory 0/1, with no heading reward. Each of 6 runs has 100 updates, using 16 examples x 8 candidates per update.

## Fresh test endpoints (512 examples)

| seed | STEP step0 to 100 | STEP gain | NAME step0 to 100 | NAME gain | NAME-STEP endpoint difference |
|---:|---:|---:|---:|---:|---:|
| 301 | 3.91%→8.79% | +4.88 pp | 7.23%→28.91% | +21.68 pp | +20.12 pp |
| 302 | 3.91%→8.40% | +4.49 pp | 7.23%→33.01% | +25.78 pp | +24.61 pp |
| 303 | 3.91%→7.62% | +3.71 pp | 7.23%→36.33% | +29.10 pp | +28.71 pp |

STEP: step100 = 8.27% ± 0.60% (3-seed mean +/- sample SD); mean gain over the condition-specific step0 = +4.36 percentage points.

NAME: step100 = 32.75% ± 3.72% (3-seed mean +/- sample SD); mean gain over the condition-specific step0 = +25.52 percentage points.

Mean paired NAME-STEP endpoint difference: +24.48 ± 4.30 percentage points; 3/3 seeds are positive. Mean difference in learning gains: +21.16 percentage points. Three seeds provide preliminary replication; seed x example counts are not treated as many independent model replications.

step0 uses the same original policy: fresh validation/test outputs are generated once per condition and explicitly referenced by three seeds. Each run retains its own paired LoRA initialization checkpoint. The fresh test set is scored only at the scheduled step0 and 100, with no best-checkpoint selection.

## Validation thresholds and complete learning curves

| Condition | seed | First 60% | First 70% | First 80% | First 90% | Mean curve success (trapezoidal area/100) |
|---|---:|---:|---:|---:|---:|---:|
| STEP | 301 | Not reached | Not reached | Not reached | Not reached | 8.69% |
| NAME | 301 | Not reached | Not reached | Not reached | Not reached | 18.79% |
| STEP | 302 | Not reached | Not reached | Not reached | Not reached | 8.20% |
| NAME | 302 | Not reached | Not reached | Not reached | Not reached | 19.10% |
| STEP | 303 | Not reached | Not reached | Not reached | Not reached | 7.95% |
| NAME | 303 | Not reached | Not reached | Not reached | Not reached | 22.60% |

Thresholds record the first fixed evaluation point at step0/10/.../100 that reaches the target. Exact crossing times between checkpoints are not inferred, and unreached thresholds receive no arbitrary update count. Complete per-seed curves and actual training tokens/GPU time at every point are in analysis/results.json.

![Validation success by update](figures/validation-vs-updates.png)

![Validation success by actual compute](figures/validation-vs-compute.png)

## Sampling, optimization, and costs

| Condition | seed | Candidates | Output tokens | Mixed-reward group fraction | Duplicate candidate fraction | Maximum KL | Training-segment GPU-hours |
|---|---:|---:|---:|---:|---:|---:|---:|
| STEP | 301 | 12800 | 1209688 | 11.50% | 25.48% | 0.03079 | 1.581 |
| NAME | 301 | 12800 | 1178337 | 18.56% | 35.68% | 0.08166 | 1.542 |
| STEP | 302 | 12800 | 1204276 | 10.88% | 24.41% | 0.03208 | 1.578 |
| NAME | 302 | 12800 | 1169590 | 19.94% | 37.41% | 0.10883 | 1.542 |
| STEP | 303 | 12800 | 1210651 | 9.81% | 24.17% | 0.08079 | 1.582 |
| NAME | 303 | 12800 | 1174228 | 23.94% | 38.02% | 0.50676 | 1.548 |

Duplicate fractions are measured within the 8 outputs for each example. All-0/all-1 groups are retained with zero task advantage, though KL gradients may remain. Equal update budgets do not imply equal compute. Compute curves accumulate sampling and update wall time across both ranks. Training-segment GPU time is run wall time after NCCL initialization x2, including model loading, saving, and waiting, but excluding earlier process/NCCL startup; it is not active GPU-kernel time. Full job occupancy, evaluation, and precheck/recovery costs are listed separately in the combined cost audit. These nested timings must not be added together.

## Headings, errors, and stopping reasons (step100 fresh test)

| Condition | seed | Fully compliant headings | Operation-sequence mismatch | Numerical error | Early prefix stop | Extra raw operations | Extra format lines | Truncation |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| STEP | 301 | 93.95% | 321 | 385 | 25 | 172 | 9 | 0 |
| NAME | 301 | 94.53% | 123 | 320 | 20 | 60 | 8 | 0 |
| STEP | 302 | 93.36% | 327 | 382 | 25 | 185 | 5 | 0 |
| NAME | 302 | 95.31% | 113 | 304 | 18 | 60 | 4 | 0 |
| STEP | 303 | 90.43% | 326 | 405 | 37 | 170 | 9 | 0 |
| NAME | 303 | 95.31% | 104 | 277 | 24 | 35 | 3 | 0 |

Error flags can overlap. Numerical errors are checked against the preceding output state; expansion mismatches include extra/missing operations. Extra raw operations are not directly counted as extra tool calls. Heading compliance is reported separately and excluded from binary rewards. Per-example raw outputs, token IDs, and EOS/cap evidence are retained in eval/outputs/.

## Evidence and scope of interpretation

Frozen configurations: config/frozen.json and freeze-manifest.json; data: data/manifest.json; prechecks: analysis/precheck-complete.json; fixed checkpoints and candidates: runs/v1-*; complete curves/pairing/costs: analysis/results.json. Implementation definitions are in the parent REGISTRATION.md. See the parent REPORT.md and COMPLETION_AUDIT.md for combined interpretation and acceptance checks.

This study compares whether label structure helps train execution under a supplied plan. It adds no internal/local rewards and does not establish transfer to real mathematics or agents, cross-model generalization, or novelty. Method gains are distinguished from hypotheses about internal mechanisms.

See [CASE_REVIEW.md](CASE_REVIEW.md) for supplementary mutually exclusive error categories, heading boundaries, and raw/reference trajectory examples. These categories interpret outputs without changing scores; heading noncompliance is distinct from tool-identity error.
