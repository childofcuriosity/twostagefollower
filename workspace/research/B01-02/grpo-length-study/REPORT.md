# Binary GRPO: full model-by-length results

All 6 settings completed STEP/NAME × 3 paired seeds, with 100 updates per run. The primary metric is strict full-trajectory success. Values below are the scheduled endpoints on 512 fresh test examples; uncertainty is the sample SD across seeds, not an example-sampling confidence interval.

| Setting | STEP step0→100 mean±SD | NAME step0→100 mean±SD | Paired NAME−STEP mean±SD(pp) | Positive/negative/tied seeds | STEP validation endpoint | 20%–90% candidate window |
|---|---:|---:|---:|---|---:|---|
| 7b-L3 | 3.91%→8.27% ±0.60pp | 7.23%→32.75% ±3.72pp | +24.48 ±4.30 | 3/0/0 | 10.81% | No |
| 7b-L4 | 0.78%→0.91% ±0.11pp | 2.93%→4.17% ±0.30pp | +3.26 ±0.23 | 3/0/0 | 1.04% | No |
| 7b-L5 | 0.00%→0.00% ±0.00pp | 0.98%→0.85% ±0.30pp | +0.85 ±0.30 | 3/0/0 | 0.00% | No |
| 14b-L5 | 5.47%→32.94% ±8.91pp | 10.55%→70.77% ±14.80pp | +37.83 ±8.40 | 3/0/0 | 35.55% | Yes |
| 14b-L6 | 2.93%→4.56% ±0.49pp | 5.66%→38.74% ±15.69pp | +34.18 ±15.23 | 3/0/0 | 5.34% | No |
| 14b-L7 | 0.78%→0.72% ±0.23pp | 3.52%→7.29% ±1.19pp | +6.58 ±0.98 | 3/0/0 | 0.39% | No |

The candidate window uses the preregistered 20%–90% range for three-seed mean STEP success on the fixed validation set at step100. Settings are not selected by the NAME difference, nor checkpoints by test results. All continuous values and seed variation are retained; candidates still require independent confirmation. Original step0 is evaluated once per condition in each setting and shared across 3 seeds, rather than counted as 3 independent model evaluations.

![Length curves before and after training](figures/test-success-vs-length.png)

![All learning curves](figures/all-learning-curves.png)

## All prespecified thresholds

| Setting | Condition | seed | 60% | 70% | 80% | 90% |
|---|---|---:|---:|---:|---:|---:|
| 7b-L3 | STEP | 301 | Not reached | Not reached | Not reached | Not reached |
| 7b-L3 | NAME | 301 | Not reached | Not reached | Not reached | Not reached |
| 7b-L3 | STEP | 302 | Not reached | Not reached | Not reached | Not reached |
| 7b-L3 | NAME | 302 | Not reached | Not reached | Not reached | Not reached |
| 7b-L3 | STEP | 303 | Not reached | Not reached | Not reached | Not reached |
| 7b-L3 | NAME | 303 | Not reached | Not reached | Not reached | Not reached |
| 7b-L4 | STEP | 301 | Not reached | Not reached | Not reached | Not reached |
| 7b-L4 | NAME | 301 | Not reached | Not reached | Not reached | Not reached |
| 7b-L4 | STEP | 302 | Not reached | Not reached | Not reached | Not reached |
| 7b-L4 | NAME | 302 | Not reached | Not reached | Not reached | Not reached |
| 7b-L4 | STEP | 303 | Not reached | Not reached | Not reached | Not reached |
| 7b-L4 | NAME | 303 | Not reached | Not reached | Not reached | Not reached |
| 7b-L5 | STEP | 301 | Not reached | Not reached | Not reached | Not reached |
| 7b-L5 | NAME | 301 | Not reached | Not reached | Not reached | Not reached |
| 7b-L5 | STEP | 302 | Not reached | Not reached | Not reached | Not reached |
| 7b-L5 | NAME | 302 | Not reached | Not reached | Not reached | Not reached |
| 7b-L5 | STEP | 303 | Not reached | Not reached | Not reached | Not reached |
| 7b-L5 | NAME | 303 | Not reached | Not reached | Not reached | Not reached |
| 14b-L5 | STEP | 301 | Not reached | Not reached | Not reached | Not reached |
| 14b-L5 | NAME | 301 | Not reached | Not reached | Not reached | Not reached |
| 14b-L5 | STEP | 302 | Not reached | Not reached | Not reached | Not reached |
| 14b-L5 | NAME | 302 | 70 | 90 | Not reached | Not reached |
| 14b-L5 | STEP | 303 | Not reached | Not reached | Not reached | Not reached |
| 14b-L5 | NAME | 303 | 70 | 80 | Not reached | Not reached |
| 14b-L6 | STEP | 301 | Not reached | Not reached | Not reached | Not reached |
| 14b-L6 | NAME | 301 | Not reached | Not reached | Not reached | Not reached |
| 14b-L6 | STEP | 302 | Not reached | Not reached | Not reached | Not reached |
| 14b-L6 | NAME | 302 | Not reached | Not reached | Not reached | Not reached |
| 14b-L6 | STEP | 303 | Not reached | Not reached | Not reached | Not reached |
| 14b-L6 | NAME | 303 | Not reached | Not reached | Not reached | Not reached |
| 14b-L7 | STEP | 301 | Not reached | Not reached | Not reached | Not reached |
| 14b-L7 | NAME | 301 | Not reached | Not reached | Not reached | Not reached |
| 14b-L7 | STEP | 302 | Not reached | Not reached | Not reached | Not reached |
| 14b-L7 | NAME | 302 | Not reached | Not reached | Not reached | Not reached |
| 14b-L7 | STEP | 303 | Not reached | Not reached | Not reached | Not reached |
| 14b-L7 | NAME | 303 | Not reached | Not reached | Not reached | Not reached |

Thresholds are checked only at fixed evaluation points step0/10/.../100. Interpret all thresholds together with the complete curves; unreached thresholds are not assigned arbitrary update counts. Each setting report also plots curves against training GPU time and output tokens. Equal update counts are not treated as equal compute.

## Evidence for each setting

- [7b-L3 full report](7b-L3/REPORT.md): per-seed endpoints, gains over baseline, paired differences, curves, sampling, costs, errors, and headings.
- [7b-L4 full report](7b-L4/REPORT.md): per-seed endpoints, gains over baseline, paired differences, curves, sampling, costs, errors, and headings.
- [7b-L5 full report](7b-L5/REPORT.md): per-seed endpoints, gains over baseline, paired differences, curves, sampling, costs, errors, and headings.
- [14b-L5 full report](14b-L5/REPORT.md): per-seed endpoints, gains over baseline, paired differences, curves, sampling, costs, errors, and headings.
- [14b-L6 full report](14b-L6/REPORT.md): per-seed endpoints, gains over baseline, paired differences, curves, sampling, costs, errors, and headings.
- [14b-L7 full report](14b-L7/REPORT.md): per-seed endpoints, gains over baseline, paired differences, curves, sampling, costs, errors, and headings.

See CONCLUSIONS.md and COMPLETION_AUDIT.md for overall interpretation, failures, and resource checks. The two models share underlying data at fixed L5. These six settings form an exploratory screen, not six independent confirmatory experiments.
