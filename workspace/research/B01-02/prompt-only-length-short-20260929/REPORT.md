# 7B/14B prompt-only short evaluation at lengths 2–9

Original weights without adapters. STEP/NAME prompts, tool definitions, data rules, chat templates, greedy decoding, and strict scoring are unchanged. Each point uses 32 shared examples. L2/L5 reuse earlier exploration; the other six lengths add 768 new outputs. Neither the old 512-example formal evaluation nor GRPO outputs are included.

![Accuracy by length](accuracy-vs-length-2-9.png)

| L | 7B STEP | 7B NAME | 14B STEP | 14B NAME | Source |
|---:|---:|---:|---:|---:|---|
| 2 | 3/32 (9.4%) | 7/32 (21.9%) | 21/32 (65.6%) | 20/32 (62.5%) | Reused |
| 3 | 2/32 (6.2%) | 1/32 (3.1%) | 4/32 (12.5%) | 10/32 (31.2%) | New |
| 4 | 0/32 (0.0%) | 1/32 (3.1%) | 5/32 (15.6%) | 6/32 (18.8%) | New |
| 5 | 0/32 (0.0%) | 0/32 (0.0%) | 3/32 (9.4%) | 5/32 (15.6%) | Reused |
| 6 | 0/32 (0.0%) | 0/32 (0.0%) | 0/32 (0.0%) | 1/32 (3.1%) | New |
| 7 | 0/32 (0.0%) | 0/32 (0.0%) | 0/32 (0.0%) | 1/32 (3.1%) | New |
| 8 | 0/32 (0.0%) | 0/32 (0.0%) | 0/32 (0.0%) | 1/32 (3.1%) | New |
| 9 | 0/32 (0.0%) | 0/32 (0.0%) | 0/32 (0.0%) | 0/32 (0.0%) | New |

Termination reasons for new outputs: {'eos': 768}. All 16 jobs exited normally. Raw outputs and token IDs, example-level strict scores, capacity prechecks, configurations, logs, and failure records are retained in the model subdirectories. Header compliance is scored separately. Old auxiliary first-error labels are not treated as reliable omitted/extra-call classifications.

Generation limits follow the existing formula based on correct target length: 256 for L3/L4 and 512 for L6–9, identical across models and conditions at each length. This is an exploratory short evaluation with 32 examples per point. A score of 0/32 does not establish zero population accuracy, and local differences are not independent formal confirmation. These are not post-GRPO length curves.

## Quick reading

The largest 14B gap is at L3: STEP 4/32 = 12.5%, NAME 10/32 = 31.25%, a paired difference of +18.75 points, with seven NAME-only and one STEP-only success. L4 has five versus six successes, and L5 three versus five; NAME succeeds on only one example at each of L6–8. The 7B model is near the floor from L3 onward. L3 merits independent confirmation with a larger sample, but several lengths were inspected and each has only 32 examples. These results establish neither stable method gains nor new formal confirmation, and do not predict persistence after GRPO training.

Parallel model-job wall time is 89.62 seconds; recorded process allocation is 0.275 GPU-hours including loading/saving, not kernel-active time. Every output ends with EOS, with no generation-limit truncation. At completion, all 16 GPUs across the local and two remote machines show 0 MiB, as recorded in resources-final.json. No new training was launched.
