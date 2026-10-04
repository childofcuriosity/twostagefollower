# Can the product of two subtask accuracies predict actual execution?
The sequence column comes from tests where a program correctly executes selected tools; the operation column comes from tests where a program supplies correct names. The final comparison is actual connected execution without program-supplied correct answers.
Compute products within each seed, then average. Error=actual success minus product. Intervals use paired resampling clustered by tool composition, conditional on the three observed training seeds; they do not establish independent internal mechanisms.

|Model|Training steps|Length|Sequence accuracy|Operation accuracy|Product|Actual full success|Error pp|95% error interval pp|
|---|---:|---|---:|---:|---:|---:|---:|---|
|qwen3b|256|all|68.47%|78.33%|52.63%|54.86%|+2.23|[+0.64, +3.86]|
|qwen3b|256|3|83.33%|95.83%|79.86%|79.51%|-0.35|[-1.13, +0.00]|
|qwen3b|256|4|81.25%|96.53%|78.27%|79.17%|+0.90|[+0.00, +2.33]|
|qwen3b|256|5|70.14%|81.60%|55.10%|53.12%|-1.97|[-4.42, +0.08]|
|qwen3b|256|6|64.93%|74.65%|46.20%|45.83%|-0.37|[-2.72, +2.28]|
|qwen3b|256|8|42.71%|43.06%|17.90%|16.67%|-1.23|[-4.42, +1.88]|
|qwen3b|512|all|68.26%|79.44%|53.16%|55.83%|+2.68|[+1.07, +4.41]|
|qwen3b|512|3|84.03%|95.83%|80.36%|80.21%|-0.15|[-0.59, +0.04]|
|qwen3b|512|4|80.90%|96.18%|77.34%|77.78%|+0.44|[+0.00, +1.37]|
|qwen3b|512|5|70.14%|84.03%|57.25%|55.21%|-2.04|[-4.28, -0.04]|
|qwen3b|512|6|65.28%|76.04%|47.12%|46.18%|-0.94|[-3.47, +1.91]|
|qwen3b|512|8|40.97%|45.14%|18.11%|19.79%|+1.68|[-1.37, +4.47]|
|qwen32b|256|all|98.06%|94.10%|92.31%|92.43%|+0.12|[-0.17, +0.51]|
|qwen32b|256|3|100.00%|100.00%|100.00%|100.00%|+0.00|[+0.00, +0.00]|
|qwen32b|256|4|99.65%|96.88%|96.56%|96.53%|-0.03|[-0.12, +0.00]|
|qwen32b|256|5|96.18%|91.67%|88.19%|88.19%|+0.01|[-0.82, +0.97]|
|qwen32b|256|6|98.61%|92.01%|90.78%|90.62%|-0.16|[-0.61, +0.00]|
|qwen32b|256|8|95.83%|89.93%|86.49%|86.81%|+0.32|[-0.87, +1.88]|
|qwen32b|512|all|98.12%|94.86%|93.12%|93.19%|+0.07|[-0.29, +0.47]|
|qwen32b|512|3|100.00%|100.00%|100.00%|100.00%|+0.00|[+0.00, +0.00]|
|qwen32b|512|4|99.65%|97.92%|97.59%|97.92%|+0.33|[+0.00, +1.02]|
|qwen32b|512|5|96.18%|92.71%|89.19%|89.24%|+0.04|[-1.19, +1.27]|
|qwen32b|512|6|98.26%|93.06%|91.51%|91.67%|+0.16|[-0.46, +0.98]|
|qwen32b|512|8|96.53%|90.62%|87.70%|87.15%|-0.54|[-1.94, +0.74]|

## Overall prediction controlling for task length
Long tasks affect both subtasks. Multiplying rates after pooling lengths mixes in length-induced association. The table first multiplies within each seed and length, then aggregates with equal weights across the tested lengths, without selecting or dropping lengths. The directly pooled product in the all row above is retained.

|Model|Steps|Length-stratified product prediction|Actual full success|Error pp|Stratified program-bootstrap interval pp|
|---|---:|---:|---:|---:|---|
|qwen3b|256|55.47%|54.86%|-0.60|[-1.54, +0.36]|
|qwen3b|512|56.04%|55.83%|-0.20|[-1.15, +0.73]|
|qwen32b|256|92.40%|92.43%|+0.03|[-0.29, +0.40]|
|qwen32b|512|93.20%|93.19%|-0.00|[-0.41, +0.41]|

These subtask scores measure each model along correct histories. Error-free execution requires both components to remain correct on that path. Multiplying marginal accuracies additionally assumes weak failure association within each length. Prediction agreement supports the usefulness of this statistical approximation, not independent internal learning, and does not exclude loss-weighting or parameter-capacity effects.
