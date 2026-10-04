# Two whole-task components: complete name order and all emitted calls

Per trajectory A: full emitted name list equals requested name list. B: at least one emitted macro and EVERY emitted macro completely/correctly expands its actual legal name, including local numeric transitions. Missing calls fail A but are not imaginary B errors. Unknown label fails B. No oracle or new inference. All A&B matched strict success in every group. Product shown per training seed then averaged; pooled product also retained. Same-data descriptive independence check, not held-out prediction or proof of independence. B has variable emitted-call exposure and is not all-required-calls oracle ability.

## main

### qwen1.5b
|Calls|A: complete order correct|B: all emitted calls expanded correctly|A×B within seed|Actual whole task|
|---|---:|---:|---:|---:|
| 3 | 59.38% | 98.96% | 58.68% | 58.33% |
| 4 | 24.74% | 95.57% | 23.61% | 21.88% |
| 5 | 13.80% | 86.20% | 11.16% | 9.11% |

### qwen3b
|Calls|A: complete order correct|B: all emitted calls expanded correctly|A×B within seed|Actual whole task|
|---|---:|---:|---:|---:|
| 3 | 92.97% | 95.05% | 88.29% | 88.02% |
| 4 | 78.12% | 87.24% | 67.57% | 66.15% |
| 5 | 48.44% | 67.19% | 31.77% | 25.00% |

### qwen7b
|Calls|A: complete order correct|B: all emitted calls expanded correctly|A×B within seed|Actual whole task|
|---|---:|---:|---:|---:|
| 3 | 91.93% | 97.40% | 89.42% | 89.32% |
| 4 | 69.01% | 87.50% | 59.73% | 56.51% |
| 5 | 47.66% | 75.78% | 33.35% | 27.86% |

### qwen32b
|Calls|A: complete order correct|B: all emitted calls expanded correctly|A×B within seed|Actual whole task|
|---|---:|---:|---:|---:|
| 3 | 96.09% | 100.00% | 96.09% | 96.09% |
| 4 | 74.22% | 98.96% | 73.71% | 73.18% |
| 5 | 53.65% | 96.09% | 50.23% | 49.74% |

## independent

### qwen1.5b
|Calls|A: complete order correct|B: all emitted calls expanded correctly|A×B within seed|Actual whole task|
|---|---:|---:|---:|---:|
| 3 | 53.47% | 98.96% | 52.78% | 52.43% |
| 4 | 27.08% | 88.54% | 23.85% | 21.18% |
| 5 | 7.64% | 88.89% | 6.34% | 5.90% |
| 6 | 2.43% | 76.04% | 1.87% | 0.69% |
| 8 | 1.04% | 58.33% | 0.35% | 1.04% |

### qwen3b
|Calls|A: complete order correct|B: all emitted calls expanded correctly|A×B within seed|Actual whole task|
|---|---:|---:|---:|---:|
| 3 | 86.46% | 97.22% | 84.07% | 83.68% |
| 4 | 75.35% | 84.03% | 61.94% | 60.76% |
| 5 | 51.39% | 69.44% | 34.28% | 28.47% |
| 6 | 31.25% | 55.56% | 14.47% | 9.38% |
| 8 | 10.07% | 40.28% | 2.49% | 2.08% |

### qwen7b
|Calls|A: complete order correct|B: all emitted calls expanded correctly|A×B within seed|Actual whole task|
|---|---:|---:|---:|---:|
| 3 | 90.97% | 95.83% | 86.98% | 86.81% |
| 4 | 67.71% | 81.94% | 53.62% | 52.08% |
| 5 | 45.14% | 71.53% | 29.54% | 23.61% |
| 6 | 36.11% | 73.96% | 24.60% | 22.57% |
| 8 | 17.01% | 40.28% | 3.48% | 0.00% |

### qwen32b
|Calls|A: complete order correct|B: all emitted calls expanded correctly|A×B within seed|Actual whole task|
|---|---:|---:|---:|---:|
| 3 | 94.10% | 100.00% | 94.10% | 94.10% |
| 4 | 73.26% | 98.26% | 72.14% | 71.53% |
| 5 | 59.03% | 98.96% | 58.66% | 57.99% |
| 6 | 32.99% | 96.53% | 32.25% | 32.64% |
| 8 | 27.78% | 89.24% | 24.67% | 24.65% |
