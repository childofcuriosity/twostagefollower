> This is the main-matrix stage report. Both subsequent stages are now complete; see [CONCLUSIONS.md](CONCLUSIONS.md) for final interpretation and current status. References below to ongoing work describe progress at the time.

# Main matrix: completed actual-composition results

This document explains only the completed, audited main matrix. At this stage, operation-context interventions and fresh-program confirmation remain in progress. CONCLUSIONS.md will be the final entry point; the goal is not yet marked complete.

Models are Qwen2.5 Base 3B and 32B. Inputs provide four numbers and the correct tool order. The model maintains that order, expands nine learned tools, and terminates correctly; it does not autonomously plan a new order or invent tools.

Joint training supervises names and operations in one LoRA adapter. Sequence-only and operation-only training compute loss only on the corresponding output tokens, while training inputs still contain the full correct text. Actual composition switches fine-tuned adapters on the same frozen base according to generation stage. The program does not supply reference answers.

## Fixed step 512: actual complete execution

Each model/route uses three training seeds and 480 long examples per seed (96 each at 3/4/5/6/8 tools), totaling 1440 trajectories. Whole-task success requires correct order, operations, and termination. Operations must follow tool definitions and produce correct numbers at every step. Coincidentally correct final numbers or a different equivalent operation sequence do not satisfy the strict primary metric.

|Name generator|Operation generator|3B all long tasks|3B eight tools|32B all long tasks|32B eight tools|
|---|---|---:|---:|---:|---:|
|Joint model|Joint model|40.49%|3.12%|85.35%|61.46%|
|Sequence specialist|Joint model|53.89%|15.28%|85.21%|65.97%|
|Joint model|Operation specialist|40.28%|2.08%|93.33%|82.64%|
|Sequence specialist|Operation specialist|55.83%|19.79%|93.19%|87.15%|

The source of gains differs by scale: 3B mainly benefits from replacing name/order generation, while 32B mainly benefits from replacing operations. This does not support a general claim that separately training both components is always easier.

With specialists in both stages, 3B gains 12.29, 8.75, and 25.00 percentage points over joint training across seeds; 32B changes by +17.08, −1.25, and +7.71 points. The negative 32B observation does not establish significant population-level harm, but it fails the registered requirement of improvement for all three seeds.

## Matching training-example exposure

Two 256-step specialists and one 512-step joint model receive the same cumulative number of training examples. The 3B gains are 11.88, 7.08, and 24.17 points, averaging 14.37. The 32B changes are +15.83, −1.88, and +7.29 points, averaging 7.08.

This excludes a simple explanation based only on twice the total example exposure, but does not match every resource. Two adapters still double parameter storage; supervised-token counts and component loss normalization also differ. Approximately 11.14% of joint target tokens are names and task-end markers, while 88.86% are operations and per-tool EndTool markers. Gains cannot directly be attributed to independent internal modules.

For 32B, two 256-step specialists outperform the 256-step joint model for all three seeds. The fixed 512-step and exposure-matched comparisons against the 512-step joint model do not improve consistently. Retain every checkpoint rather than choosing the strongest one as the primary result.

## Subtask scores predict actual performance, but do not establish independent learning

Multiplying within seed and tool length before aggregation predicts 56.04% for the two 3B specialists versus 55.83% actual success, and 93.20% for 32B versus 93.19% actual success. Program-clustered bootstrap intervals conditional on the three training seeds place prediction errors at approximately [−1.15,+0.73] and [−0.41,+0.41] percentage points.

The joint model is a necessary control: the same calculation predicts 41.17% versus 40.49% actual success for 3B, and 85.43% versus 85.35% for 32B. Product agreement supports this decomposition as a performance diagnostic, rather than providing evidence unique to separate training. Internal independence and easier learning require additional interventions.

Pooling lengths before multiplication introduces association because length affects both components. Both calculations are reported in ORACLE_PREDICTION_CHECK.md and ALL_ROUTE_PREDICTIONS.md. Actual execution is not replaced by the fraction of examples correct in both oracle tests.

## Findings on instability

At steps 64/128/256/512, 32B joint-model long-task success counts out of 480 are 382/351/349/354 for seed 11, 346/425/415/437 for seed 22, and 429/431/434/438 for seed 33. One common early-stopping rule cannot simultaneously explain and improve all three. Near-perfect short-task performance does not guarantee stable long-task performance.

On 288 eight-tool 32B examples with correct names supplied, joint-model operations are all correct for the first two calls, with errors beginning at the third. The operation specialist is correct for the first three, with errors beginning at the fourth. New errors also occur after entirely correct histories, so imitation of earlier errors cannot explain every failure. This motivates the operation-context intervention; it does not establish a causal effect of any particular factor in long histories.

## Audits and limitations

All 109824 formal main-matrix trajectories passed independent recomputation of operations, scores, token decoding, and prefix hashes: 102624 new records and 7200 reused old 32B step-512 outputs. Direct single-adapter calls and routing to the same adapter match on all 40 calibration examples at each scale on current hardware.

Of 7200 old 3B outputs from the 5090 and new local PRO6000 outputs, 6930 match exactly; the largest group-level whole-task score difference is 5/480. Final adapters and step-512 checkpoints have identical verified weights and configurations. The primary analysis uses only the locally rerun 3B baselines.

Among first divergences under single-component replacement, 80 occur in the unchanged component despite identical text prefixes for that line. Dynamic-batch numerical differences are a possible, separately unverified explanation. Retain every case. At step 512, these exceptions contribute zero net successes to the 193-example net gain from replacing the 3B sequence component. None occur within the 115-example net gain from replacing 32B operations, so they cannot explain the main gains.

The task remains controlled, with supplied tool order, three training seeds, and a limited tool library. Because the existing confirmation set has already been analyzed, a new program set is separately preregistered and frozen. Transfer to real agents, innovation, and RSI remain unestablished; reorganizing context is not a new training method.
