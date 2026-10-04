# New-program confirmation results
Data were frozen before any actual local-context model inference:100 new tool compositions x4 inputs. This tests neither learning new tools nor real-agent tasks. All models use fixed 512-step checkpoints.
J/J uses the jointly trained model for both components; S/E uses specialists for names and operations. full retains all history; local gives only the current tool and actual state to the operation component.

|Model|Comparison|Length|New full success|Control full success|Difference pp|Three seed differences pp|
|---|---|---|---:|---:|---:|---|
|qwen3b|JJ local versus JJ full|all|39.67%|35.67%|+4.00|+3.50 / +3.75 / +4.75|
|qwen3b|JJ local versus JJ full|3|85.42%|83.33%|+2.08|+6.25 / +0.00 / +0.00|
|qwen3b|JJ local versus JJ full|4|57.08%|50.42%|+6.67|+6.25 / +3.75 / +10.00|
|qwen3b|JJ local versus JJ full|5|30.00%|27.50%|+2.50|+0.00 / +3.75 / +3.75|
|qwen3b|JJ local versus JJ full|6|20.00%|12.92%|+7.08|+5.00 / +7.50 / +8.75|
|qwen3b|JJ local versus JJ full|8|5.83%|4.17%|+1.67|+0.00 / +3.75 / +1.25|
|qwen3b|SE local versus SE full|all|62.25%|51.17%|+11.08|+23.25 / +1.25 / +8.75|
|qwen3b|SE local versus SE full|3|82.50%|81.25%|+1.25|+3.75 / +0.00 / +0.00|
|qwen3b|SE local versus SE full|4|75.83%|69.58%|+6.25|+10.00 / +3.75 / +5.00|
|qwen3b|SE local versus SE full|5|63.75%|47.08%|+16.67|+35.00 / +0.00 / +15.00|
|qwen3b|SE local versus SE full|6|63.33%|47.92%|+15.42|+35.00 / +0.00 / +11.25|
|qwen3b|SE local versus SE full|8|25.83%|10.00%|+15.83|+32.50 / +2.50 / +12.50|
|qwen3b|SE local versus JJ local|all|62.25%|39.67%|+22.58|+43.25 / +0.00 / +24.50|
|qwen3b|SE local versus JJ local|3|82.50%|85.42%|-2.92|+6.25 / -26.25 / +11.25|
|qwen3b|SE local versus JJ local|4|75.83%|57.08%|+18.75|+43.75 / -3.75 / +16.25|
|qwen3b|SE local versus JJ local|5|63.75%|30.00%|+33.75|+73.75 / +10.00 / +17.50|
|qwen3b|SE local versus JJ local|6|63.33%|20.00%|+43.33|+62.50 / +21.25 / +46.25|
|qwen3b|SE local versus JJ local|8|25.83%|5.83%|+20.00|+30.00 / -1.25 / +31.25|
|qwen3b|SE full versus JJ full|all|51.17%|35.67%|+15.50|+23.50 / +2.50 / +20.50|
|qwen3b|SE full versus JJ full|3|81.25%|83.33%|-2.08|+8.75 / -26.25 / +11.25|
|qwen3b|SE full versus JJ full|4|69.58%|50.42%|+19.17|+40.00 / -3.75 / +21.25|
|qwen3b|SE full versus JJ full|5|47.08%|27.50%|+19.58|+38.75 / +13.75 / +6.25|
|qwen3b|SE full versus JJ full|6|47.92%|12.92%|+35.00|+32.50 / +28.75 / +43.75|
|qwen3b|SE full versus JJ full|8|10.00%|4.17%|+5.83|-2.50 / +0.00 / +20.00|
|qwen32b|JJ local versus JJ full|all|93.92%|79.58%|+14.33|+27.00 / +7.00 / +9.00|
|qwen32b|JJ local versus JJ full|3|100.00%|97.50%|+2.50|+2.50 / +0.00 / +5.00|
|qwen32b|JJ local versus JJ full|4|100.00%|95.42%|+4.58|+11.25 / +1.25 / +1.25|
|qwen32b|JJ local versus JJ full|5|98.33%|83.75%|+14.58|+33.75 / +5.00 / +5.00|
|qwen32b|JJ local versus JJ full|6|96.67%|73.75%|+22.92|+45.00 / +8.75 / +15.00|
|qwen32b|JJ local versus JJ full|8|74.58%|47.50%|+27.08|+42.50 / +20.00 / +18.75|
|qwen32b|SE local versus SE full|all|96.00%|90.75%|+5.25|+7.00 / +8.00 / +0.75|
|qwen32b|SE local versus SE full|3|100.00%|100.00%|+0.00|+0.00 / +0.00 / +0.00|
|qwen32b|SE local versus SE full|4|100.00%|100.00%|+0.00|+0.00 / +0.00 / +0.00|
|qwen32b|SE local versus SE full|5|99.17%|92.08%|+7.08|+10.00 / +11.25 / +0.00|
|qwen32b|SE local versus SE full|6|96.25%|89.17%|+7.08|+13.75 / +7.50 / +0.00|
|qwen32b|SE local versus SE full|8|84.58%|72.50%|+12.08|+11.25 / +21.25 / +3.75|
|qwen32b|SE local versus JJ local|all|96.00%|93.92%|+2.08|-3.50 / +2.25 / +7.50|
|qwen32b|SE local versus JJ local|3|100.00%|100.00%|+0.00|+0.00 / +0.00 / +0.00|
|qwen32b|SE local versus JJ local|4|100.00%|100.00%|+0.00|+0.00 / +0.00 / +0.00|
|qwen32b|SE local versus JJ local|5|99.17%|98.33%|+0.83|+1.25 / +0.00 / +1.25|
|qwen32b|SE local versus JJ local|6|96.25%|96.67%|-0.42|-11.25 / +5.00 / +5.00|
|qwen32b|SE local versus JJ local|8|84.58%|74.58%|+10.00|-7.50 / +6.25 / +31.25|
|qwen32b|SE full versus JJ full|all|90.75%|79.58%|+11.17|+16.50 / +1.25 / +15.75|
|qwen32b|SE full versus JJ full|3|100.00%|97.50%|+2.50|+2.50 / +0.00 / +5.00|
|qwen32b|SE full versus JJ full|4|100.00%|95.42%|+4.58|+11.25 / +1.25 / +1.25|
|qwen32b|SE full versus JJ full|5|92.08%|83.75%|+8.33|+25.00 / -6.25 / +6.25|
|qwen32b|SE full versus JJ full|6|89.17%|73.75%|+15.42|+20.00 / +6.25 / +20.00|
|qwen32b|SE full versus JJ full|8|72.50%|47.50%|+25.00|+23.75 / +5.00 / +46.25|

See analysis/comparisons.json for per-seed subtask accuracies, raw correct/incorrect counts, and program-clustered intervals; analysis/completion-audit.json audits all actual inputs and outputs.
