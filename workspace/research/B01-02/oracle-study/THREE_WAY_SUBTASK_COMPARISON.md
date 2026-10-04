# Three-way comparison of subtask accuracy
Compare natural outputs of the original first-stage model, program-assisted subtask tests after joint training in this stage, and subtask tests after separate training with the same assistance. Each cell uses 96 examples x 3 seeds from the same independent confirmation set.
In sequence tests, the program executes the tools actually selected by the model without correcting names. In operation tests, it supplies correct names. Only the current joint-versus-separate columns compare training under the same format and program assistance. First-stage operations cover emitted calls; current operations cover all required calls. Cross-stage differences are not pure training effects.

## qwen1.5b
|Tools|Subtask|First-stage original model|Current joint training|Current separate training|Separate−joint (percentage points)|
|---|---|---:|---:|---:|---:|
|3|Sequence|53.47%|93.40%|82.64%|-10.76|
|3|Operations|98.96%|98.26%|99.31%|+1.04|
|4|Sequence|27.08%|64.24%|73.61%|+9.38|
|4|Operations|88.54%|95.83%|90.62%|-5.21|
|5|Sequence|7.64%|36.46%|40.62%|+4.17|
|5|Operations|88.89%|84.38%|73.26%|-11.11|
|6|Sequence|2.43%|26.74%|35.42%|+8.68|
|6|Operations|76.04%|74.31%|75.35%|+1.04|
|8|Sequence|1.04%|28.47%|33.68%|+5.21|
|8|Operations|58.33%|53.47%|41.67%|-11.81|

## qwen3b
|Tools|Subtask|First-stage original model|Current joint training|Current separate training|Separate−joint (percentage points)|
|---|---|---:|---:|---:|---:|
|3|Sequence|86.46%|86.11%|84.72%|-1.39|
|3|Operations|97.22%|99.65%|95.49%|-4.17|
|4|Sequence|75.35%|64.58%|82.29%|+17.71|
|4|Operations|84.03%|95.83%|95.83%|+0.00|
|5|Sequence|51.39%|43.06%|70.14%|+27.08|
|5|Operations|69.44%|78.12%|84.03%|+5.90|
|6|Sequence|31.25%|27.43%|64.93%|+37.50|
|6|Operations|55.56%|62.85%|76.39%|+13.54|
|8|Sequence|10.07%|9.03%|41.32%|+32.29|
|8|Operations|40.28%|35.42%|45.83%|+10.42|

## qwen7b
|Tools|Subtask|First-stage original model|Current joint training|Current separate training|Separate−joint (percentage points)|
|---|---|---:|---:|---:|---:|
|3|Sequence|90.97%|98.26%|100.00%|+1.74|
|3|Operations|95.83%|98.96%|98.96%|+0.00|
|4|Sequence|67.71%|89.93%|93.75%|+3.82|
|4|Operations|81.94%|94.10%|85.07%|-9.03|
|5|Sequence|45.14%|62.50%|67.36%|+4.86|
|5|Operations|71.53%|84.72%|57.64%|-27.08|
|6|Sequence|36.11%|46.18%|51.39%|+5.21|
|6|Operations|73.96%|78.12%|52.43%|-25.69|
|8|Sequence|17.01%|33.33%|29.86%|-3.47|
|8|Operations|40.28%|48.61%|9.38%|-39.24|

## qwen32b
|Tools|Subtask|First-stage original model|Current joint training|Current separate training|Separate−joint (percentage points)|
|---|---|---:|---:|---:|---:|
|3|Sequence|94.10%|100.00%|100.00%|+0.00|
|3|Operations|100.00%|100.00%|100.00%|+0.00|
|4|Sequence|73.26%|100.00%|99.65%|-0.35|
|4|Operations|98.26%|96.18%|97.92%|+1.74|
|5|Sequence|59.03%|100.00%|96.18%|-3.82|
|5|Operations|98.96%|85.76%|92.71%|+6.94|
|6|Sequence|32.99%|100.00%|98.26%|-1.74|
|6|Operations|96.53%|83.33%|93.06%|+9.72|
|8|Sequence|27.78%|92.01%|96.53%|+4.51|
|8|Operations|89.24%|68.06%|90.62%|+22.57|
