# Qwen2.5-0.5B in-domain label replication: preregistration

Date: 2026-09-27. User authorization: change only model scale in the original label experiment and first replicate training lengths 1–2. If the in-domain STEP baseline remains saturated, extend maximum supported training length successively to 3, 4, 5, 6, 7, and 8. Evaluate only supported lengths. Do not run original OOD or earlier independent long-sequence tests.

## Inherited settings

- Qwen2.5 **Base**, LoRA r16/alpha32/dropout0, seven original projection types, AdamW, LR 3e-4 with original schedule, 512 steps, microbatch 16 × accumulation 2, and 16384 example presentations. Reuse the original trainer algorithm without test-based checkpoint selection.
- Original nine tools, four-digit operations, prompt, Answer termination protocol, and target format. flat/position/alias/macro definitions match the 2026-09-26 experiment exactly. The alias mapping still comes from `random.Random(2026092601)`.
- Twenty seeds: 11, 22, 33, and 100–116, paired across conditions. `set_seed` controls LoRA initialization and training-data shuffling. Use greedy generation, original short-test batch 32/max_new_tokens256, and the existing strict complete-trajectory scorer.
- Maximum length two reuses the original 4096 training examples and 128 IID short tests verbatim. Do not add original OOD/pressure, old independent 480-example, or with-library evaluations. Training steps and budget do not grow with length.

## Changes and sequential thresholds

The sole model change is to official `Qwen/Qwen2.5-0.5B` Base, with frozen revision and manifest. At maximum length two, run only the 20 flat seeds first and check strict in-domain accuracy on 128 examples.

Initial definition of near-perfect saturation: flat mean strict accuracy ≥99% across 20 seeds and at least 19/20 seeds individually ≥99%. If unmet, **stop at maximum length two and complete the formal four-label comparison with 20 seeds**. Otherwise freeze those flat results and extend lengths sequentially, first training 20 flat seeds at each level. At the first level below that same saturation criterion, train the remaining labels. If length eight remains saturated, report saturation at all flat levels without further automatic expansion. Never advance based on identity-label results.

Before running lengths 3–8, extend the original sampling, deduplication, digits, prompts, and tool-library logic to 1–L. Retain files, generation seeds, sampling records, and hashes. Each level fixes 4096 training examples, effective batch, and 512 steps. Evaluate only frozen in-domain tests at lengths 1–L. Extending length changes the example distribution, the only additional experimental variable authorized here. Compare labels within each level; cross-level scores do not measure improvement on one shared test set.

## Primary endpoint and audit

Primary endpoint: strict complete-trajectory success across all in-domain tests. Report each label with 20-seed mean, sample SD, every seed score, same-seed differences and intervals, plus each call length. Descriptive learning curves may use only existing trainer checkpoints; do not change training to save extra points.

Retain every run configuration, frozen source, training log, adapter, raw output, and failure. Verify revision, 512 steps, 16384 examples, prompt/target consistency, data coverage, and the old scorer. Inspect normal training hourly and handle completion/failure promptly. Keep all files within the project without overwriting earlier experiments.

## Future notes, outside this round

Near term: prompt-only comparison of rules/plan alone versus repeating current tool identity before execution. Longer term: related-work/novelty review and transfer to automatically verifiable real execution tasks, testing supplied plan → pre-execution subtask identity → completion. Public claims and individual contributions must follow actual evidence.

## 2026-09-27 pre-run amendment from latest user instructions

The user rejected the above 99% saturation threshold before it was used. Retain it as history, but replace it before any 0.5B training/evaluation: sufficient headroom requires STEP **mean strict in-domain success ≤90%** across 20 seeds and at least 15/20 seeds individually ≤95%. Select the first maximum-length level meeting this rule for the four-label comparison. If none of lengths 2–8 qualify, complete all seven STEP screening levels and honestly report the length-eight baseline/headroom without adjusting levels for expected identity-label gains. Length one is covered by the original length-two training set and receives no separate training.

The 90% threshold identifies baseline error headroom; it guarantees neither method effectiveness nor publication-strength evidence. Conclusions depend on paired seed differences, between-seed SD, length-specific results, raw failures, and honest intervals. Selection uses STEP only and reports all label outcomes. Because baseline screening selects the level, subsequent intervals are not confirmatory tests on a completely prespecified task.

## Length-extension details frozen before starting length three

All 20 length-two STEP seeds achieve 128/128 strict success, triggering extension under the revised rule. For each L=3–8, independently generate 4096 training examples using the original principle: sample uniformly from all nine-tool chains of length at most L, draw four digits uniformly, and deduplicate chain/input pairs. Fix data seed `900+L` and freeze files/SHA256 before training. Preserve a direct anchor to length two by retaining the old 128 one-/two-call IID tests, adding 128 frozen examples for every new length 3–L. Each level thus has `128*(L-1)` tests, all training-supported. Twenty seeds share the same training/test files and labels are paired.

Longer targets may exceed the old 256-token training assertion or generation limit. Precheck maximum targets; only if exceeded, raise capacity enough to fit complete training/test targets. Preserve greedy decoding, prompts, targets, parsing, scoring, optimization steps, and budget. Record per-level changes and values in prechecks. This necessary compatibility adjustment does not alter old experiments.
