# Review: conditional separation of execution training and proposal utility

2026-09-24. Actual training, three-round loops, same-start interventions, supplementary controls, and integrity audits are complete. The finding is worth retaining with a narrower claim. Evidence does not establish a universal RSI bottleneck or a paper with a complete mechanism account.

## Findings established by the experiments

Under the original macro-execution supervision recipe, execution improves while finite-budget abstraction-proposal utility declines, replicated across three models from two families. Utility is net compression of held-out programs by proposed macros, including definition costs. It does not directly measure scientific innovation.

| Model | Unseen-composition execution after macro training | Net proposal compression: base → macro-trained |
|---|---:|---:|
| Qwen2.5-1.5B | 29.77% | 39.01% → 9.06% |
| Qwen2.5-3B | 60.76% | 40.42% → 9.15% |
| SmolLM2-1.7B | 22.66% | 35.39% → 9.01% |

The table uses the primary setting and three-seed means. For every model, macro-trained mean proposal utility is below base in all 12 prompt/temperature/budget settings. Shared models, examples, and sampling prefixes mean these are not 36 independent replications. Prompt changes, larger budgets, and fixed candidate lengths do not remove the gap. Missing ends coverage in original macros is a real confound. Restoring it yields 12.93% primary proposal utility, still far below base at 39.01%, but broader distribution shift remains possible.

Final weights from three original-recipe reruns match original SHA256 hashes. Checkpoint measurements show compression falling from 40.26% to 20.78% at step 16 and 9.48% at step 64, when IID execution reaches 98.96%; proposal utility is 10.37% at step 512. The decline occurs early, not only at the final checkpoint. Timeline and primary-table sampling paths differ and are not one measurement.

## Scope limits revealed by the extension

The new proposal → support selection → curriculum generation → execution-training loop does not naturally reproduce proposal degradation. Three rounds with a shared model give:

| Execution domain | Initial → final net proposal compression | Final unseen-family execution |
|---|---:|---:|
| Numeric | 38.69% → 40.58% | 99.22% |
| String | 37.99% → 39.05% | 95.57% |

This counters the claim that any execution training harms proposing. Recipes differ in input representation, curriculum, learning rate, training amount, and optimizer resets, so no single protective factor is identified; see [RECIPE_COMPARISON.md](RECIPE_COMPARISON.md). Shared final execution on the longer string stress set is only 28.65%; high standard-set scores do not establish comprehensive mastery.

Joint proposal supervision yields slightly higher final mean proposal utility than shared but lower mean execution, not an across-the-board improvement. Most paired intervals are wide. The string unseen-family execution difference is −4.69 points, three-seed 95% t interval [−8.05, −1.33]. This is one of multiple unadjusted comparisons and cannot alone establish a stable mechanism. Replay and shuffled replay match auxiliary tokens round by round; shuffled replay notably worsens numeric proposal performance, motivating study of supervision relationships without establishing a general repair.

## Which RSI-related causal links remain unestablished?

We separately measure execution E, proxy proposal utility P, and actual learning gain G after proposal-source changes to the curriculum. The original recipe supports rising E with falling P; evidence from falling P to falling G remains insufficient.

From identical learner checkpoints, switching between the initial base and updated proposer yields primary execution intervals crossing zero in both domains. Base-source minus updated-source is −0.78 points [−6.60, 5.04] numerically and +4.69 [−6.96, 16.33] for strings. This establishes neither harm nor harmlessness. Because the new loop does not degrade its proposer, these comparisons weakly test consequences of degradation.

An explicitly post hoc stress intervention therefore substitutes the degraded original-recipe proposer while training learners from the same starts. Updated-source minus degraded-source is +7.03 points numerically, positive in all three seeds but with interval [−2.67, 16.73]; for strings it is −2.86 [−31.28, 25.55], with inconsistent direction. This does not establish a reliable cross-domain RSI bottleneck. Proposal sources also change program lengths and token counts, so comparisons estimate total curriculum effects at fixed examples/steps.

Original-recipe gradient probes show negative cosines at several post-update checkpoints, but the loop recipe also has negative cosines without sustained degradation. At step 16, proposal surrogate NLL improves while sampled utility declines. Neither surrogate loss nor gradient sign directly establishes an innovation mechanism. Local first-order analysis is an explanatory framework, not a new theorem or completed causal explanation.

## Recommendation

Retain the core claim: **On controlled program-abstraction tasks, execution gains alone do not establish proposal-utility or subsequent improvement gains; proposal degradation under execution supervision depends on training conditions.** Evidence comprises three-model replication, early timelines, candidate controls, a loop that preserves proposing, and same-start branches.

Avoid blindly adding similar toy training or selecting seeds by results. Next, isolate identifiable factors and test actual learning gains: fix data/update budgets and cross explicit primitive plans versus macro-name inputs with narrow versus broad curricula. Then use an independent executable-code task, identical learner starts, and comparable budgets to test proposal-source effects on held-out learning gains. Prespecify endpoints, meaningful effect sizes, and power rather than stopping for positive results. If P differs consistently but G does not follow, abandon an RSI causal-bottleneck claim and limit the contribution to proposal metrics and training-transfer boundaries.

These are next-stage recommendations after review. No natural-code experiments were run here, nor are conclusions established for larger models, full-parameter training, or RL. Nearby work already studies proposer/solver interference, entropy decline, and proposer-training ablations; those broad concepts are not original. See [literature review](literature/NEAREST.md).

## Delivery and audit

- [Full report](REPORT.md): design, conditions, budgets, primary controls, and limits.
- [Supplement](SUPPLEMENT.md): coverage, length, timeline, original-recipe gradients, and degraded-source stress tests.
- [Audit](analysis/verification.json): 50,464 execution records, 180,864 proposals, 150 checkpoint hashes, semantic separation, and training counts. Repeated measurements are not independent samples; checkpoints are not independent training runs.
- [Intervals](analysis/loop-inference.json), [raw results/reproduction](README.md), [exportable figures](figures/), and [resource accounting](analysis/cost.json). New allocation is approximately 4.67 GPU-hours, excluding downloads/queues and distinct from kernel activity.

Computation is complete. All new environments, models, caches, logs, and research artifacts remain in the project, including counterexamples, failures, and post hoc amendments. Research results were not published or uploaded at this stage.
