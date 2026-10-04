# First research candidates: idea review

2026-09-23. Project: EvoScientist + EvoSkills. Awaiting user review; none of these training experiments, proofs, or results drafts has started.

The direction asks whether model iteration develops reusable innovation, provisionally measured by curricula improving subsequent learning or abstractions reused across tasks. These bounded measures do not establish general scientific innovation. Record assistant GPT separately from experimentally trained open bases. Candidates are preliminarily reviewed questions, not confirmed original methods.

Prioritize B01-02 for relevance/testable mechanisms; B01-03 second for falsifiability despite artificial-task risk; hold B01-01 because dense recent literature raises incremental-contribution risk.

## B01-01: does generated-curriculum utility transfer across models and optimizers?

**Question.** Are examples useful after training student A specific to its parameters/optimizer? Controlling difficulty, accuracy, and compute, can curricula help reward-excluded student C? Measure actual post-update gains rather than answer disagreement.

**Closest work.** [INFUSER](https://arxiv.org/html/2606.09052v4) §2 rewards optimizer-aware influence; [SOAR](https://arxiv.org/html/2601.18778v1) §3 uses short student updates averaged across copies; [DARC](https://arxiv.org/html/2601.13761v1) §4 demonstrates cross-size reuse; [Beyond Uncertainty](https://arxiv.org/html/2608.30035v1) §4 rewards heterogeneous-solver disagreement. Utility rewards, multiple students, and transfer are not themselves new.

**Unverified distinction.** Make utility on reward-excluded families/optimizers primary and separately tested. Compare real updates with disagreement, difficulty, and single-student influence. A multi-student lower-quantile objective is only a candidate; combining existing ideas is insufficient. Value requires systematic mismatch and repeatable repair, not merely another reward formula. Exact overlap remains possible.

**Assumption.** Single-student utility has separable model-specific components; shared utility predicts unseen learners. Nearly invariant rankings across students/optimizers weaken motivation.

**Minimal experiment.**
1. Executable string/integer programs, structurally separated across training, reward-development, and tests. Verifier truth prevents pseudo-label errors contaminating utility.
2. Fix one generator and approximately 256 batches; measure 8–16-step gains, difficulty, and disagreement on two 1–3B families, reserving a third for final transfer. Diagnose rankings before large meta-RL.
3. After a signal, compare equal-budget random, difficulty, disagreement, single-student, and multi-student curricula, accounting for generation/scoring/training. Three seeds and fixed output-token budgets.
4. Measure unseen-family accuracy gains, learning-curve area per GPU-hour, and utility-rank correlation. Ablate learner diversity, optimizers, and real updates versus gradient approximations. Charge extra-student compute.

**Estimated resources.** Initial diagnosis 32–64 GPU-hours; if passed, full small comparison 96–192 on four to eight local GPUs over approximately 2–4 days including implementation/debugging. These unmeasured short-sequence 1–3B estimates exclude full INFUSER/SOAR replication. Calibrate 20 steps after theory review, then revise.

**Drop criteria.** No stable utility mismatch; or cost-accounted unseen-student gains fail to exceed the best baseline by two points with uncertainty including zero; or gains occur only for rewarded students. Three seeds screen only; near-threshold outcomes remain uncertain.

**Judgment.** Recommendation C, hold. Dense literature requires clear mechanisms and cross-family evidence.

## B01-02: do model-invented abstractions become composable capabilities in weights?

**Question.** After proposing reusable functions from solving traces, validation, and training, can a model use their semantics in unseen compositions without a library? Are gains from abstractions, additional correct answers/tokens, or memorized names?

**Closest work.** [LILO](https://arxiv.org/html/2310.19791v2) compresses interpretable libraries; [Notes to Self](https://arxiv.org/html/2607.20372v1) §3–4 tests abstraction-assisted training without test abstractions; [SPEE](https://arxiv.org/html/2608.02139v1) internalizes evolved experience through privileged distillation; [Rethinking Continual Experience Internalization](https://arxiv.org/html/2606.04703v1) studies stability. Library invention, removing prompts, and experience in weights are not novelty claims.

**Unverified distinction.** Pair training data and intervene on model-proposed executable abstractions: does behavior follow changed semantics and survive renaming? Potential contribution is controlled abstraction-driven composable learning and resulting constraints, not one benchmark gain. Main nearby works do not directly establish this exact comparison; citation tracing remains necessary.

**Assumption.** Some proposed abstractions reduce description complexity and transfer beyond information-matched direct-trace distillation. Retrieval-only use does not support parameter internalization.

**Minimal experiment.**
1. Restricted-DSL string/list transformations. Propose approximately 20–50 macros from actual successful/failed traces; sandbox-check equivalence, types, and resources. Measure valid rates/compression. Separate ASTs to prevent same-program/different-number leakage.
2. Four token/update-matched groups on one 1–3B base: correct traces, natural-language experience, executable-abstraction assistance, and same-length ineffective-abstraction control. Keep frozen base plus library as an upper-bound capability reference, with separate costs.
3. Test unseen 3–5-layer compositions without libraries. Pair fixed-semantics/randomized-name and fixed-name/changed-definition training. Supply changed rules during training rather than demand guesses of unknown rules.
4. Measure library-free composition, semantic responsiveness, and naming stability. Ablate generation/validation/internalization; check memorized long-program expansions and retain an independent generator test.

**Estimated resources.** Four conditions × three seeds, 1–3B, sequence cap 2048, approximately 2–5M training tokens per condition. With generation/interventions: 48–120 GPU-hours, two to four GPUs, approximately 2–4 days including implementation. Review excess budgets rather than silently remove controls. Unmeasured estimates.

**Drop criteria.** No stable ≥3-point no-library gain over matched distillation; gains disappear after AST deduplication; semantic insensitivity with strong naming sensitivity; or scarce valid abstractions with simple manual macros explaining all gains. Negative results may remain diagnostics without a promised paper.

**Judgment.** Recommendation A, prioritize mechanisms. Closest to inventing reusable concepts and learning them, with feasible small-model interventions. Main risk is artificial-DSL success without natural transfer.

## B01-03: does immediate-utility filtering discard complementary stepping stones?

**Question.** Can individually unhelpful packages A/B yield useful A→B training for unseen composition? Does one-round filtering discard A and obstruct iteration? Focus on identifiable complementarity rather than vaguely looking further ahead.

**Closest work.** [SOAR](https://arxiv.org/html/2601.18778v1) optimizes ten-step updates and accumulates promotion tasks; [INFUSER](https://arxiv.org/html/2606.09052v4) uses local influence; [Learning to Self-Evolve](https://arxiv.org/html/2603.18620v1) §3.3 proposes cumulative objectives but simplifies to one-step context updates. Multi-step gains, stepping stones, and long-term objectives have precedents.

**Unverified distinction.** Identify order-dependent complementarity of individually unhelpful batches under real updates. Estimate through reversible paired short updates, then test retention in generated curricula. Longer reward windows alone are insufficient; beat compute-matched long windows, random retention, and replay.

**Assumption.** Complementarity is common and cheaply predictable, not entirely extra steps, easy-to-hard order, or replay.

**Minimal experiment.**
1. Approximately 128 packages in executable composition/small symbolic derivation with two structurally independent generators, not one hand-designed A→B example.
2. Restore identical model/optimizer states for A→B, B→A, A→A, B→B, random→B at equal tokens/updates/tests. Observe 8/32/128-step windows to distinguish noise/delay.
3. Only repeatable paired signals justify later authorized generator training. Compare one-round filtering, fixed long windows, random retention, replay, and complementarity retention. Tests do not select pairs/windows.
4. Measure useful-pair frequency, compute to matched accuracy, and net gains after at least three rounds. Use three seeds and retain failed pairs rather than selected successes.

**Estimated resources.** Diagnosis 24–48 GPU-hours; complete small loop 72–160, two to four GPUs, approximately 2–4 days with implementation. Short-sequence 1–3B models, calibrated before commitments. Large-model meta-RL is outside initial budget.

**Drop criteria.** Gains disappear under equal steps/tokens, exist only in designed dependencies, lack repeatable ≥3-point gains across two generators, or match cheaper random retention/replay. Unresolved windows do not turn noise into deep long-term innovation.

**Judgment.** Recommendation B, second choice. Clear mechanisms and informative counterexamples, with greater toy-task risk than B01-02.

## Budget, evidence, and review agreement

GPU-hours are GPU count × actual allocation time, including generation/scoring/training/evaluation, not wall time alone. Screening ranges use measured hardware models, not training throughput; matrix-smoke speed is not extrapolated. Implementation, downloads, shared storage, and learnability may dominate. Start with small open bases; freeze checkpoints/licenses/dependencies during authorized mechanisms. Do not transplant full SOAR paper budgets locally.

Recommend B01-02 for theory/mechanisms, B01-03 as backup, B01-01 on hold. Next review covers definitions, identifiability, controls, confounds, preregistered metrics, and budgets before implementation/runs.

No missing item blocks idea review. Training needs a local stack/full weights. paper-navigator deepxiv-sdk/optional credentials, end-to-end WebUI, and distributed training remain unverified. These do not block Tavily/arXiv review or require new keys now.
