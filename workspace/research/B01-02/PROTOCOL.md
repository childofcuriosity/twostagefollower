# B01-02: mechanism analysis and preregistration before results

The user authorized combined mechanism analysis and experiments followed by review. Question: can executable abstractions proposed from model-generated program traces yield library-free compositional generalization through parameter updates beyond information-matched flat-trace training? This is controlled mechanism screening, not a paper or proof of general innovation.

## Identifiable claims

H1, internalization: updated parameters execute learned macros and untrained macro compositions without an external library.
H2, structural utility: with matched base, tasks, expanded programs, correct intermediate states, and answers, macro-boundary-organized supervision improves unseen composition over flat supervision.
H3, semantic dependence: permuting training-world macro definitions changes behavior toward the new semantics; consistent name permutations largely preserve capability.

Falsification criterion: an accuracy difference of at least three points with consistent direction across three paired seeds establishes an H2 signal worth pursuing; wide intervals remain uncertain. Falling short or beating only incorrect/random labels does not pass. Gains only on training compositions or with supplied libraries do not support library-free generalization.

Finite input/output observations cannot uniquely identify internal algorithms: lookup and rule-based models may behave identically on finite tests. H1/H3 provide operational evidence, not unique neural-mechanism identification. Neural claims require later representation interventions. This round does not claim new primitives beyond the training language, general scientific innovation, or recursive improvement.

## Causal comparisons

Shared information I comprises inputs, macro-call order, every expanded primitive, all correct states, and the answer. The executor supplies identical I. Treatment G is only each boundary label: correct macro name, neutral flat word, or unrelated shuffled macro name. Boundary counts/positions match, preventing added steps from being attributed to abstraction.

Natural-language descriptions derived from the same expansions form a secondary representation control. Their token counts may differ; report costs separately without treating differences alone as causal superiority. Macro versus flat must match boundary-label token length; if the tokenizer prevents this, stop and repair serialization rather than ignore the mismatch.

Report effective training tokens, generated tokens, actual duration, and allocated GPU-hours. Three primary groups share example order and update counts. Primary causal comparisons share initialization/seeds/examples. Natural is not strictly token-matched; shuffled is a negative control, not a replacement for flat.

## Model and abstraction source

Use open-base Qwen/Qwen2.5-1.5B with frozen Hub revision/file hashes and a project-local training environment. First attempt DSL solving, retaining raw success/failure outputs, then propose length-2–3 primitive combinations from those traces. Parse with a whitelist; do not execute arbitrary generated Python. Exhaustively validate candidates over the finite input domain, remove semantic duplicates, and rank by compression on separate discovery data. Failed self-proposals must not be replaced with hand-authored macros presented as discoveries; record failure and narrow claims.

Freeze one proposed library to isolate representation. Tasks built around that library do not establish superiority of discovery policy over random policy. Complete multi-round evolution and natural-task transfer are outside demonstrable scope.

## Tasks and separation

Inputs are four-digit lists with deterministic reverse, rotate-left, increment-mod10, negate-mod10, swap-first-two, and increment-ends-mod10 primitives, composed left to right. Separate discovery, training, calibration/development, and final tests. Train macro depth 1–2 and test 3–5, deduplicating expanded ASTs. Audit equivalent-program leakage using semantic signatures. If exact separation leaves insufficient capacity, report it and stop the corresponding claim.

Retain IID unseen-input tests to distinguish failure to learn from failed composition. Report depths 3–5 separately. Repeated digits, palindromes, and boundary digits form a distribution stress test, not another natural domain.

## Run plan

1. Verifier property checks, AST/semantic separation audit, and actual model inference/training throughput calibration.
2. Frozen-base evaluation with/without libraries as initialization/prompt baselines; supplied-library performance is not a theoretical upper bound.
3. flat/macro/natural/shuffled × seeds 11/22/33 with small-model updates. Use 20-step throughput to fix common steps once, initially capped at 512 steps, batch 32, sequence 256. LoRA must be described as adapter updates, not full-parameter base training.
4. Three-seed macro runs for name and semantic permutations. If the core task is unlearned, diagnose at matched budget rather than expand models. Score each control under its actual training semantics and additionally against old semantics counterfactually.
5. Retain every raw generation, score, input/output, data hash, curve, configuration, failure log, final checkpoint, and analysis script.

## Statistics and decisions

Training seeds are primary independent repetitions; thousands of test examples are not independent training runs. Report seed accuracies/paired differences, means, and t intervals with explicit n=3 limits, plus descriptive AST-clustered bootstrap. Use one final evaluation without test-based checkpoint selection. Calibration sees development only; timestamp protocol changes and state whether results were visible.

The candidate-card 48–120 GPU-hour range is an initial plan, not a spending requirement. Measure first-round scope rather than prolong ineffective training. Independent jobs run on separate GPUs and do not constitute NCCL distributed-training validation.
