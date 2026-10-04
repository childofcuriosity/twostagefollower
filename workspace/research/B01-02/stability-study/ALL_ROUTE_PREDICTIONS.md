# Testing product predictions consistently for joint and separate training
All results below use fixed 512-step matched controls under the new protocol, not replacements for the original first-stage NAME baseline. Sequence and operation accuracies are measured with the program supplying the correct other component; actual execution receives no reference-answer assistance.
Compute products within each seed and length, then aggregate. The all-row prediction therefore need not equal the product of the two displayed overall mean rates. See JSON for 256-step and per-seed records.

|Model|Name writer / operation writer|Length|Sequence accuracy|Operation accuracy|Stratified product prediction|Actual success|Error pp|
|---|---|---|---:|---:|---:|---:|---:|
|qwen3b|Joint / joint|all|45.76%|74.38%|41.17%|40.49%|-0.69|
|qwen3b|Sequence specialist / joint|all|68.26%|74.38%|55.86%|53.89%|-1.97|
|qwen3b|Joint / operation specialist|all|45.76%|79.44%|40.12%|40.28%|+0.16|
|qwen3b|Sequence specialist / operation specialist|all|68.26%|79.44%|56.04%|55.83%|-0.20|
|qwen32b|Joint / joint|all|98.40%|86.67%|85.43%|85.35%|-0.08|
|qwen32b|Sequence specialist / joint|all|98.12%|86.67%|85.22%|85.21%|-0.01|
|qwen32b|Joint / operation specialist|all|98.40%|94.86%|93.40%|93.33%|-0.07|
|qwen32b|Sequence specialist / operation specialist|all|98.12%|94.86%|93.20%|93.19%|-0.00|
|qwen3b|Joint / joint|3|86.11%|99.65%|85.78%|85.76%|-0.01|
|qwen3b|Sequence specialist / joint|3|84.03%|99.65%|83.68%|83.68%|+0.00|
|qwen3b|Joint / operation specialist|3|86.11%|95.83%|82.51%|82.29%|-0.22|
|qwen3b|Sequence specialist / operation specialist|3|84.03%|95.83%|80.36%|80.21%|-0.15|
|qwen32b|Joint / joint|3|100.00%|100.00%|100.00%|100.00%|+0.00|
|qwen32b|Sequence specialist / joint|3|100.00%|100.00%|100.00%|100.00%|+0.00|
|qwen32b|Joint / operation specialist|3|100.00%|100.00%|100.00%|100.00%|+0.00|
|qwen32b|Sequence specialist / operation specialist|3|100.00%|100.00%|100.00%|100.00%|+0.00|
|qwen3b|Joint / joint|4|64.24%|95.49%|61.14%|61.11%|-0.03|
|qwen3b|Sequence specialist / joint|4|80.90%|95.49%|77.76%|76.39%|-1.37|
|qwen3b|Joint / operation specialist|4|64.24%|96.18%|62.13%|62.50%|+0.37|
|qwen3b|Sequence specialist / operation specialist|4|80.90%|96.18%|77.34%|77.78%|+0.44|
|qwen32b|Joint / joint|4|100.00%|96.18%|96.18%|96.18%|+0.00|
|qwen32b|Sequence specialist / joint|4|99.65%|96.18%|95.86%|96.18%|+0.32|
|qwen32b|Joint / operation specialist|4|100.00%|97.92%|97.92%|97.92%|+0.00|
|qwen32b|Sequence specialist / operation specialist|4|99.65%|97.92%|97.59%|97.92%|+0.33|
|qwen3b|Joint / joint|5|42.01%|78.12%|34.99%|32.64%|-2.35|
|qwen3b|Sequence specialist / joint|5|70.14%|78.12%|57.26%|54.86%|-2.39|
|qwen3b|Joint / operation specialist|5|42.01%|84.03%|34.12%|33.33%|-0.79|
|qwen3b|Sequence specialist / operation specialist|5|70.14%|84.03%|57.25%|55.21%|-2.04|
|qwen32b|Joint / joint|5|100.00%|85.76%|85.76%|85.76%|+0.00|
|qwen32b|Sequence specialist / joint|5|96.18%|85.76%|82.56%|81.60%|-0.96|
|qwen32b|Joint / operation specialist|5|100.00%|92.71%|92.71%|92.71%|+0.00|
|qwen32b|Sequence specialist / operation specialist|5|96.18%|92.71%|89.19%|89.24%|+0.04|
|qwen3b|Joint / joint|6|26.39%|63.19%|17.96%|19.79%|+1.83|
|qwen3b|Sequence specialist / joint|6|65.28%|63.19%|43.51%|39.24%|-4.28|
|qwen3b|Joint / operation specialist|6|26.39%|76.04%|18.84%|21.18%|+2.34|
|qwen3b|Sequence specialist / operation specialist|6|65.28%|76.04%|47.12%|46.18%|-0.94|
|qwen32b|Joint / joint|6|100.00%|83.33%|83.33%|83.33%|+0.00|
|qwen32b|Sequence specialist / joint|6|98.26%|83.33%|81.85%|82.29%|+0.44|
|qwen32b|Joint / operation specialist|6|100.00%|93.06%|93.06%|93.40%|+0.35|
|qwen32b|Sequence specialist / operation specialist|6|98.26%|93.06%|91.51%|91.67%|+0.16|
|qwen3b|Joint / joint|8|10.07%|35.42%|6.00%|3.12%|-2.87|
|qwen3b|Sequence specialist / joint|8|40.97%|35.42%|17.10%|15.28%|-1.82|
|qwen3b|Joint / operation specialist|8|10.07%|45.14%|2.98%|2.08%|-0.90|
|qwen3b|Sequence specialist / operation specialist|8|40.97%|45.14%|18.11%|19.79%|+1.68|
|qwen32b|Joint / joint|8|92.01%|68.06%|61.85%|61.46%|-0.39|
|qwen32b|Sequence specialist / joint|8|96.53%|68.06%|65.84%|65.97%|+0.13|
|qwen32b|Joint / operation specialist|8|92.01%|90.62%|83.33%|82.64%|-0.69|
|qwen32b|Sequence specialist / operation specialist|8|96.53%|90.62%|87.70%|87.15%|-0.54|

If the same two subtask scores also approximately predict jointly trained models, product agreement supports decomposition as a performance diagnostic. It alone does not establish that separate training creates independent internal modules. Learning gains require separate assessment through same-protocol training controls, actual component replacement, and context interventions.
