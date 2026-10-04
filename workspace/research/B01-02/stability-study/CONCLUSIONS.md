# Stability study: final results and interpretation

The fixed main matrix, operation-input comparison, and fresh-program confirmation are complete and have passed trajectory audits. The strongest new finding is that operation performance on these tool-composition tasks can fail with full history and recover with unchanged weights when the input contains only the current tool and actual state. Separate training helps under some conditions, but does not consistently outperform joint training across all models, seeds, and lengths.

## What the comparisons mean

The models are Qwen2.5 Base 3B/32B with existing LoRA adapters trained under three seeds. Joint training uses one adapter for names, operations, and termination. Separate training supervises names/order/termination in one adapter and operations in another, then switches adapters during actual inference. The primary comparison is fixed at 512 steps. Curves cover steps 64/128/256/512; two 256-step specialists versus the 512-step joint model provide a cumulative-training-example-matched comparison.

Inputs already specify tool order, so name generation maintains and repeats that order and terminates correctly; it does not plan from a goal. There are nine tools, with 1–2 calls per training example and 3/4/5/6/8 in long tests. Complete success requires correct names, termination, every prescribed operation, and every intermediate number.

“Current tool + actual state” changes only the operation input; name generation still sees the original task and actual global history. The model chooses the tool name and supplies the state through its actual output. The program provides no correct names, states, or corrections. This intervention removes both past operations and the future tool list and resembles the single-tool training format. Its effect cannot be attributed solely to context length.

## Fresh-program confirmation: main results

The set contains 100 preregistered, frozen new tool sequences with four inputs each: 400 examples per condition and three training seeds. The table reports complete success. Repeated conditions and seeds do not create additional independent examples.

|Model|Joint training + full history|Separate training + full history|Joint training + current tool/state|Separate training + current tool/state|
|---|---:|---:|---:|---:|
|3B|35.67%|51.17%|39.67%|62.25%|
|32B|79.58%|90.75%|93.92%|96.00%|

Changing only operation input improves the 32B joint model by 27.00, 7.00, and 9.00 percentage points across seeds. There are 172 failure-to-success transitions and no success-to-failure transitions. Under the relaxed criterion of correct names/order, termination, and final numbers, accuracy still rises from 80.33% to 93.92%; the improvement goes beyond format differences that leave final states unchanged.

With the same local operation input, separate training changes 32B accuracy relative to joint training by −3.50, +2.25, and +7.50 percentage points. The additional benefit is not consistent. The corresponding 3B changes are +43.25, 0.00, and +24.50 points: a large mean gain with substantial seed variation. Changing only operation input in the 3B joint model yields +3.50, +3.75, and +4.75 points.

On fresh eight-tool examples, the four routes score 4.17%, 10.00%, 5.83%, and 25.83% for 3B, and 47.50%, 72.50%, 74.58%, and 84.58% for 32B. With local input, the additional 32B benefit from separate training is −7.50, +6.25, and +31.25 points across seeds, again including a counterexample.

## The two subtask columns

These scores come from the same actual execution, not the intersection of two oracle tests. “All emitted operations correct” covers every call actually generated. Missing calls fail the sequence criterion; no operation scores are invented for them.

|Model|Training|Operation input|Complete sequence and termination correct|All emitted operations correct|Whole-task success|
|---|---|---|---:|---:|---:|
|3B|Joint training|Full history|40.25%|85.50%|35.67%|
|3B|Joint training|Current tool/state|39.67%|100.00%|39.67%|
|3B|Separate training|Full history|62.75%|82.58%|51.17%|
|3B|Separate training|Current tool/state|62.25%|100.00%|62.25%|
|32B|Joint training|Full history|92.17%|83.92%|79.58%|
|32B|Joint training|Current tool/state|93.92%|100.00%|93.92%|
|32B|Separate training|Full history|95.58%|94.67%|90.75%|
|32B|Separate training|Current tool/state|96.00%|100.00%|96.00%|

All emitted operations are correct under local input in this evaluation; remaining errors concern names, order, call count, or termination. This 100% applies only to observed calls, not every possible state. The 144-cell table covering every length, four routes, and both datasets is in [CONTEXT_SUBTASKS.md](CONTEXT_SUBTASKS.md).

## Relation to the existing program set and original hypothesis

Across three seeds on the existing 480 examples, 3B scores are 40.49% for joint and 55.83% for separate training, rising to 46.32% and 68.26% with local input. The corresponding 32B scores are 85.35% and 93.19%, then 98.40% and 98.19%. The direction of local-input improvement agrees across datasets; the extra benefit of separate training for 32B does not.

Single-component replacements on the existing set give 3B a 13.40-point gain from replacing name generation and a −0.21-point change from replacing operations. For 32B, the changes are −0.14 and +7.99 points. The main bottleneck differs by scale. Checkpoint curves also do not support a common early-stopping explanation; see all checkpoints in [REPORT.md](REPORT.md) and [COMPOSITION_EFFECTS.md](COMPOSITION_EFFECTS.md).

The subtask-product prediction proposed by the user is practically useful. At step 512 on the existing set, computing products within length and seed and then averaging predicts 56.04% versus 55.83% actual accuracy for separate 3B, and 93.20% versus 93.19% for separate 32B. Joint training is also close: 41.17% versus 40.49% for 3B and 85.43% versus 85.35% for 32B. This agreement supports decomposed performance estimation, but alone cannot establish independent internal modules or explain easier learning. See [THEORY.md](THEORY.md) and [ALL_ROUTE_PREDICTIONS.md](ALL_ROUTE_PREDICTIONS.md) for assumptions and all routes.

## Auditable cases and scope limits

Fixed random samples of improved fresh 32B cases include seed 11 context-confirm-L8-p05-x2, which omits an inc in the sixth brown tool; seed 11 context-confirm-L5-p17-x2, which omits the final inc in the second white tool; and seed 22 context-confirm-L8-p16-x3, which omits the final inc in the sixth gray tool. Local input restores each operation, with the first divergence in the operation stage. See analysis/context-cases.json for raw numbers, actual inputs, and comparisons. A few 3B cases first diverge at name generation; these are retained, so not every difference can be assigned directly to operation input.

Every fresh tool sequence is absent from earlier data, but the 100 sequences represent only 85 final numeric transformations, and 18 sequences have final functions equivalent to training functions. They are not 100 new functions. The existing set applies stricter function exclusions, so the sets are reported separately. Post hoc semantic strata retain all 400 primary examples. On the 82 sequences with training-unseen functions, the 32B joint model still improves from 77.85% to 93.70%. This stratification is not another independent confirmation; see fresh-confirmation/DATASET_SCOPE.md and SEMANTIC_STRATA.md.

Separate training also changes loss normalization and parameter count. Names account for approximately 11.14% of jointly supervised tokens and operations for 88.86%; two adapters store twice the parameters of one. Matching cumulative examples does not exclude these explanations. Three seeds cannot guarantee stable generalization, and the study does not establish benefits for real-world agents, innovation, or RSI.

## Recommendation

Describe the finding as follows: operation execution in long tool compositions is sensitive to input context; organizing input around the current tool and actual state can substantially improve execution without changing model weights. Present separate training as a conditional improvement, retaining the 3B sequence bottleneck and 32B counterexamples.

To investigate training causes, hold inference inputs fixed and compare ordinary joint loss, balanced name/operation loss, and capacity-matched separate training. This would better distinguish division of work from supervision weighting and capacity. Transfer to real agents requires testing when current state is sufficient to determine operations; cross-tool dependencies cannot simply be removed. All experiments registered for this round are complete. Specific extensions for the next round are to be submitted for user review.

## Delivery and resources

Formal coverage totals 136320 trajectories: 129120 new and 7200 reused, with calibration counted separately. All stages passed score, token-provenance, and actual-generation-context audits; all compute jobs have ended. New evaluations used 31.62 allocated GPU-hours with no new training. The final local check showed 0 MiB and 0% utilization on all eight GPUs. Returned remote machines were not accessed again.

Audit entry point: [COMPLETION_AUDIT.md](COMPLETION_AUDIT.md). Fresh confirmation by length and seed: [fresh-confirmation/REPORT.md](fresh-confirmation/REPORT.md). Figure: [figures/context-and-fresh-confirmation.png](figures/context-and-fresh-confirmation.png).
