# Lower learning rate and instruction-model supplement

Registered before final formal scores for the new models were visible: symmetric 1e-4 learning rates for 3B/32B versus the original 3e-4 recipe, and 32B-Instruct at 3e-4 with the official chat template. Each flat/macro group uses three seeds, 512 steps, and batch size 32. Learning rate and stopping steps were not tuned on test scores. Intermediate adapters are retained; this comparison uses fixed final evaluation.

| Model | Condition | Tool definitions supplied | Long-composition answer correct | Complete trajectory correct | Stops after two correct tools |
|---|---|---|---:|---:|---:|
| qwen3b | flat | no_definitions | 0.09% | 0.00% | 73.26% |
| qwen3b | flat | definitions | 1.13% | 0.00% | 5.47% |
| qwen3b | macro | no_definitions | 13.72% | 12.33% | 0.17% |
| qwen3b | macro | definitions | 8.16% | 7.03% | 1.30% |
| qwen32b | flat | no_definitions | 30.38% | 30.03% | 0.17% |
| qwen32b | flat | definitions | 87.50% | 87.15% | 0.00% |
| qwen32b | macro | no_definitions | 55.56% | 53.65% | 0.00% |
| qwen32b | macro | definitions | 79.17% | 78.47% | 0.00% |
| qwen32b-instruct | flat | no_definitions | 34.64% | 34.55% | 7.47% |
| qwen32b-instruct | flat | definitions | 57.47% | 57.38% | 2.78% |
| qwen32b-instruct | macro | no_definitions | 65.19% | 64.76% | 0.00% |
| qwen32b-instruct | macro | definitions | 59.11% | 58.59% | 0.35% |
| qwen32b-instruct | frozen | no_definitions | 0.00% | 0.00% | 0.00% |
| qwen32b-instruct | frozen | definitions | 0.00% | 0.00% | 0.00% |

The frozen baseline receives one deterministic evaluation, not three training seeds. Without definitions, the base model does not know the artificial color mapping; low scores do not establish low capability. Results with and without definitions are different conditions. Base and Instruct differ in templates and post-training, so differences cannot all be attributed to parameter scale or prior stability. The low-learning-rate 3B group uses a 5090 while the original 3B group uses a PRO6000, limiting a purely learning-rate causal interpretation. Both 32B learning-rate groups use PRO6000 GPUs.

See [supplementary statistics](analysis/supplement-results.json) for all seed differences, 95% t intervals, example-level checks, training counts, and 126 checkpoint hashes. This file is a summary; interpret it with the main report and CONCLUSIONS.md.
