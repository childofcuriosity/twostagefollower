# B01-02 status overview

Updated 2026-09-27. Unpublished internal research summary, separating results, interpretation, and recommendations. No training awaits restart. Detailed data/raw trajectories remain in experiment directories.

Resource update, 2026-09-27: the user supplied three PRO6000 endpoints, checked read-only. One `REDACTED_HOST` matches the current local hostname/internal address and exposes eight local GPUs; the other two `REDACTED_HOST` endpoints each expose four. All are RTX PRO6000 Blackwell with the shared project directory. At inspection, memory was 0 MiB and utilization 0% throughout. This is a point-in-time snapshot requiring recheck before scheduling. Resource inspection launched no study jobs; the 20-seed replication ran only locally as recorded. Credentials are not written into research documents.

## Main point

In the controlled nine-tool task with supplied order, **stable current-tool identity labels are associated with better long execution than step or position labels**. Twenty-seed 1.5B/3B/7B replication strengthens this observation, but does not isolate name-operation binding as the sole cause or establish real-agent gains.

## Task and latest experiment

Inputs contain four digits and a supplied tool sequence. Models emit prescribed primitives, each numeric state, and final `Answer`. Training has 1–2 tools; tests have 3/4/5/6/8. Complete success requires every operation, intermediate number, and answer. This tests execution-length extrapolation, not autonomous planning.

Four header types: uniform `step` (boundaries), `step1/step2` (positions), fixed `toolA`–`toolI` (stable identity with input/output renaming), and original color names (stable identity/original forms). Both identity groups share names across input/output. Position and identity encode different information; columns are not a strictly monotonic information control.

Complete-trajectory success on the existing independent 480 tests, mean ± sample SD across 20 training seeds:

| Model | Uniform step | Position index | Fixed alias | Original tool name |
|---|---:|---:|---:|---:|
|1.5B|0.00±0.00%|0.00±0.00%|15.21±8.92%|18.84±5.79%|
|3B|0.00±0.00%|0.87±0.78%|49.45±11.68%|35.06±5.55%|
|7B|13.49±6.00%|15.16±9.31%|43.73±15.19%|41.25±13.14%|

Paired by seed, aliases beat positions in 20/20 seeds at all three scales, averaging +15.21, +48.57, +28.57 points. Original names beat step in 20/20 at all scales. Aliases beat original names at 3B by +14.39 points, with 18/20 positive seeds. The 1.5B/7B comparison remains unresolved; 7B splits 10 wins/10 losses. 32B has only three original seeds: aliases lose to original names on existing independent tests, but reverse with definitions on original tests. **Do not combine 32B with the 20-seed table as equally robust evidence.**

## Related results under different protocols

Earlier stability experiments use `EndTool/Done` handoffs and cannot be added to `Answer` scores or plotted as one progress curve. On 400 fresh examples, 32B joint/full-history accuracy is 79.58%, rising to 93.92% with only current-tool/actual-state operation inputs. For 3B, 35.67% rises to 39.67%. Operation-input organization matters, but history length, future lists, and format change together, preventing attribution solely to identity or attention.

## Supported scope

The firmer observation is that **label representation substantially affects long-execution extrapolation in this task**, and positions do not reproduce stable-identity gains. Identity itself is not causally isolated: position headers after step2 never appear as training headers; two new conditions have approximately 2.96% more supervised target tokens than original names, and alias inputs are longer. Only one mapping and repeatedly used long-test set are tested. Twenty seeds per scale still share fixed training data/test programs; SD does not cover changed datasets/names.

## Initial novelty assessment

Stable names for tools/skills are established in [Toolformer](https://arxiv.org/abs/2302.04761), [Voyager](https://arxiv.org/abs/2305.16291), and related work. [Atomic Task Graph](https://arxiv.org/abs/2607.01942) explicitly manages subtasks/dependencies. [From Fixed Keys to Readable Schemas](https://arxiv.org/abs/2609.09476) directly compares function-identity representations; [Attributing Structured-Output Gains](https://arxiv.org/abs/2607.02595) notes interface alignment can be mistaken for program-capability gains.

A possible contribution is narrower: **after matching format and training exposure, does outputting current-tool identity independently improve short-training to long-execution extrapolation, and does that transfer to complete real-agent tasks?** Neither key validation is complete, and publication-level novelty is unestablished. arXiv/OpenAlex/Semantic Scholar rate limits constrain preliminary searches; this is not exhaustive review.

## Next decision worth reviewing

First isolate key factors with multiple fixed alias maps, matched tokenization/lengths, comparable position-header training exposure, and fresh long programs. If identity gains persist, compare stable task IDs, positions, and semantic task names for a frozen agent on shared real long tasks, fixing tools, budgets, and acceptance checks. Report completion, omissions, early stopping, and costs. If gains disappear, narrow claims to particular word forms/training protocols in a toy task rather than expanding mechanism claims.

## Reading guide

- [20-seed conclusions](label-seed-replication/CONCLUSIONS.md): latest findings, scope, and audit.
- [Detailed 20-seed tables](label-seed-replication/REPORT.md): means, SD, paired differences, and original OOD.
- [Preliminary literature review](label-seed-replication/NOVELTY_REVIEW_2026-09-27.md): primary nearby work and unresolved distinctions.
- [Original four-label conclusions](label-controls/CONCLUSIONS.md): includes 32B and definition-supplied counterexamples.
- [Separate training and context](stability-study/CONCLUSIONS.md): a different handoff protocol, not directly comparable above.
- [Previous-stage review package](review-package-2026-09-26/RESEARCH_REVIEW_CN.md): background preceding the 20-seed replication.
