# Checking oracle subtask products
Each length has 24 programs x 4 inputs x 3 training seeds. Compute A x B within each seed, then average. Both-correct on the same example is measured from two oracle evaluations, not an executed composed model. The table reports both-correct minus A x B, in percentage points. Intervals use 2000 program-cluster bootstrap resamples, conditional on the three observed seeds; they exclude population uncertainty over training seeds. An interval containing 0 does not establish independence or equivalence.
|Model|Calls|Difference|Program bootstrap 95% interval|Seed11 / 22 / 33 differences|
|---|---:|---:|---|---|
|qwen1.5b|3|+0.18|[-0.20, +0.74]|+0.00 / +0.00 / +0.54|
|qwen1.5b|4|+1.87|[-0.87, +5.03]|+0.00 / +2.65 / +2.95|
|qwen1.5b|5|-0.60|[-5.69, +4.44]|-2.93 / +1.91 / -0.77|
|qwen1.5b|6|+0.38|[-3.79, +4.36]|+0.62 / -0.42 / +0.95|
|qwen1.5b|8|+1.88|[-2.61, +6.16]|+0.52 / +0.50 / +4.62|
|qwen3b|3|-0.48|[-1.48, +0.00]|+0.00 / -1.43 / +0.00|
|qwen3b|4|+0.36|[-0.27, +1.35]|+0.00 / +1.07 / +0.00|
|qwen3b|5|-1.90|[-4.16, -0.02]|-5.78 / +0.78 / -0.68|
|qwen3b|6|-0.95|[-3.59, +1.99]|-2.05 / +0.58 / -1.37|
|qwen3b|8|+0.13|[-3.09, +3.15]|+0.81 / -1.91 / +1.48|
|qwen7b|3|+0.00|[+0.00, +0.00]|+0.00 / +0.00 / +0.00|
|qwen7b|4|+0.53|[-1.52, +3.21]|+3.10 / -0.61 / -0.91|
|qwen7b|5|-2.58|[-5.95, +0.90]|-5.64 / -1.82 / -0.26|
|qwen7b|6|-0.65|[-4.64, +3.14]|-0.35 / +0.78 / -2.39|
|qwen7b|8|-1.61|[-3.49, +0.69]|-1.53 / -3.31 / +0.00|
|qwen32b|3|+0.00|[+0.00, +0.00]|+0.00 / +0.00 / +0.00|
|qwen32b|4|-0.02|[-0.09, +0.00]|-0.07 / +0.00 / +0.00|
|qwen32b|5|-0.30|[-0.93, +0.00]|-0.65 / -0.26 / +0.00|
|qwen32b|6|-0.19|[-0.61, +0.00]|-0.10 / -0.48 / +0.00|
|qwen32b|8|-0.20|[-1.06, +0.47]|-0.26 / -0.33 / +0.00|

See ORACLE_PRODUCTS.md for A, B, and joint free-execution accuracy. Distinguish two differences: both-correct versus the product measures statistical association between oracle subtask outputs; the product versus joint free execution additionally changes training and inference environments and cannot be attributed only to correlation.
