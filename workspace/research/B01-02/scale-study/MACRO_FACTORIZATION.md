# Macro-level statistics from existing trajectories

Whole macro J: correct name at required position AND complete correct expansion of that emitted name with locally valid arithmetic. Missing=incorrect. Prediction per model/seed/length: p(J)^L estimated on other four program folds. Conditional adjacency restricted to both segments actually emitted excludes missing-tail failures. Correlation descriptive, no causal mimicry claim; difficult programs and positions can confound. Position standardized rates use overlap positions only, still not program/seed adjusted.

Independent confirmation: each row contains 288 trajectories from 24 programs × four inputs × three seeds. All predictions use cross-validation grouped by program.


## qwen1.5b
|Length|Single-macro accuracy|Product across macros|Original separate A/B product|Actual whole task|Current error after correct macro|Current error after incorrect macro|
|---|---:|---:|---:|---:|---:|---:|
| 3 | 81.71% | 56.02% | 56.03% | 52.43% | 5.43% (24/442) | No observations |
| 4 | 69.36% | 23.44% | 22.25% | 21.18% | 13.11% (75/572) | 17.65% (3/17) |
| 5 | 53.75% | 4.47% | 4.35% | 5.90% | 27.58% (182/660) | 89.04% (65/73) |
| 6 | 44.79% | 1.00% | 0.86% | 0.69% | 30.79% (206/669) | 80.67% (96/119) |
| 8 | 33.68% | 0.02% | 0.01% | 1.04% | 34.33% (240/699) | 91.59% (316/345) |

## qwen3b
|Length|Single-macro accuracy|Product across macros|Original separate A/B product|Actual whole task|Current error after correct macro|Current error after incorrect macro|
|---|---:|---:|---:|---:|---:|---:|
| 3 | 92.71% | 81.78% | 81.82% | 83.68% | 4.47% (24/537) | No observations |
| 4 | 87.67% | 59.81% | 59.09% | 60.76% | 7.55% (58/768) | 29.41% (5/17) |
| 5 | 76.11% | 26.64% | 25.64% | 28.47% | 15.37% (140/911) | 46.38% (32/69) |
| 6 | 61.28% | 5.66% | 5.23% | 9.38% | 22.09% (209/946) | 79.76% (134/168) |
| 8 | 45.10% | 0.30% | 0.16% | 2.08% | 28.09% (266/947) | 84.48% (381/451) |

## qwen7b
|Length|Single-macro accuracy|Product across macros|Original separate A/B product|Actual whole task|Current error after correct macro|Current error after incorrect macro|
|---|---:|---:|---:|---:|---:|---:|
| 3 | 94.21% | 84.96% | 85.00% | 86.81% | 4.36% (24/550) | No observations |
| 4 | 86.02% | 55.93% | 56.05% | 52.08% | 8.58% (64/746) | 0.00% (0/21) |
| 5 | 71.88% | 21.12% | 21.12% | 23.61% | 17.96% (157/874) | 48.28% (28/58) |
| 6 | 68.40% | 11.90% | 11.01% | 22.57% | 16.20% (166/1025) | 66.98% (71/106) |
| 8 | 46.70% | 0.37% | 0.28% | 0.00% | 28.82% (283/982) | 80.09% (362/452) |

## qwen32b
|Length|Single-macro accuracy|Product across macros|Original separate A/B product|Actual whole task|Current error after correct macro|Current error after incorrect macro|
|---|---:|---:|---:|---:|---:|---:|
| 3 | 98.03% | 94.24% | 94.24% | 94.10% | 0.00% (0/559) | No observations |
| 4 | 91.84% | 72.16% | 72.18% | 71.53% | 1.92% (15/781) | 0.00% (0/4) |
| 5 | 85.14% | 47.34% | 47.35% | 57.99% | 5.46% (54/989) | 72.73% (8/11) |
| 6 | 74.42% | 21.10% | 21.01% | 32.64% | 8.54% (92/1077) | 69.05% (29/42) |
| 8 | 65.84% | 9.45% | 9.54% | 24.65% | 8.57% (112/1307) | 73.64% (95/129) |

The last two columns include only adjacent macros that were both emitted; missing calls are excluded. These conditional associations do not control program difficulty. An incorrect preceding macro may cause persistent positional misalignment, which is not necessarily error copying. JSON also retains missing-call and position-standardized results.

All length-specific results for the original 3–5-call set are also in analysis/macro-factorization.json.
