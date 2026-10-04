# Second-stage oracle ablation: conclusions after completion

2026-09-25. **All 36 training jobs, 60 checkpoint/inference-mode combinations, and 62,400 main evaluations are complete. Independent record-level recomputation and token-context checks passed. New-process reruns of 120 examples per scale, 480 total, matched complete records exactly.** This deliverable includes positive results, counterexamples, seed variation, and unresolved interpretations; work did not stop at obtaining servers or launching jobs. See [COMPLETION_AUDIT.md](COMPLETION_AUDIT.md).

## Answer to the main hypothesis

The two subtasks can indeed be learned separately. On in-distribution short calls, both specialist conditions score384/384 at all four scales (128 examples x3 seeds). On long calls, the two 32B specialists also retain high accuracy:96.53% on eight-tool sequence prediction and 90.62% on all-operation expansion. This supports measuring and training the two abilities separately as a useful research approach.

**Separate training is not established as always easier than joint training, nor are name benefits explained by two independent internal modules.** Under matched oracle inference, training gains depend on subtask, model scale, and seed. There is clear 7B degradation, and 32B expansion gains are not positive in all three seeds. No STEP training condition under the new protocol is included, so this study alone cannot explain all earlier NAME-versus-STEP gains.

Tool order is supplied in the input. Sequence ability here means repeating names in input-list order and stopping correctly, rather than autonomously planning from a goal. The 9 tools are fixed, with no on-the-fly invention. See [METHOD_AND_REPRODUCTION.md](METHOD_AND_REPRODUCTION.md) for training/program-handoff examples.

## Key training comparisons under matched inference

The table uses eight-tool tasks in the independent confirmation set, with 96 examples x3 seeds =288 outputs per cell. Both expansion columns receive correct program-supplied sequences; both sequence columns have programs correctly execute the tools actually selected. Within each pair, the changed factor is the training target, without added inference assistance.

|Model|Expansion: joint training|Expansion: specialist training|Sequence: joint training|Sequence: specialist training|Joint autonomous execution|
|---|---:|---:|---:|---:|---:|
|1.5B|53.47%|41.67%|28.47%|33.68%|9.72%|
|3B|35.42%|45.83%|9.03%|41.32%|2.78%|
|7B|48.61%|9.38%|33.33%|29.86%|13.89%|
|32B|68.06%|90.62%|92.01%|96.53%|61.46%|

Two specific positive findings deserve attention:

- **32B expansion-specialist training improves by 22.57 percentage points on average**, with seed differences+65.63,−9.38,+11.46. A24-program clustered-bootstrap 95% interval is[+15.28,+30.56] points, conditional on the three trained seeds; it must not hide seed22 degradation or the large seed11 contribution. Per-seed correct counts are 27/84/85 for joint and 90/75/96 for specialist, each out of 96.
- **3B sequence-specialist training improves by 32.29 percentage points on average**, with consistent seed differences+28.13,+15.63,+53.13. The program-bootstrap interval is[+20.49,+44.44] points. Correct counts are 24/1/1 for joint and 51/16/52 for specialist, each out of 96.

7B expansion training is an essential counterexample: all three differences are negative, averaging−39.24 points.32B sequence training averages+4.51 points with program-bootstrap interval[−4.51,+15.97], insufficient for a consistent-improvement claim. See [REPORT.md](REPORT.md) for all short-call, unseen-composition, stress, and 3/4/5/6/8-tool results; per-seed paired differences are in analysis/paired-comparisons.json. These intervals are descriptive, uncorrected for multiple comparisons, and not population-level confidence claims over training randomness.

## Can the subtask product predict overall performance?

The 32B specialist results follow. A means the entire sequence is correct; B means every required call is expanded correctly. Compute products within each seed before averaging.

|Calls|A sequence|B all expansions|A×B|Both oracle tasks correct on the same example|Joint autonomous execution|
|---|---:|---:|---:|---:|---:|
|3|100.00%|100.00%|100.00%|100.00%|100.00%|
|4|99.65%|97.92%|97.59%|97.57%|96.18%|
|5|96.18%|92.71%|89.19%|88.89%|85.76%|
|6|98.26%|93.06%|91.51%|91.32%|83.33%|
|8|96.53%|90.62%|87.70%|87.50%|61.46%|

For these two **separately trained, separately oracle-assisted** subtasks, paired both-correct rates are close to their products. The eight-tool difference is−0.20 points, with program-bootstrap interval[−1.06,+0.47]. This is compatible with weak association between subtask outputs, but does not prove independence, especially since high accuracies tend to make the difference small.

The 87.70% product nevertheless does not predict the joint autonomous model at 61.46%. The issue is not a sudden strong correlation between the specialists: the comparison changes checkpoints, supervision, and inference history. End-to-end accuracy of actual alternating specialist models was not tested;87.50% is not measured composed-agent performance. See [ORACLE_PRODUCTS.md](ORACLE_PRODUCTS.md) for all scales and [FACTORIZATION.md](FACTORIZATION.md) for differences and uncertainty.

## What do failure trajectories show?

Analysis goes beyond means or a few selected examples. All 62,400 outputs are categorized. Under the correct-sequence oracle on independent eight-tool tasks, all same-example expansion outputs are paired and the first error located.

32B joint training fails92/288 cases: first errors are premature within-tool `EndTool` in 77, wrong operation sequences in 4, numerical errors in 3, and unparseable bodies in 8. Expansion-specialist training fails 27:6 premature internal endings and 21 wrong operation sequences. In pairs,81 change from wrong to correct and 16 from correct to wrong, a net gain of 65. **The established behavioral change is fewer omitted operations within tools; this is not a settled internal learning mechanism or direct proof of the original STEP whole-task stopping-after-two-calls mechanism.**

7B shows the reverse: expansion-specialist training fails 261 cases, with 201 first errors from premature within-tool ending, versus 121 under joint training. Final 32-step teacher-forced losses are approximately 10⁻⁶ for both, and in-distribution short calls are all correct. This is not well described as nonconvergence or failure to learn format; long-history generalization is sensitive to supervision targets and seeds. See [BADCASES.md](BADCASES.md) for 3 fixed-random, individually checked 32B gains and 3 7B degradations. Full counts, operation details, and positions are in analysis/mechanism-diagnostics.json.

Overall failure categories:4843 early Done with correct name prefix,4096 wrong/incomplete operations,3580 wrong names,91 format/segment-budget failures,144 EOS/format failures,37 purely numerical errors, and 2 multi-tool cases. Categories have fixed priority rather than independent causes. All failures remain in denominators. Correct-reference bodies are at most 33 tokens, below 128; full output is at most 282, below 2048. Reference line counts do not force truncation.

## Reliability and remaining explanations

Input/output provenance, program-token loss masks, uncorrected wrong tools, propagation of wrong numbers, and batched asynchronous segment endings are checked. All 36 runs complete 512 steps with finite losses and gradients. Main inference/protocol code hashes match across runs. Original tests contain no exact training duplicates; independent confirmation inputs contain no exact original training/test duplicates. That confirmation set was fixed earlier, not created blind after this study produced results.

Two oracle interventions on the same joint checkpoint form 24,960 pairs with autonomous inference. In 19 cases, model segments differ before program content diverges:2 at 1.5B,10 at 3B,7 at 7B,0 at 32B, despite matching prefix hashes. BF16 numerical differences under dynamic batching are a possible explanation, not yet localized per example through logits. These 19 cases are not clean token-intervention evidence. They include 4 correctness gains and 3 losses; excluding anomalies leaves 3223 gains and 0 losses, while primary tables retain original denominators. Exact480/480 new-process reproduction with original batches establishes reproducibility for that execution setup, not bitwise invariance across batches.

Specialization removes the other loss component and changes supervised-token counts and gradient weights; expansion specialization also masks names, Done, and EOS. Results cannot distinguish multitask gradient interference, ending supervision, or supervision weighting. They do not establish that names necessarily create internal modules, larger models necessarily resolve the issue, real-agent early stopping is solved, or RSI improves.

## Recommended claim and next steps

The most defensible statement is: **In named-tool execution trained on short calls and tested on long calls, sequence repetition and tool expansion can be learned separately. Changing supervision targets substantially changes long-task generalization, with gains depending on subtask, scale, and seed.32B expansion-specialist training reduces premature within-tool endings, and the paired success of its two oracle subtasks is close to the product of their marginal success rates.**

Retain this research direction, focusing on which supervision components cause which long-history errors. Next separate name loss from Done/EOS termination loss, control the relative weights of both subtasks, and add seeds. These controls can distinguish the proposed two-stage learning explanation from ending-signal/weighting explanations. Actual two-model composition and real-agent transfer should follow. The preregistered second stage is complete; these mechanism studies are recommendations, not completed results or substitutes for current acceptance checks.

Total single-GPU process time including loading, calibration, and reruns is approximately 22.76 hours across different GPU types, not a uniform-hardware compute cost. Main training is approximately 14.18 hours, main evaluation 8.40, calibration 0.04, and reruns 0.14. See analysis/cost-total.json for definitions. All six 5090 servers were returned; local training/evaluation processes ended. Environments, adapters, code, raw outputs, and reports remain in this directory.
