# Execution learning and improvement capability: extended-study protocol

The user authorized deeper and larger RSI-related research, with autonomous execution followed by review. All environments and outputs stay in the project. No new models, data, or interventions had run when this protocol was written.

## Core hypotheses and falsification
H1: Execution training improves execution but reduces proposal utility on new tasks. Pair identical initializations and report prompt/budget sensitivity. Models without execution improvement do not support separation.
H2: Reduced proposal capability affects next-round execution gains through training data. Intervene on proposal source from identical learner starts. Symbolic compression/search alone does not establish this causal chain.
H3: Preserving/training the proposal objective can recover proposing or loop gains during execution learning. Report failed recovery interventions fully.

Claims progress from artificial-DSL observations to cross-model/task replication and finite-round loops with counterfactual interventions. Without stable H2/H3, do not claim an established RSI mechanism. Finite rounds with human-designed verifiers are not open-ended recursive intelligence improvement.

## A: robustness and model-scale replication
Reuse original three-seed 1.5B flat/macro adapters. Add Qwen2.5-3B and SmolLM2-1.7B flat/macro runs with three seeds each, retaining original data, 512 steps, batch 32, LoRA 16, and LR 3e-4. Tokenizers may change supervised-token counts; report them without claiming cross-model token matching.

Add frozen-base comparisons with three sampling seeds per model. Use original IID/OOD execution tests and format audits. Proposal evaluation uses 32 new families: 12 train, four development, 16 test. Each has three distinct hidden macros, exactly semantically disjoint across splits and from the original nine macros, 12 support programs, and 64 held-out programs with within-family semantic separation. Test families never enter intervention training.

Use fixed instruction, concise, and two-example prompts at temperature 1, plus instruction at 1.5. Sample 64 proposals per support set and evaluate prefixes K=4/16/64 with the same selector and complete curves. Primary setting: instruction T1/K16. Constrain the same 252 candidates and report duplicates, semantic diversity, and zero utility. Use the earlier sensitivity-validated selector that compares literal gains before removing semantic equivalents after selection.

## B: three-round closed loop
Start 1.5B from the same base across three seeds. Train three rounds of 128 steps, batch 16, LR 1e-4, LoRA 16, totaling 384 steps. Each round proposes candidates on 12 training families and selects up to three macros. Selected libraries shape next-round operations: 80% selected-macro concatenations and 20% uniform primitives; empty libraries use only primitives. Each example has 2–3 fragment calls. The executor supplies correct steps, so supervision is environment-provided rather than zero external supervision.

shared updates one proposer/executor; frozen keeps the initial proposer and updates the executor; replay adds initial-model proposals on training families; joint adds current support-selected proposal supervision; shuffled uses identical replay prompt/target sets with shuffled pairings. Every step has equal execution-example counts. Auxiliary conditions add proposal loss weighted 0.2. Disclose added compute and save execution/proposal tokens separately. Never select rounds on test results.

Primary metrics: fixed unseen-program execution, test-family net proposal compression, proposal diversity, and actual incremental learning gains each round. Continue after evaluation without test-based hyperparameter changes. Save adapters and example-level outputs at rounds 0/1/2/3.

## C: causal mediation and task replication
Copy two 128-step branches from the identical shared round-1 adapter, using either the updated model or frozen base for training proposals. Match executor, learner, seed, and budget; compare fixed-test execution gains. No difference or reversed direction does not support H2; compression cannot substitute.

Replicate shared/frozen/joint three-round procedures across three seeds under separate variable-length binary-string semantics. Share syntax but train, execute, and evaluate separately; do not claim zero-shot domain transfer.

## Interpretation, resources, and delivery
Compare paired seeds and test families. Report wide intervals from few seeds without inflating sample counts with examples. Show all prompts/budgets and rounds rather than choosing favorable test settings.

Expect dozens of independent GPU jobs. Measure throughput and proceed in stages, initially estimating 10–40 GPU-hours subject to measurement. Use eight local RTX PRO6000 GPUs, approximately 96 GiB each, without paid external resources. Freeze model revisions/hashes, avoid global-environment changes, and inspect long tasks infrequently by stage.

If nearby work covers broad observations, narrow claims to measured identifiable differences rather than assuming novelty. Retain failures/counterexamples, revise claims, and deliver complete evidence. Outputs are a report and reproducible assets; do not submit or present them as published work before user review.
