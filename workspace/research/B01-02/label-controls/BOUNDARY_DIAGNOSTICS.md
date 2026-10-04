# Does execution continue after the second call?
Supplementary description using the registered segment-count/early-stopping metrics. This is not independent causal evidence for an attention mechanism or failure to extrapolate numbering. Every denominator is the earlier independent 480 examples x 3 seeds.

|Model|Condition|Emits at least a third segment label|Early Answer after correctly completing two tools|Full trajectory|
|---|---|---:|---:|---:|
|qwen1.5b|flat|0.00%|81.04%|0.00%|
|qwen1.5b|macro|80.35%|17.50%|16.25%|
|qwen1.5b|position|0.42%|75.69%|0.00%|
|qwen1.5b|alias|83.61%|13.75%|16.81%|
|qwen3b|flat|0.00%|80.28%|0.00%|
|qwen3b|macro|94.93%|3.68%|36.88%|
|qwen3b|position|28.47%|50.69%|0.97%|
|qwen3b|alias|97.78%|1.11%|52.92%|
|qwen7b|flat|78.96%|20.90%|12.15%|
|qwen7b|macro|97.01%|2.01%|37.01%|
|qwen7b|position|90.00%|9.24%|19.86%|
|qwen7b|alias|96.67%|3.33%|58.33%|
|qwen32b|flat|99.44%|0.56%|25.63%|
|qwen32b|macro|97.71%|2.29%|56.18%|
|qwen32b|position|97.99%|2.01%|39.17%|
|qwen32b|alias|88.82%|10.90%|31.18%|

All seeds, segment-count histograms, and full-trajectory rates stratified by correct labels are in analysis/boundary-diagnostics.json. Stratification conditional on model output introduces selection bias and cannot estimate an unbiased training effect.
