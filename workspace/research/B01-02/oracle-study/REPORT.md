# Second-stage oracle ablation results

Currently audited: 62400 outputs; 36/36 training jobs and corresponding evaluations have completion markers. See COMPLETION_AUDIT.md for completeness checks. Until counts reach 62400 and 36, this file is an interim result.

All models are Qwen2.5 Base, using the same 4096 training examples, LoRA configuration, 512 steps, and three seeds. The three conditions see identical text and differ only in loss masks, sharing the EndTool/Done protocol. Earlier macro-name/step results cannot be the sole same-format controls.

joint: the model generates sequence and operations. order_oracle: a program supplies correct names and the model generates operations. operation_oracle: the model selects names and termination, and a program executes the tools actually selected. Program-supplied content is not counted as prediction ability.

The table reports full-task accuracy. Expansion requires correct expansion of every required call; sequence prediction requires the complete correct names and correct termination. joint+oracle evaluates the same jointly trained checkpoint in the corresponding oracle environment; single-task+oracle evaluates a specialist checkpoint supervised only on that component.


## qwen1.5b / Original test: in-distribution short calls
|Calls|Joint free execution|Joint + sequence oracle|Single-task + sequence oracle|Joint + operation oracle|Single-task + operation oracle|
|---|---:|---:|---:|---:|---:|
| 1 | 100.00% (n=33) | 100.00% (n=33) | 100.00% (n=33) | 100.00% (n=33) | 100.00% (n=33) |
| 2 | 99.72% (n=351) | 99.72% (n=351) | 100.00% (n=351) | 100.00% (n=351) | 100.00% (n=351) |

## qwen3b / Original test: in-distribution short calls
|Calls|Joint free execution|Joint + sequence oracle|Single-task + sequence oracle|Joint + operation oracle|Single-task + operation oracle|
|---|---:|---:|---:|---:|---:|
| 1 | 100.00% (n=33) | 100.00% (n=33) | 100.00% (n=33) | 100.00% (n=33) | 100.00% (n=33) |
| 2 | 100.00% (n=351) | 100.00% (n=351) | 100.00% (n=351) | 100.00% (n=351) | 100.00% (n=351) |

## qwen7b / Original test: in-distribution short calls
|Calls|Joint free execution|Joint + sequence oracle|Single-task + sequence oracle|Joint + operation oracle|Single-task + operation oracle|
|---|---:|---:|---:|---:|---:|
| 1 | 100.00% (n=33) | 100.00% (n=33) | 100.00% (n=33) | 100.00% (n=33) | 100.00% (n=33) |
| 2 | 100.00% (n=351) | 100.00% (n=351) | 100.00% (n=351) | 100.00% (n=351) | 100.00% (n=351) |

## qwen32b / Original test: in-distribution short calls
|Calls|Joint free execution|Joint + sequence oracle|Single-task + sequence oracle|Joint + operation oracle|Single-task + operation oracle|
|---|---:|---:|---:|---:|---:|
| 1 | 100.00% (n=33) | 100.00% (n=33) | 100.00% (n=33) | 100.00% (n=33) | 100.00% (n=33) |
| 2 | 100.00% (n=351) | 100.00% (n=351) | 100.00% (n=351) | 100.00% (n=351) | 100.00% (n=351) |

## qwen1.5b / Original test: unseen long compositions
|Calls|Joint free execution|Joint + sequence oracle|Single-task + sequence oracle|Joint + operation oracle|Single-task + operation oracle|
|---|---:|---:|---:|---:|---:|
| 3 | 91.93% (n=384) | 99.22% (n=384) | 100.00% (n=384) | 92.71% (n=384) | 81.51% (n=384) |
| 4 | 54.95% (n=384) | 92.71% (n=384) | 89.84% (n=384) | 60.16% (n=384) | 66.41% (n=384) |
| 5 | 27.60% (n=384) | 71.61% (n=384) | 80.99% (n=384) | 44.01% (n=384) | 44.53% (n=384) |

## qwen3b / Original test: unseen long compositions
|Calls|Joint free execution|Joint + sequence oracle|Single-task + sequence oracle|Joint + operation oracle|Single-task + operation oracle|
|---|---:|---:|---:|---:|---:|
| 3 | 91.67% (n=384) | 100.00% (n=384) | 99.74% (n=384) | 91.67% (n=384) | 87.50% (n=384) |
| 4 | 56.77% (n=384) | 92.71% (n=384) | 93.23% (n=384) | 61.46% (n=384) | 85.16% (n=384) |
| 5 | 43.49% (n=384) | 80.21% (n=384) | 77.86% (n=384) | 53.12% (n=384) | 76.56% (n=384) |

## qwen7b / Original test: unseen long compositions
|Calls|Joint free execution|Joint + sequence oracle|Single-task + sequence oracle|Joint + operation oracle|Single-task + operation oracle|
|---|---:|---:|---:|---:|---:|
| 3 | 97.14% (n=384) | 99.22% (n=384) | 93.75% (n=384) | 97.92% (n=384) | 100.00% (n=384) |
| 4 | 77.34% (n=384) | 93.75% (n=384) | 84.11% (n=384) | 83.59% (n=384) | 97.66% (n=384) |
| 5 | 58.33% (n=384) | 89.32% (n=384) | 61.98% (n=384) | 68.75% (n=384) | 70.83% (n=384) |

## qwen32b / Original test: unseen long compositions
|Calls|Joint free execution|Joint + sequence oracle|Single-task + sequence oracle|Joint + operation oracle|Single-task + operation oracle|
|---|---:|---:|---:|---:|---:|
| 3 | 99.74% (n=384) | 99.74% (n=384) | 100.00% (n=384) | 100.00% (n=384) | 99.48% (n=384) |
| 4 | 94.53% (n=384) | 94.53% (n=384) | 99.48% (n=384) | 100.00% (n=384) | 100.00% (n=384) |
| 5 | 73.70% (n=384) | 73.70% (n=384) | 94.01% (n=384) | 100.00% (n=384) | 98.96% (n=384) |

## qwen1.5b / Original test: stress subset
|Calls|Joint free execution|Joint + sequence oracle|Single-task + sequence oracle|Joint + operation oracle|Single-task + operation oracle|
|---|---:|---:|---:|---:|---:|
| 3 | 100.00% (n=48) | 100.00% (n=48) | 100.00% (n=48) | 100.00% (n=48) | 100.00% (n=48) |
| 4 | 45.83% (n=48) | 85.42% (n=48) | 81.25% (n=48) | 58.33% (n=48) | 70.83% (n=48) |
| 5 | 37.50% (n=48) | 79.17% (n=48) | 85.42% (n=48) | 47.92% (n=48) | 66.67% (n=48) |

## qwen3b / Original test: stress subset
|Calls|Joint free execution|Joint + sequence oracle|Single-task + sequence oracle|Joint + operation oracle|Single-task + operation oracle|
|---|---:|---:|---:|---:|---:|
| 3 | 100.00% (n=48) | 100.00% (n=48) | 97.92% (n=48) | 100.00% (n=48) | 100.00% (n=48) |
| 4 | 81.25% (n=48) | 89.58% (n=48) | 91.67% (n=48) | 91.67% (n=48) | 83.33% (n=48) |
| 5 | 43.75% (n=48) | 97.92% (n=48) | 97.92% (n=48) | 43.75% (n=48) | 75.00% (n=48) |

## qwen7b / Original test: stress subset
|Calls|Joint free execution|Joint + sequence oracle|Single-task + sequence oracle|Joint + operation oracle|Single-task + operation oracle|
|---|---:|---:|---:|---:|---:|
| 3 | 100.00% (n=48) | 100.00% (n=48) | 97.92% (n=48) | 100.00% (n=48) | 100.00% (n=48) |
| 4 | 83.33% (n=48) | 100.00% (n=48) | 83.33% (n=48) | 83.33% (n=48) | 100.00% (n=48) |
| 5 | 47.92% (n=48) | 93.75% (n=48) | 81.25% (n=48) | 50.00% (n=48) | 70.83% (n=48) |

## qwen32b / Original test: stress subset
|Calls|Joint free execution|Joint + sequence oracle|Single-task + sequence oracle|Joint + operation oracle|Single-task + operation oracle|
|---|---:|---:|---:|---:|---:|
| 3 | 93.75% (n=48) | 93.75% (n=48) | 100.00% (n=48) | 100.00% (n=48) | 100.00% (n=48) |
| 4 | 100.00% (n=48) | 100.00% (n=48) | 100.00% (n=48) | 100.00% (n=48) | 100.00% (n=48) |
| 5 | 72.92% (n=48) | 72.92% (n=48) | 97.92% (n=48) | 100.00% (n=48) | 100.00% (n=48) |

## qwen1.5b / Independent confirmation
|Calls|Joint free execution|Joint + sequence oracle|Single-task + sequence oracle|Joint + operation oracle|Single-task + operation oracle|
|---|---:|---:|---:|---:|---:|
| 3 | 92.01% (n=288) | 98.26% (n=288) | 99.31% (n=288) | 93.40% (n=288) | 82.64% (n=288) |
| 4 | 61.46% (n=288) | 95.83% (n=288) | 90.62% (n=288) | 64.24% (n=288) | 73.61% (n=288) |
| 5 | 31.94% (n=288) | 84.38% (n=288) | 73.26% (n=288) | 36.46% (n=288) | 40.62% (n=288) |
| 6 | 17.01% (n=288) | 74.31% (n=288) | 75.35% (n=288) | 26.74% (n=288) | 35.42% (n=288) |
| 8 | 9.72% (n=288) | 53.47% (n=288) | 41.67% (n=288) | 28.47% (n=288) | 33.68% (n=288) |

## qwen3b / Independent confirmation
|Calls|Joint free execution|Joint + sequence oracle|Single-task + sequence oracle|Joint + operation oracle|Single-task + operation oracle|
|---|---:|---:|---:|---:|---:|
| 3 | 85.76% (n=288) | 99.65% (n=288) | 95.49% (n=288) | 86.11% (n=288) | 84.72% (n=288) |
| 4 | 61.11% (n=288) | 95.83% (n=288) | 95.83% (n=288) | 64.58% (n=288) | 82.29% (n=288) |
| 5 | 34.03% (n=288) | 78.12% (n=288) | 84.03% (n=288) | 43.06% (n=288) | 70.14% (n=288) |
| 6 | 20.83% (n=288) | 62.85% (n=288) | 76.39% (n=288) | 27.43% (n=288) | 64.93% (n=288) |
| 8 | 2.78% (n=288) | 35.42% (n=288) | 45.83% (n=288) | 9.03% (n=288) | 41.32% (n=288) |

## qwen7b / Independent confirmation
|Calls|Joint free execution|Joint + sequence oracle|Single-task + sequence oracle|Joint + operation oracle|Single-task + operation oracle|
|---|---:|---:|---:|---:|---:|
| 3 | 97.22% (n=288) | 98.96% (n=288) | 98.96% (n=288) | 98.26% (n=288) | 100.00% (n=288) |
| 4 | 84.03% (n=288) | 94.10% (n=288) | 85.07% (n=288) | 89.93% (n=288) | 93.75% (n=288) |
| 5 | 50.35% (n=288) | 84.72% (n=288) | 57.64% (n=288) | 62.50% (n=288) | 67.36% (n=288) |
| 6 | 37.15% (n=288) | 78.12% (n=288) | 52.43% (n=288) | 46.18% (n=288) | 51.39% (n=288) |
| 8 | 13.89% (n=288) | 48.61% (n=288) | 9.38% (n=288) | 33.33% (n=288) | 29.86% (n=288) |

## qwen32b / Independent confirmation
|Calls|Joint free execution|Joint + sequence oracle|Single-task + sequence oracle|Joint + operation oracle|Single-task + operation oracle|
|---|---:|---:|---:|---:|---:|
| 3 | 100.00% (n=288) | 100.00% (n=288) | 100.00% (n=288) | 100.00% (n=288) | 100.00% (n=288) |
| 4 | 96.18% (n=288) | 96.18% (n=288) | 97.92% (n=288) | 100.00% (n=288) | 99.65% (n=288) |
| 5 | 85.76% (n=288) | 85.76% (n=288) | 92.71% (n=288) | 100.00% (n=288) | 96.18% (n=288) |
| 6 | 83.33% (n=288) | 83.33% (n=288) | 93.06% (n=288) | 100.00% (n=288) | 98.26% (n=288) |
| 8 | 61.46% (n=288) | 68.06% (n=288) | 90.62% (n=288) | 92.01% (n=288) | 96.53% (n=288) |

## Scope and reproduction

Oracle-assisted ability is distinct from autonomous ability. Seeds/examples are not selected for positive results; segment EOS/format failures are retained. Supervised-token counts differ across conditions and are recorded separately. B under earlier natural outputs covered only emitted calls; the correct-sequence oracle here covers all required calls.

Raw per-example trajectories are in runs/<run>/evaluation-*.jsonl, including all program/model segments and token IDs. Independent recomputation is in analysis/results-audit.json. Environment, model, and input hashes are in infrastructure/ and analysis/reproducibility-inputs.json; task configurations and frozen source are in analysis/formal-source-freeze.json.
