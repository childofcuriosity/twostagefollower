# Two separately trained subtasks and joint execution

Independent confirmation set; compute products separately for three seeds, then average. A and B come from different specialist checkpoints. Both subtasks correct on the same example is a paired statistic from two oracle evaluations, not an executed two-model composition. Only cells with all three seeds complete are shown.


## qwen1.5b
|Calls|A sequence task|B all-expansions task|A x B|Both subtasks correct on the same example|Joint autonomous execution|
|---|---:|---:|---:|---:|---:|
| 3 | 82.64% | 99.31% | 82.11% | 82.29% | 92.01% |
| 4 | 73.61% | 90.62% | 66.19% | 68.06% | 61.46% |
| 5 | 40.62% | 73.26% | 29.42% | 28.82% | 31.94% |
| 6 | 35.42% | 75.35% | 24.62% | 25.00% | 17.01% |
| 8 | 33.68% | 41.67% | 13.40% | 15.28% | 9.72% |

## qwen3b
|Calls|A sequence task|B all-expansions task|A x B|Both subtasks correct on the same example|Joint autonomous execution|
|---|---:|---:|---:|---:|---:|
| 3 | 84.72% | 95.49% | 80.69% | 80.21% | 85.76% |
| 4 | 82.29% | 95.83% | 78.46% | 78.82% | 61.11% |
| 5 | 70.14% | 84.03% | 57.10% | 55.21% | 34.03% |
| 6 | 64.93% | 76.39% | 47.13% | 46.18% | 20.83% |
| 8 | 41.32% | 45.83% | 18.62% | 18.75% | 2.78% |

## qwen7b
|Calls|A sequence task|B all-expansions task|A x B|Both subtasks correct on the same example|Joint autonomous execution|
|---|---:|---:|---:|---:|---:|
| 3 | 100.00% | 98.96% | 98.96% | 98.96% | 97.22% |
| 4 | 93.75% | 85.07% | 79.68% | 80.21% | 84.03% |
| 5 | 67.36% | 57.64% | 44.94% | 42.36% | 50.35% |
| 6 | 51.39% | 52.43% | 26.69% | 26.04% | 37.15% |
| 8 | 29.86% | 9.38% | 3.00% | 1.39% | 13.89% |

## qwen32b
|Calls|A sequence task|B all-expansions task|A x B|Both subtasks correct on the same example|Joint autonomous execution|
|---|---:|---:|---:|---:|---:|
| 3 | 100.00% | 100.00% | 100.00% | 100.00% | 100.00% |
| 4 | 99.65% | 97.92% | 97.59% | 97.57% | 96.18% |
| 5 | 96.18% | 92.71% | 89.19% | 88.89% | 85.76% |
| 6 | 98.26% | 93.06% | 91.51% | 91.32% | 83.33% |
| 8 | 96.53% | 90.62% | 87.70% | 87.50% | 61.46% |
