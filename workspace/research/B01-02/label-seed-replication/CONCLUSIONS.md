# Replication with 20 training seeds: conclusions

As preregistered, this study completed the 20-training-seed comparison of four labels at 1.5B, 3B, and 7B. Earlier seeds 11/22/33 were reused read-only; all 204 new runs with seeds 100–116 succeeded. The primary endpoint is full-trajectory success on the same earlier independent 480-example set. Seeds, checkpoints, and sample sizes were not selected or changed based on interim performance.

## Main results

Means ± sample SD over 20 seeds per model/condition, in percent:

|Model|Uniform step|Position numbering|Fixed aliases|Original tool names|
|---|---:|---:|---:|---:|
|1.5B|0.00±0.00|0.00±0.00|15.21±8.92|18.84±5.79|
|3B|0.00±0.00|0.87±0.78|49.45±11.68|35.06±5.55|
|7B|13.49±6.00|15.16±9.31|43.73±15.19|41.25±13.14|

Comparisons use differences within the same seed:

|Model|Comparison|Mean difference, percentage points|Better/worse/tied among 20 seeds|Descriptive 95% t interval, percentage points|
|---|---|---:|---:|---:|
|1.5B|Fixed aliases−position numbering|+15.21|20/0/0|[+11.03,+19.38]|
|3B|Fixed aliases−position numbering|+48.57|20/0/0|[+43.12,+54.02]|
|7B|Fixed aliases−position numbering|+28.57|20/0/0|[+21.61,+35.53]|
|1.5B|Fixed aliases−original names|−3.64|9/11/0|[−8.37,+1.10]|
|3B|Fixed aliases−original names|+14.39|18/2/0|[+8.96,+19.81]|
|7B|Fixed aliases−original names|+2.48|10/10/0|[−7.72,+12.68]|
|7B|Position numbering−uniform step|+1.67|11/9/0|[−2.98,+6.31]|

Original tool names outperform uniform step in 20/20 seeds at each of 1.5B/3B/7B, with mean differences of +18.84, +35.06, and +27.76 percentage points. These remain results on fixed data and an earlier test set, not guarantees for other tasks.

## How much stronger is the evidence?

Twenty seeds estimate training randomness more reliably than three, without requiring SD itself to decrease. The clearest result is that, under this protocol and fixed mapping, **both conditions that output stable tool identities generally outperform position numbering substantially**. Original tool names also clearly outperform uniform step. At 3B, fixed aliases exceed original names by approximately 14.39 percentage points, with 18/20 seeds agreeing, providing stronger replication evidence for this mapping and earlier test set.

At 1.5B and 7B, twenty seeds still do not resolve which of fixed aliases or original names is better. At 7B, the mean difference is only +2.48 points, with paired-difference SD 21.79 points. If the effect is near this size, adding only a few seeds will not resolve it. A rough calculation using the observed SD and a conventional two-sided 95% interval requires approximately 300 paired seeds to reduce the half-width below 2.48 points, assuming the effect does not shrink. That is not a suitable next step. More informative work would change the fixed alias mapping, control tokenization and length, and confirm results on new test programs.

Position numbering does not consistently reproduce identity-label gains, but this does not establish that position information is useless: training includes only step1/step2 headings, while long tasks require step3 and later. Nor are the four conditions a single-variable manipulation of monotonically increasing information. Position and identity convey different information; fixed aliases and original names both provide identity with different word forms. The two added conditions have approximately 2.96% more target tokens than original names, and alias inputs are longer.

Intervals are computed over 20 training seeds, conditional on the same 4096 training examples, 480 test examples, and **one** fixed alias mapping. The 480 examples include four numerical inputs per sequence, rather than 480 independent programs. The dataset has been reused repeatedly and is not a fresh blind test. Multiple comparisons are uncorrected. Reliable benefits across mappings, datasets, real agents, or RSI cannot be inferred here.

## Execution and audit

All 204 new training/main-test/independent-test jobs exited with code 0. Each had 512 updates and 16,384 example exposures, yielding 212,160 new scored records. Including the earlier 36 model-condition-seed runs gives 249,600 records, not independent examples. Raw outputs, training logs, configurations, adapters, and per-seed statistics are retained. Earlier output hashes are unchanged, and per-example IDs, inputs, and sequences match. For all 17 new 7B seeds, initial adapters match file by file across the four conditions. New work totaled 66.52 allocated GPU-hours and 8.38 hours wall time, using only the 8 local PRO6000 GPUs. The final local GPU compute-process list was empty.

The first automated analysis failed because the standalone analysis script omitted an import of `re` while loading the old scoring module; all training and inference had already succeeded. Adding the import and rerunning offline analysis succeeded, without retraining or changing raw model outputs or the old scorer. The failure marker remains in analysis/pipeline-failed.json; recovery is recorded in analysis/recovery.json.

Detailed tables and original-test OOD results: [REPORT.md](REPORT.md). Per-seed results, paired differences, and output hashes: [analysis/results.json](analysis/results.json). Completion coverage: [analysis/completion-audit.json](analysis/completion-audit.json).
