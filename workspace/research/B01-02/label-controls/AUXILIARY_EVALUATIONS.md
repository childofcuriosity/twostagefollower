# Supplementary evaluations retained from the original trainer
These outputs all come from the existing workflow of the original trainer; no extra model conditions were run. Primary conclusions still use the original tests without tool definitions and the fixed-512-step independent set. This table does not substitute better-performing conditions for the primary results.

## Original tests with tool definitions (final step512)

|Model|Subset|Original STEP|Original NAME|Position numbering|Fixed aliases|
|---|---|---:|---:|---:|---:|
|qwen7b|iid|96.09%|94.53%|88.02%|95.83%|
|qwen7b|ood|16.67%|50.09%|30.12%|42.01%|
|qwen7b|pressure|20.14%|59.72%|34.03%|54.17%|
|qwen32b|iid|94.27%|100.00%|98.44%|100.00%|
|qwen32b|ood|63.45%|71.70%|81.16%|81.77%|
|qwen32b|pressure|75.00%|81.25%|91.67%|82.64%|

Per-seed and per-subset development scores at every checkpoint are saved in analysis/auxiliary-audit.json and are not pooled with formal tests as additional independent samples.
