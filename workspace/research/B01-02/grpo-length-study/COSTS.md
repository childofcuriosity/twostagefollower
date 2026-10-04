# Compute, output tokens, and stopping reasons

All token counts are checked record by record against saved output_ids, including actual EOS and excluding prompt and padding. EOS must be the final output token; cap-truncated outputs must exactly match the frozen cap. Token totals in training-loss records also match the raw candidates.

| Setting | STEP training tokens | NAME training tokens | NAME relative change | STEP training-segment GPUh | NAME training-segment GPUh | NAME relative change |
|---|---:|---:|---:|---:|---:|---:|
| 7b-L3 | 3,624,615 | 3,522,155 | -2.83% | 4.742 | 4.632 | -2.32% |
| 7b-L4 | 4,547,028 | 4,441,896 | -2.31% | 5.505 | 5.304 | -3.66% |
| 7b-L5 | 5,275,805 | 5,323,943 | +0.91% | 6.069 | 5.887 | -2.99% |
| 14b-L5 | 5,872,937 | 5,711,950 | -2.74% | 11.382 | 10.899 | -4.24% |
| 14b-L6 | 6,818,650 | 6,691,325 | -1.87% | 13.065 | 12.361 | -5.38% |
| 14b-L7 | 7,647,766 | 7,694,354 | +0.61% | 14.586 | 13.977 | -4.18% |

Each cell totals three seeds and 38400 candidates. Training-segment GPUh is run wall time after NCCL initialization multiplied by 2, including loading, sampling, backpropagation, saving, and waiting, but excluding earlier process/NCCL startup. Paired conditions run sequentially in the same physical two-GPU slot. Time differences are measurements from this study, not pure GPU-kernel speedups. Output length is a result of generation behavior; success differences cannot be attributed entirely to the token lengths of the labels themselves.

## Total job occupancy and nested timings

| Scope | GPU-hours |
|---|---:|
| Prechecks and recovery | 5.868 |
| Complete main paired training jobs | 108.770 |
| Complete evaluation-worker lifecycles | 21.360 |
| Total | 135.998 |

Total evaluation-task time: 15.737 GPUh, including model generate time of 15.542 GPUh. Both timings are nested within worker lifecycles and must not be added to the total above. Full-job accounting includes startup, loading, and waiting; sparse utilization samples are not used to estimate active GPU-kernel time. CPU-only data preparation, scoring, and plotting contribute no GPU time.

Resources changed from 6 two-GPU training slots + 4 evaluation GPUs to 7 two-GPU slots + 2 evaluation GPUs in the first hour. Once all training jobs had been dispatched and two GPUs became free, 2 evaluation GPUs were added to finish the queue. These changes affected scheduling only; frozen models, data, sampling, scoring, and training budgets remained unchanged. Training was not interrupted or restarted.

## Actual samples and truncations

Main candidates: 460,800; output tokens: 67,172,424; cap truncations: 9. Independently generated scheduled evaluations: 119,808; output tokens: 17,552,357; cap truncations: 2. All other outputs end with EOS, which alone does not imply task success.

An additional 9216 candidates were generated during prechecks/recovery: 4 original updates + 2 replayed recovery updates for each of 12 condition/tasks. Recovery replays are not independent seeds or main evidence; their costs are included in prechecks. Original-model step0 is generated once per setting/condition and referenced by three seeds; reference counts are not treated as independent generations.

Complete per-setting training/evaluation tokens and stopping reasons: analysis/cost-and-token-audit.json; per-job allocations: analysis/lifecycle-audit.json.

## Inference costs for step100 greedy tests

Each condition totals 512 examples per seed across three seeds, or 1536 fresh test responses. The table uses only the scheduled step100 endpoint, includes EOS, and does not treat multiple seeds as independent samples from one policy. Generation time is actual batch generate wall time, apportioned across outputs and summed, multiplied by the single-GPU count of 1; loading and worker waiting are excluded.

| Setting | STEP mean output tokens | NAME mean output tokens | NAME change | STEP generation GPUh | NAME generation GPUh | NAME change |
|---|---:|---:|---:|---:|---:|---:|
| 7b-L3 | 94.63 | 93.63 | -1.06% | 0.0773 | 0.0759 | -1.73% |
| 7b-L4 | 117.98 | 116.92 | -0.90% | 0.1001 | 0.0976 | -2.48% |
| 7b-L5 | 137.92 | 140.08 | +1.56% | 0.1164 | 0.1133 | -2.62% |
| 14b-L5 | 151.87 | 149.52 | -1.55% | 0.2609 | 0.2478 | -5.04% |
| 14b-L6 | 176.52 | 175.70 | -0.47% | 0.3028 | 0.3058 | +0.98% |
| 14b-L7 | 198.81 | 201.54 | +1.37% | 0.3483 | 0.3718 | +6.74% |

Timing depends on the longest output in each batch and on scheduling. Fewer output tokens do not guarantee a proportional decrease in generate time. These measured time differences are not a cross-hardware or independent throughput benchmark. Full training and evaluation use the same frozen generation caps, with no relaxed budget for NAME.
