# Original first-stage results versus second-stage separate training
This table uses the baseline corrected by the user: sequence/operation accuracies extracted from natural generations of the first-stage NAME model, compared with the corresponding separately trained second-stage subtasks. Oracle-assisted scores from the new jointly trained model do not replace first-stage results.
Both stages use the same independent confirmation examples: 96 examples x 3 seeds per length. Differences are second stage minus first stage, in percentage points.
The first-stage operation metric checks every emitted call; the second-stage metric checks every required call. The second stage also introduces the EndTool/Done handoff protocol and program-supplied complementary content at test time. These are cross-stage comparisons of existing scores, not strict single-factor differences changing only training.

## qwen1.5b
|Tools|First-stage sequence|Separately trained sequence|Difference|First-stage operations|Separately trained operations|Difference|
|---|---:|---:|---:|---:|---:|---:|
|3|53.47%|82.64%|+29.17|98.96%|99.31%|+0.35|
|4|27.08%|73.61%|+46.53|88.54%|90.62%|+2.08|
|5|7.64%|40.62%|+32.99|88.89%|73.26%|-15.62|
|6|2.43%|35.42%|+32.99|76.04%|75.35%|-0.69|
|8|1.04%|33.68%|+32.64|58.33%|41.67%|-16.67|

|Tools|First-stage original-model full-task accuracy|Product of first-stage extracted components|Product of separately trained components|
|---|---:|---:|---:|
|3|52.43%|52.78%|82.11%|
|4|21.18%|23.85%|66.19%|
|5|5.90%|6.34%|29.42%|
|6|0.69%|1.87%|24.62%|
|8|1.04%|0.35%|13.40%|

## qwen3b
|Tools|First-stage sequence|Separately trained sequence|Difference|First-stage operations|Separately trained operations|Difference|
|---|---:|---:|---:|---:|---:|---:|
|3|86.46%|84.72%|-1.74|97.22%|95.49%|-1.74|
|4|75.35%|82.29%|+6.94|84.03%|95.83%|+11.81|
|5|51.39%|70.14%|+18.75|69.44%|84.03%|+14.58|
|6|31.25%|64.93%|+33.68|55.56%|76.39%|+20.83|
|8|10.07%|41.32%|+31.25|40.28%|45.83%|+5.56|

|Tools|First-stage original-model full-task accuracy|Product of first-stage extracted components|Product of separately trained components|
|---|---:|---:|---:|
|3|83.68%|84.07%|80.69%|
|4|60.76%|61.94%|78.46%|
|5|28.47%|34.28%|57.10%|
|6|9.38%|14.47%|47.13%|
|8|2.08%|2.49%|18.62%|

## qwen7b
|Tools|First-stage sequence|Separately trained sequence|Difference|First-stage operations|Separately trained operations|Difference|
|---|---:|---:|---:|---:|---:|---:|
|3|90.97%|100.00%|+9.03|95.83%|98.96%|+3.12|
|4|67.71%|93.75%|+26.04|81.94%|85.07%|+3.12|
|5|45.14%|67.36%|+22.22|71.53%|57.64%|-13.89|
|6|36.11%|51.39%|+15.28|73.96%|52.43%|-21.53|
|8|17.01%|29.86%|+12.85|40.28%|9.38%|-30.90|

|Tools|First-stage original-model full-task accuracy|Product of first-stage extracted components|Product of separately trained components|
|---|---:|---:|---:|
|3|86.81%|86.98%|98.96%|
|4|52.08%|53.62%|79.68%|
|5|23.61%|29.54%|44.94%|
|6|22.57%|24.60%|26.69%|
|8|0.00%|3.48%|3.00%|

## qwen32b
|Tools|First-stage sequence|Separately trained sequence|Difference|First-stage operations|Separately trained operations|Difference|
|---|---:|---:|---:|---:|---:|---:|
|3|94.10%|100.00%|+5.90|100.00%|100.00%|+0.00|
|4|73.26%|99.65%|+26.39|98.26%|97.92%|-0.35|
|5|59.03%|96.18%|+37.15|98.96%|92.71%|-6.25|
|6|32.99%|98.26%|+65.28|96.53%|93.06%|-3.47|
|8|27.78%|96.53%|+68.75|89.24%|90.62%|+1.39|

|Tools|First-stage original-model full-task accuracy|Product of first-stage extracted components|Product of separately trained components|
|---|---:|---:|---:|
|3|94.10%|94.10%|100.00%|
|4|71.53%|72.14%|97.59%|
|5|57.99%|58.66%|89.19%|
|6|32.64%|32.25%|91.51%|
|8|24.65%|24.67%|87.70%|
