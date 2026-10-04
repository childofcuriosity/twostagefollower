# Two actual-execution subtasks and full success
Correct sequence means the entire task name list is correct. All operations correct means every actually generated call is expanded correctly; missing calls fail the sequence column.
Products are computed within each training seed and then averaged. A product close to full-task success indicates compatible aggregate rates, not proven statistical independence.
The separately listed correct-context product comes from two tests where a program supplies the correct other component; it is not actual execution performance.
|Model|Training steps|Tools|Name writer / operation writer|Correct sequence|All generated operations correct|Product of both columns|Actual full-task success|Correct-context product|
|---|---:|---|---|---:|---:|---:|---:|---:|
|qwen3b|256|all|Joint / joint|47.22%|83.68%|39.63%|41.74%|—|
|qwen3b|256|all|Sequence specialist / joint|68.40%|78.33%|53.90%|53.54%|—|
|qwen3b|256|all|Joint / operation specialist|47.64%|86.53%|41.14%|41.88%|—|
|qwen3b|256|all|Sequence specialist / operation specialist|68.61%|79.44%|53.10%|54.86%|52.63%|
|qwen3b|256|3|Joint / joint|87.50%|99.65%|87.17%|87.15%|—|
|qwen3b|256|3|Sequence specialist / joint|83.33%|99.65%|82.99%|82.99%|—|
|qwen3b|256|3|Joint / operation specialist|87.50%|96.18%|84.22%|83.68%|—|
|qwen3b|256|3|Sequence specialist / operation specialist|83.33%|96.18%|80.03%|79.51%|79.86%|
|qwen3b|256|4|Joint / joint|67.01%|96.18%|64.26%|63.19%|—|
|qwen3b|256|4|Sequence specialist / joint|81.25%|94.10%|77.06%|75.35%|—|
|qwen3b|256|4|Joint / operation specialist|67.01%|97.57%|65.51%|65.62%|—|
|qwen3b|256|4|Sequence specialist / operation specialist|81.25%|96.88%|78.49%|79.17%|78.27%|
|qwen3b|256|5|Joint / joint|44.44%|87.50%|39.21%|33.68%|—|
|qwen3b|256|5|Sequence specialist / joint|69.44%|84.72%|59.00%|55.21%|—|
|qwen3b|256|5|Joint / operation specialist|45.14%|88.54%|39.27%|34.72%|—|
|qwen3b|256|5|Sequence specialist / operation specialist|70.14%|81.25%|54.29%|53.12%|55.10%|
|qwen3b|256|6|Joint / joint|26.04%|78.82%|20.31%|19.79%|—|
|qwen3b|256|6|Sequence specialist / joint|66.32%|66.32%|43.68%|38.54%|—|
|qwen3b|256|6|Joint / operation specialist|27.08%|85.42%|22.59%|21.53%|—|
|qwen3b|256|6|Sequence specialist / operation specialist|65.62%|72.92%|44.87%|45.83%|46.20%|
|qwen3b|256|8|Joint / joint|11.11%|56.25%|7.43%|4.86%|—|
|qwen3b|256|8|Sequence specialist / joint|41.67%|46.88%|20.41%|15.62%|—|
|qwen3b|256|8|Joint / operation specialist|11.46%|64.93%|6.96%|3.82%|—|
|qwen3b|256|8|Sequence specialist / operation specialist|42.71%|50.00%|20.40%|16.67%|17.90%|
|qwen3b|512|all|Joint / joint|45.83%|83.82%|38.54%|40.49%|—|
|qwen3b|512|all|Sequence specialist / joint|68.33%|78.33%|54.04%|53.89%|—|
|qwen3b|512|all|Joint / operation specialist|45.76%|87.43%|39.85%|40.28%|—|
|qwen3b|512|all|Sequence specialist / operation specialist|68.47%|81.32%|54.36%|55.83%|53.16%|
|qwen3b|512|3|Joint / joint|86.11%|99.65%|85.78%|85.76%|—|
|qwen3b|512|3|Sequence specialist / joint|84.03%|99.65%|83.68%|83.68%|—|
|qwen3b|512|3|Joint / operation specialist|86.11%|96.18%|82.81%|82.29%|—|
|qwen3b|512|3|Sequence specialist / operation specialist|84.03%|96.18%|80.54%|80.21%|80.36%|
|qwen3b|512|4|Joint / joint|64.24%|96.88%|62.18%|61.11%|—|
|qwen3b|512|4|Sequence specialist / joint|80.90%|95.49%|77.76%|76.39%|—|
|qwen3b|512|4|Joint / operation specialist|64.24%|97.57%|62.87%|62.50%|—|
|qwen3b|512|4|Sequence specialist / operation specialist|80.90%|96.18%|77.34%|77.78%|77.34%|
|qwen3b|512|5|Joint / joint|43.06%|87.50%|38.12%|32.64%|—|
|qwen3b|512|5|Sequence specialist / joint|70.14%|84.38%|59.76%|54.86%|—|
|qwen3b|512|5|Joint / operation specialist|42.01%|90.97%|37.29%|33.33%|—|
|qwen3b|512|5|Sequence specialist / operation specialist|70.14%|83.68%|56.68%|55.21%|57.25%|
|qwen3b|512|6|Joint / joint|26.04%|79.51%|20.15%|19.79%|—|
|qwen3b|512|6|Sequence specialist / joint|65.62%|66.67%|43.91%|39.24%|—|
|qwen3b|512|6|Joint / operation specialist|26.04%|86.46%|21.92%|21.18%|—|
|qwen3b|512|6|Sequence specialist / operation specialist|65.28%|74.65%|45.48%|46.18%|47.12%|
|qwen3b|512|8|Joint / joint|9.72%|55.56%|6.73%|3.12%|—|
|qwen3b|512|8|Sequence specialist / joint|40.97%|45.49%|19.84%|15.28%|—|
|qwen3b|512|8|Joint / operation specialist|10.42%|65.97%|6.11%|2.08%|—|
|qwen3b|512|8|Sequence specialist / operation specialist|42.01%|55.90%|23.03%|19.79%|18.11%|
|qwen32b|256|all|Joint / joint|96.67%|84.65%|81.71%|83.19%|—|
|qwen32b|256|all|Sequence specialist / joint|96.39%|84.31%|81.22%|82.57%|—|
|qwen32b|256|all|Joint / operation specialist|98.06%|94.10%|92.26%|92.36%|—|
|qwen32b|256|all|Sequence specialist / operation specialist|97.99%|94.17%|92.31%|92.43%|92.31%|
|qwen32b|256|3|Joint / joint|100.00%|100.00%|100.00%|100.00%|—|
|qwen32b|256|3|Sequence specialist / joint|100.00%|100.00%|100.00%|100.00%|—|
|qwen32b|256|3|Joint / operation specialist|100.00%|100.00%|100.00%|100.00%|—|
|qwen32b|256|3|Sequence specialist / operation specialist|100.00%|100.00%|100.00%|100.00%|100.00%|
|qwen32b|256|4|Joint / joint|100.00%|96.53%|96.53%|96.53%|—|
|qwen32b|256|4|Sequence specialist / joint|99.31%|95.83%|95.17%|95.49%|—|
|qwen32b|256|4|Joint / operation specialist|100.00%|96.88%|96.88%|96.88%|—|
|qwen32b|256|4|Sequence specialist / operation specialist|99.65%|96.88%|96.56%|96.53%|96.56%|
|qwen32b|256|5|Joint / joint|95.49%|85.76%|81.86%|85.76%|—|
|qwen32b|256|5|Sequence specialist / joint|91.32%|85.07%|77.75%|81.25%|—|
|qwen32b|256|5|Joint / operation specialist|99.31%|91.67%|91.07%|91.67%|—|
|qwen32b|256|5|Sequence specialist / operation specialist|95.83%|92.01%|88.22%|88.19%|88.19%|
|qwen32b|256|6|Joint / joint|97.57%|77.78%|75.85%|77.78%|—|
|qwen32b|256|6|Sequence specialist / joint|95.83%|77.08%|73.83%|75.69%|—|
|qwen32b|256|6|Joint / operation specialist|100.00%|92.01%|92.01%|92.01%|—|
|qwen32b|256|6|Sequence specialist / operation specialist|98.61%|92.01%|90.78%|90.62%|90.78%|
|qwen32b|256|8|Joint / joint|90.28%|63.19%|56.02%|55.90%|—|
|qwen32b|256|8|Sequence specialist / joint|95.49%|63.54%|60.56%|60.42%|—|
|qwen32b|256|8|Joint / operation specialist|90.97%|89.93%|81.90%|81.25%|—|
|qwen32b|256|8|Sequence specialist / operation specialist|95.83%|89.93%|86.49%|86.81%|86.49%|
|qwen32b|512|all|Joint / joint|96.39%|86.67%|83.37%|85.35%|—|
|qwen32b|512|all|Sequence specialist / joint|96.11%|86.74%|83.27%|85.21%|—|
|qwen32b|512|all|Joint / operation specialist|98.26%|94.86%|93.20%|93.33%|—|
|qwen32b|512|all|Sequence specialist / operation specialist|98.06%|94.86%|93.06%|93.19%|93.12%|
|qwen32b|512|3|Joint / joint|100.00%|100.00%|100.00%|100.00%|—|
|qwen32b|512|3|Sequence specialist / joint|100.00%|100.00%|100.00%|100.00%|—|
|qwen32b|512|3|Joint / operation specialist|100.00%|100.00%|100.00%|100.00%|—|
|qwen32b|512|3|Sequence specialist / operation specialist|100.00%|100.00%|100.00%|100.00%|100.00%|
|qwen32b|512|4|Joint / joint|100.00%|96.18%|96.18%|96.18%|—|
|qwen32b|512|4|Sequence specialist / joint|100.00%|96.18%|96.18%|96.18%|—|
|qwen32b|512|4|Joint / operation specialist|100.00%|97.92%|97.92%|97.92%|—|
|qwen32b|512|4|Sequence specialist / operation specialist|100.00%|97.92%|97.92%|97.92%|97.59%|
|qwen32b|512|5|Joint / joint|95.49%|85.76%|81.91%|85.76%|—|
|qwen32b|512|5|Sequence specialist / joint|91.32%|85.07%|77.85%|81.60%|—|
|qwen32b|512|5|Joint / operation specialist|99.31%|92.71%|92.11%|92.71%|—|
|qwen32b|512|5|Sequence specialist / operation specialist|95.83%|92.71%|88.94%|89.24%|89.19%|
|qwen32b|512|6|Joint / joint|97.57%|83.33%|81.13%|83.33%|—|
|qwen32b|512|6|Sequence specialist / joint|96.18%|84.03%|80.62%|82.29%|—|
|qwen32b|512|6|Joint / operation specialist|100.00%|93.40%|93.40%|93.40%|—|
|qwen32b|512|6|Sequence specialist / operation specialist|98.26%|93.40%|91.84%|91.67%|91.51%|
|qwen32b|512|8|Joint / joint|88.89%|68.06%|59.12%|61.46%|—|
|qwen32b|512|8|Sequence specialist / joint|93.06%|68.40%|63.15%|65.97%|—|
|qwen32b|512|8|Joint / operation specialist|92.01%|90.28%|83.03%|82.64%|—|
|qwen32b|512|8|Sequence specialist / operation specialist|96.18%|90.28%|87.08%|87.15%|87.70%|
