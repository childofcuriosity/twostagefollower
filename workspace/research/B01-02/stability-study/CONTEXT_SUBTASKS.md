# Context controls: two subtasks in actual outputs
Every column comes from the same actual execution without correct-answer assistance. Correct sequence requires all names in order and correct termination. All generated operations correct requires correct expansion of every emitted call; missing calls fail the sequence column.
This differs from oracle tests where a program supplies the correct other component; see ORACLE_PREDICTION_CHECK.md. Products below are computed by seed before averaging and do not prove internal independence.
Three seeds per condition;480 earlier examples per seed and 400 new-program examples per seed. Repeating the same examples across seeds/conditions does not create that many independent programs.

## Existing program set

|Model|Name writer / operation writer|Operation context|Tools|Correct sequence|All generated operations correct|Product of both columns|Full-task success|
|---|---|---|---|---:|---:|---:|---:|
|qwen3b|Joint / joint|Full history|all|45.83%|83.82%|38.54%|40.49%|
|qwen3b|Joint / joint|Current tool + actual state|all|46.32%|100.00%|46.32%|46.32%|
|qwen3b|Sequence specialist / joint|Full history|all|68.33%|78.33%|54.04%|53.89%|
|qwen3b|Sequence specialist / joint|Current tool + actual state|all|68.26%|100.00%|68.26%|68.26%|
|qwen3b|Joint / operation specialist|Full history|all|45.76%|87.43%|39.85%|40.28%|
|qwen3b|Joint / operation specialist|Current tool + actual state|all|46.32%|100.00%|46.32%|46.32%|
|qwen3b|Sequence specialist / operation specialist|Full history|all|68.47%|81.32%|54.36%|55.83%|
|qwen3b|Sequence specialist / operation specialist|Current tool + actual state|all|68.26%|100.00%|68.26%|68.26%|
|qwen32b|Joint / joint|Full history|all|96.39%|86.67%|83.37%|85.35%|
|qwen32b|Joint / joint|Current tool + actual state|all|98.40%|100.00%|98.40%|98.40%|
|qwen32b|Sequence specialist / joint|Full history|all|96.11%|86.74%|83.27%|85.21%|
|qwen32b|Sequence specialist / joint|Current tool + actual state|all|98.19%|100.00%|98.19%|98.19%|
|qwen32b|Joint / operation specialist|Full history|all|98.26%|94.86%|93.20%|93.33%|
|qwen32b|Joint / operation specialist|Current tool + actual state|all|98.40%|100.00%|98.40%|98.40%|
|qwen32b|Sequence specialist / operation specialist|Full history|all|98.06%|94.86%|93.06%|93.19%|
|qwen32b|Sequence specialist / operation specialist|Current tool + actual state|all|98.19%|100.00%|98.19%|98.19%|
|qwen3b|Joint / joint|Full history|3|86.11%|99.65%|85.78%|85.76%|
|qwen3b|Joint / joint|Current tool + actual state|3|86.11%|100.00%|86.11%|86.11%|
|qwen3b|Sequence specialist / joint|Full history|3|84.03%|99.65%|83.68%|83.68%|
|qwen3b|Sequence specialist / joint|Current tool + actual state|3|84.03%|100.00%|84.03%|84.03%|
|qwen3b|Joint / operation specialist|Full history|3|86.11%|96.18%|82.81%|82.29%|
|qwen3b|Joint / operation specialist|Current tool + actual state|3|86.11%|100.00%|86.11%|86.11%|
|qwen3b|Sequence specialist / operation specialist|Full history|3|84.03%|96.18%|80.54%|80.21%|
|qwen3b|Sequence specialist / operation specialist|Current tool + actual state|3|84.03%|100.00%|84.03%|84.03%|
|qwen32b|Joint / joint|Full history|3|100.00%|100.00%|100.00%|100.00%|
|qwen32b|Joint / joint|Current tool + actual state|3|100.00%|100.00%|100.00%|100.00%|
|qwen32b|Sequence specialist / joint|Full history|3|100.00%|100.00%|100.00%|100.00%|
|qwen32b|Sequence specialist / joint|Current tool + actual state|3|100.00%|100.00%|100.00%|100.00%|
|qwen32b|Joint / operation specialist|Full history|3|100.00%|100.00%|100.00%|100.00%|
|qwen32b|Joint / operation specialist|Current tool + actual state|3|100.00%|100.00%|100.00%|100.00%|
|qwen32b|Sequence specialist / operation specialist|Full history|3|100.00%|100.00%|100.00%|100.00%|
|qwen32b|Sequence specialist / operation specialist|Current tool + actual state|3|100.00%|100.00%|100.00%|100.00%|
|qwen3b|Joint / joint|Full history|4|64.24%|96.88%|62.18%|61.11%|
|qwen3b|Joint / joint|Current tool + actual state|4|64.93%|100.00%|64.93%|64.93%|
|qwen3b|Sequence specialist / joint|Full history|4|80.90%|95.49%|77.76%|76.39%|
|qwen3b|Sequence specialist / joint|Current tool + actual state|4|80.90%|100.00%|80.90%|80.90%|
|qwen3b|Joint / operation specialist|Full history|4|64.24%|97.57%|62.87%|62.50%|
|qwen3b|Joint / operation specialist|Current tool + actual state|4|64.93%|100.00%|64.93%|64.93%|
|qwen3b|Sequence specialist / operation specialist|Full history|4|80.90%|96.18%|77.34%|77.78%|
|qwen3b|Sequence specialist / operation specialist|Current tool + actual state|4|80.90%|100.00%|80.90%|80.90%|
|qwen32b|Joint / joint|Full history|4|100.00%|96.18%|96.18%|96.18%|
|qwen32b|Joint / joint|Current tool + actual state|4|100.00%|100.00%|100.00%|100.00%|
|qwen32b|Sequence specialist / joint|Full history|4|100.00%|96.18%|96.18%|96.18%|
|qwen32b|Sequence specialist / joint|Current tool + actual state|4|100.00%|100.00%|100.00%|100.00%|
|qwen32b|Joint / operation specialist|Full history|4|100.00%|97.92%|97.92%|97.92%|
|qwen32b|Joint / operation specialist|Current tool + actual state|4|100.00%|100.00%|100.00%|100.00%|
|qwen32b|Sequence specialist / operation specialist|Full history|4|100.00%|97.92%|97.92%|97.92%|
|qwen32b|Sequence specialist / operation specialist|Current tool + actual state|4|100.00%|100.00%|100.00%|100.00%|
|qwen3b|Joint / joint|Full history|5|43.06%|87.50%|38.12%|32.64%|
|qwen3b|Joint / joint|Current tool + actual state|5|43.75%|100.00%|43.75%|43.75%|
|qwen3b|Sequence specialist / joint|Full history|5|70.14%|84.38%|59.76%|54.86%|
|qwen3b|Sequence specialist / joint|Current tool + actual state|5|70.14%|100.00%|70.14%|70.14%|
|qwen3b|Joint / operation specialist|Full history|5|42.01%|90.97%|37.29%|33.33%|
|qwen3b|Joint / operation specialist|Current tool + actual state|5|43.75%|100.00%|43.75%|43.75%|
|qwen3b|Sequence specialist / operation specialist|Full history|5|70.14%|83.68%|56.68%|55.21%|
|qwen3b|Sequence specialist / operation specialist|Current tool + actual state|5|70.14%|100.00%|70.14%|70.14%|
|qwen32b|Joint / joint|Full history|5|95.49%|85.76%|81.91%|85.76%|
|qwen32b|Joint / joint|Current tool + actual state|5|100.00%|100.00%|100.00%|100.00%|
|qwen32b|Sequence specialist / joint|Full history|5|91.32%|85.07%|77.85%|81.60%|
|qwen32b|Sequence specialist / joint|Current tool + actual state|5|96.53%|100.00%|96.53%|96.53%|
|qwen32b|Joint / operation specialist|Full history|5|99.31%|92.71%|92.11%|92.71%|
|qwen32b|Joint / operation specialist|Current tool + actual state|5|100.00%|100.00%|100.00%|100.00%|
|qwen32b|Sequence specialist / operation specialist|Full history|5|95.83%|92.71%|88.94%|89.24%|
|qwen32b|Sequence specialist / operation specialist|Current tool + actual state|5|96.53%|100.00%|96.53%|96.53%|
|qwen3b|Joint / joint|Full history|6|26.04%|79.51%|20.15%|19.79%|
|qwen3b|Joint / joint|Current tool + actual state|6|26.04%|100.00%|26.04%|26.04%|
|qwen3b|Sequence specialist / joint|Full history|6|65.62%|66.67%|43.91%|39.24%|
|qwen3b|Sequence specialist / joint|Current tool + actual state|6|65.28%|100.00%|65.28%|65.28%|
|qwen3b|Joint / operation specialist|Full history|6|26.04%|86.46%|21.92%|21.18%|
|qwen3b|Joint / operation specialist|Current tool + actual state|6|26.04%|100.00%|26.04%|26.04%|
|qwen3b|Sequence specialist / operation specialist|Full history|6|65.28%|74.65%|45.48%|46.18%|
|qwen3b|Sequence specialist / operation specialist|Current tool + actual state|6|65.28%|100.00%|65.28%|65.28%|
|qwen32b|Joint / joint|Full history|6|97.57%|83.33%|81.13%|83.33%|
|qwen32b|Joint / joint|Current tool + actual state|6|100.00%|100.00%|100.00%|100.00%|
|qwen32b|Sequence specialist / joint|Full history|6|96.18%|84.03%|80.62%|82.29%|
|qwen32b|Sequence specialist / joint|Current tool + actual state|6|98.26%|100.00%|98.26%|98.26%|
|qwen32b|Joint / operation specialist|Full history|6|100.00%|93.40%|93.40%|93.40%|
|qwen32b|Joint / operation specialist|Current tool + actual state|6|100.00%|100.00%|100.00%|100.00%|
|qwen32b|Sequence specialist / operation specialist|Full history|6|98.26%|93.40%|91.84%|91.67%|
|qwen32b|Sequence specialist / operation specialist|Current tool + actual state|6|98.26%|100.00%|98.26%|98.26%|
|qwen3b|Joint / joint|Full history|8|9.72%|55.56%|6.73%|3.12%|
|qwen3b|Joint / joint|Current tool + actual state|8|10.76%|100.00%|10.76%|10.76%|
|qwen3b|Sequence specialist / joint|Full history|8|40.97%|45.49%|19.84%|15.28%|
|qwen3b|Sequence specialist / joint|Current tool + actual state|8|40.97%|100.00%|40.97%|40.97%|
|qwen3b|Joint / operation specialist|Full history|8|10.42%|65.97%|6.11%|2.08%|
|qwen3b|Joint / operation specialist|Current tool + actual state|8|10.76%|100.00%|10.76%|10.76%|
|qwen3b|Sequence specialist / operation specialist|Full history|8|42.01%|55.90%|23.03%|19.79%|
|qwen3b|Sequence specialist / operation specialist|Current tool + actual state|8|40.97%|100.00%|40.97%|40.97%|
|qwen32b|Joint / joint|Full history|8|88.89%|68.06%|59.12%|61.46%|
|qwen32b|Joint / joint|Current tool + actual state|8|92.01%|100.00%|92.01%|92.01%|
|qwen32b|Sequence specialist / joint|Full history|8|93.06%|68.40%|63.15%|65.97%|
|qwen32b|Sequence specialist / joint|Current tool + actual state|8|96.18%|100.00%|96.18%|96.18%|
|qwen32b|Joint / operation specialist|Full history|8|92.01%|90.28%|83.03%|82.64%|
|qwen32b|Joint / operation specialist|Current tool + actual state|8|92.01%|100.00%|92.01%|92.01%|
|qwen32b|Sequence specialist / operation specialist|Full history|8|96.18%|90.28%|87.08%|87.15%|
|qwen32b|Sequence specialist / operation specialist|Current tool + actual state|8|96.18%|100.00%|96.18%|96.18%|

## Preregistered frozen new program set

|Model|Name writer / operation writer|Operation context|Tools|Correct sequence|All generated operations correct|Product of both columns|Full-task success|
|---|---|---|---|---:|---:|---:|---:|
|qwen3b|Joint / joint|Full history|all|40.25%|85.50%|34.40%|35.67%|
|qwen3b|Joint / joint|Current tool + actual state|all|39.67%|100.00%|39.67%|39.67%|
|qwen3b|Sequence specialist / operation specialist|Full history|all|62.75%|82.58%|50.29%|51.17%|
|qwen3b|Sequence specialist / operation specialist|Current tool + actual state|all|62.25%|100.00%|62.25%|62.25%|
|qwen32b|Joint / joint|Full history|all|92.17%|83.92%|77.19%|79.58%|
|qwen32b|Joint / joint|Current tool + actual state|all|93.92%|100.00%|93.92%|93.92%|
|qwen32b|Sequence specialist / operation specialist|Full history|all|95.58%|94.67%|90.56%|90.75%|
|qwen32b|Sequence specialist / operation specialist|Current tool + actual state|all|96.00%|100.00%|96.00%|96.00%|
|qwen3b|Joint / joint|Full history|3|85.42%|97.92%|83.46%|83.33%|
|qwen3b|Joint / joint|Current tool + actual state|3|85.42%|100.00%|85.42%|85.42%|
|qwen3b|Sequence specialist / operation specialist|Full history|3|82.50%|98.75%|81.25%|81.25%|
|qwen3b|Sequence specialist / operation specialist|Current tool + actual state|3|82.50%|100.00%|82.50%|82.50%|
|qwen32b|Joint / joint|Full history|3|100.00%|97.50%|97.50%|97.50%|
|qwen32b|Joint / joint|Current tool + actual state|3|100.00%|100.00%|100.00%|100.00%|
|qwen32b|Sequence specialist / operation specialist|Full history|3|100.00%|100.00%|100.00%|100.00%|
|qwen32b|Sequence specialist / operation specialist|Current tool + actual state|3|100.00%|100.00%|100.00%|100.00%|
|qwen3b|Joint / joint|Full history|4|57.08%|91.67%|51.99%|50.42%|
|qwen3b|Joint / joint|Current tool + actual state|4|57.08%|100.00%|57.08%|57.08%|
|qwen3b|Sequence specialist / operation specialist|Full history|4|75.83%|93.75%|70.56%|69.58%|
|qwen3b|Sequence specialist / operation specialist|Current tool + actual state|4|75.83%|100.00%|75.83%|75.83%|
|qwen32b|Joint / joint|Full history|4|100.00%|95.42%|95.42%|95.42%|
|qwen32b|Joint / joint|Current tool + actual state|4|100.00%|100.00%|100.00%|100.00%|
|qwen32b|Sequence specialist / operation specialist|Full history|4|100.00%|100.00%|100.00%|100.00%|
|qwen32b|Sequence specialist / operation specialist|Current tool + actual state|4|100.00%|100.00%|100.00%|100.00%|
|qwen3b|Joint / joint|Full history|5|30.42%|92.92%|28.82%|27.50%|
|qwen3b|Joint / joint|Current tool + actual state|5|30.00%|100.00%|30.00%|30.00%|
|qwen3b|Sequence specialist / operation specialist|Full history|5|65.83%|77.50%|48.45%|47.08%|
|qwen3b|Sequence specialist / operation specialist|Current tool + actual state|5|63.75%|100.00%|63.75%|63.75%|
|qwen32b|Joint / joint|Full history|5|96.67%|85.42%|82.61%|83.75%|
|qwen32b|Joint / joint|Current tool + actual state|5|98.33%|100.00%|98.33%|98.33%|
|qwen32b|Sequence specialist / operation specialist|Full history|5|99.17%|92.92%|92.17%|92.08%|
|qwen32b|Sequence specialist / operation specialist|Current tool + actual state|5|99.17%|100.00%|99.17%|99.17%|
|qwen3b|Joint / joint|Full history|6|22.50%|74.17%|16.44%|12.92%|
|qwen3b|Joint / joint|Current tool + actual state|6|20.00%|100.00%|20.00%|20.00%|
|qwen3b|Sequence specialist / operation specialist|Full history|6|63.75%|81.25%|49.89%|47.92%|
|qwen3b|Sequence specialist / operation specialist|Current tool + actual state|6|63.33%|100.00%|63.33%|63.33%|
|qwen32b|Joint / joint|Full history|6|94.58%|77.08%|72.24%|73.75%|
|qwen32b|Joint / joint|Current tool + actual state|6|96.67%|100.00%|96.67%|96.67%|
|qwen32b|Sequence specialist / operation specialist|Full history|6|93.75%|92.92%|87.53%|89.17%|
|qwen32b|Sequence specialist / operation specialist|Current tool + actual state|6|96.25%|100.00%|96.25%|96.25%|
|qwen3b|Joint / joint|Full history|8|5.83%|70.83%|4.30%|4.17%|
|qwen3b|Joint / joint|Current tool + actual state|8|5.83%|100.00%|5.83%|5.83%|
|qwen3b|Sequence specialist / operation specialist|Full history|8|25.83%|61.67%|14.17%|10.00%|
|qwen3b|Sequence specialist / operation specialist|Current tool + actual state|8|25.83%|100.00%|25.83%|25.83%|
|qwen32b|Joint / joint|Full history|8|69.58%|64.17%|44.11%|47.50%|
|qwen32b|Joint / joint|Current tool + actual state|8|74.58%|100.00%|74.58%|74.58%|
|qwen32b|Sequence specialist / operation specialist|Full history|8|85.00%|87.50%|74.50%|72.50%|
|qwen32b|Sequence specialist / operation specialist|Current tool + actual state|8|84.58%|100.00%|84.58%|84.58%|
