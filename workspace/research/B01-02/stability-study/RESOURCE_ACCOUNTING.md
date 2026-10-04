# Training exposure and resource accounting
This study reuses trained weights, with no retraining for the main matrix. The table gives actual counts from the original training; each full 512-step condition sees 16384 examples.
|Model|Seed|Joint 512-step supervised tokens|Sequence fraction|Operation fraction|Total supervised tokens for two 256-step specialists|Trainable parameters per adapter|
|---|---:|---:|---:|---:|---:|---:|
|qwen3b|11|1001552|11.14%|88.86%|500776|29933568|
|qwen3b|22|1001552|11.14%|88.86%|500776|29933568|
|qwen3b|33|1001552|11.14%|88.86%|500776|29933568|
|qwen32b|11|1001552|11.14%|88.86%|500776|134217728|
|qwen32b|22|1001552|11.14%|88.86%|500776|134217728|
|qwen32b|33|1001552|11.14%|88.86%|500776|134217728|

Joint training averages loss over valid target tokens; specialists average over their own supervised components. Sequence fraction is a target-token count fraction, not measured gradient contribution, and alone does not establish gradient conflict or diluted learning.
Two 256-step specialists and one 512-step joint model have equal cumulative example exposure/optimizer steps, but differ in repeated-example allocation, supervised-token counts, and parameter storage. Two specialist adapters contain twice the parameters of one adapter. Weight-balanced or capacity-matched experiments are still needed to exclude these explanations.
Total allocated GPU wall time for completed new evaluation jobs: 31.62 GPU-hours, including loading, initial archived calibration, and failed jobs, but excluding unfinished jobs. This is not active GPU-kernel time.

|Stage|Completed jobs|Allocated GPU-hours|
|---|---:|---:|
|main|26|22.31|
|context|26|5.49|
|fresh|24|3.77|
|initial_calibration|2|0.05|
