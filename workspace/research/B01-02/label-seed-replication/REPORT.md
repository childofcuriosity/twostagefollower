# Label experiments: replication with 20 training seeds

The original training data, earlier independent 480-example set, and one alias mapping are fixed. The original 3 seeds are reused, with 17 new seeds 100–116. Results reflect only training randomness under fixed data and mapping. Values are mean ± sample SD, in percent.

|Model|Uniform step|Position numbering|Fixed aliases|Original tool names|
|---|---:|---:|---:|---:|
|qwen1.5b|0.00 ± 0.00%|0.00 ± 0.00%|15.21 ± 8.92%|18.84 ± 5.79%|
|qwen3b|0.00 ± 0.00%|0.87 ± 0.78%|49.45 ± 11.68%|35.06 ± 5.55%|
|qwen7b|13.49 ± 6.00%|15.16 ± 9.31%|43.73 ± 15.19%|41.25 ± 13.14%|

## Same-seed paired differences: earlier independent 480-example set

Differences, sample SDs, and 95% t intervals are in percentage points. Intervals cover training-seed variation only, conditional on this set of test programs.

|Model|Comparison|Mean±SD|95% interval|Positive/negative/tied seeds|
|---|---|---:|---:|---:|
|qwen1.5b|Position numbering − Uniform step|+0.00 ± 0.00|[+0.00, +0.00]|0/0/20|
|qwen1.5b|Fixed aliases − Position numbering|+15.21 ± 8.92|[+11.03, +19.38]|20/0/0|
|qwen1.5b|Original tool names − Fixed aliases|+3.64 ± 10.11|[-1.10, +8.37]|11/9/0|
|qwen1.5b|Original tool names − Uniform step|+18.84 ± 5.79|[+16.13, +21.55]|20/0/0|
|qwen1.5b|Fixed aliases − Original tool names|-3.64 ± 10.11|[-8.37, +1.10]|9/11/0|
|qwen3b|Position numbering − Uniform step|+0.87 ± 0.78|[+0.51, +1.24]|13/0/7|
|qwen3b|Fixed aliases − Position numbering|+48.57 ± 11.65|[+43.12, +54.02]|20/0/0|
|qwen3b|Original tool names − Fixed aliases|-14.39 ± 11.59|[-19.81, -8.96]|2/18/0|
|qwen3b|Original tool names − Uniform step|+35.06 ± 5.55|[+32.46, +37.66]|20/0/0|
|qwen3b|Fixed aliases − Original tool names|+14.39 ± 11.59|[+8.96, +19.81]|18/2/0|
|qwen7b|Position numbering − Uniform step|+1.67 ± 9.93|[-2.98, +6.31]|11/9/0|
|qwen7b|Fixed aliases − Position numbering|+28.57 ± 14.88|[+21.61, +35.53]|20/0/0|
|qwen7b|Original tool names − Fixed aliases|-2.48 ± 21.79|[-12.68, +7.72]|10/10/0|
|qwen7b|Original tool names − Uniform step|+27.76 ± 13.03|[+21.66, +33.86]|20/0/0|
|qwen7b|Fixed aliases − Original tool names|+2.48 ± 21.79|[-7.72, +12.68]|10/10/0|

## Original OOD test: 384 examples

|Model|Uniform step|Position numbering|Fixed aliases|Original tool names|
|---|---:|---:|---:|---:|
|qwen1.5b|0.00 ± 0.00%|0.00 ± 0.00%|25.46 ± 12.89%|30.12 ± 8.92%|
|qwen3b|0.00 ± 0.00%|1.32 ± 1.98%|69.99 ± 9.47%|58.15 ± 8.79%|
|qwen7b|18.95 ± 10.15%|23.66 ± 15.15%|63.72 ± 14.10%|60.68 ± 14.31%|

## Interpretation limits

- All 20 seeds use the same 4096 training examples, 480 test examples, and fixed alias mapping. SD does not measure uncertainty for new tasks, new data, or different mappings.
- Position numbering and tool identity do not form a strictly increasing information hierarchy; original names and fixed aliases both identify tools. The two new target formats contain approximately 2.96% more tokens than original names, and alias inputs are longer.
- Training contains only 1–2 calls; headings step3 and later for long tasks never appear as headings in training.
- Multiple comparisons are uncorrected, and the earlier independent set has been analyzed repeatedly. Positive/negative seed counts and intervals are not evidence about real agents or RSI.
- See analysis/results.json for every training seed, training loss, output-file hash, and itemized result. All failures are retained in raw outputs.
