# Stage-one amendment: model scale, prior capability, and early termination

2026-09-24. The user supports the agent-completion proposal and prioritizes tens-of-billions scale validation before extrapolating from ≤3B. This supplements execution design; no new weights/training have been downloaded/run yet.

## Research questions

Q1: Does the same short-call fine-tuning still produce two-segment stopping as one base-model family scales from 1.5/3B to 7/32B?
Q2: Do tool-identity label gains shrink with scale?
Q3: Do post-training and more reliable instruction following provide additional protection?
Q4: Do differences reflect initial capability, learning speed, fine-tuning perturbation, or stable task-structure use?

More parameters do not guarantee richer or more stable priors. Scale trends are not randomized single-factor effects; pretraining/checkpoint differences remain. Establish within-family associations, then narrow explanations through dose, instruction variants, and known-semantics conditions.

## Models and execution order

Primary series: Qwen2.5-1.5B/3B/7B/32B Base. Reuse audited 1.5/3B primary results and add 7/32B. Complete new mechanisms/baseline diagnostics under common protocols at every scale.

Prioritize six 32B Base flat/macro × seed11/22/33 runs, then the same six 7B runs. Complete the planned comparison even without 32B degradation; continuation does not depend on positive results.

Bridge: Qwen2.5-32B-Instruct frozen and flat/macro-fine-tuned conditions, separate from Base. Instruction-model scale trends require smaller matched Instruct models, not 3B Base versus 32B Instruct. Instruct uses official chat templates consistently; Base retains original text templates.

Official model source:
https://huggingface.co/Qwen/Qwen2.5-32B (32.5B parameters, 64 layers, Base)
https://huggingface.co/Qwen/Qwen2.5-32B-Instruct
https://huggingface.co/Qwen/Qwen2.5-7B

Freeze Hub revision/file SHA before downloading into project caches via the existing proxy. Same-family selection reduces confounding rather than competing for the latest model. Real-agent stages may separately select a strong instruction model.

## Matching training intensity

Retain 4,096 original examples, short-call distribution, LoRA rank16/alpha32/target_modules, 512 steps, effective batch32, LR3e-4/schedule, BF16. Equal examples/steps do not match FLOPs; report LoRA parameter counts/proportions. Adjust microbatch/accumulation only for memory, preserving effective batch/order. Prefer activation checkpointing to 32B-only quantization confounding.

Fix checkpoints 0/16/64/128/256/512. Report complete short-mastery, long-accuracy, trajectory, and stopping curves without test-optimal selection. Select mastery-matched secondary checkpoints from development using a predefined short-call threshold. Disclose failure to reach it; poor tool execution is not resistance to stopping bias.

Prespecify symmetric low-LR 1e-4 sensitivity for 3B/32B, since rates can affect scales differently. Lock before formal runs; retain all results rather than tune one model or discard settings. If resources constrain, finish original-recipe scale comparisons first.

## Prior-capability diagnostics

Frozen models cannot know arbitrary color definitions that are not supplied. Add full-definition/explicit-operation-plan frozen baselines at every scale, with local operation accuracy.

Report these separately without altering original train/test matching. Compare before/after training on identical definition-supplied benchmarks. Strong initial 32B long execution followed by stopping after narrow training would support interference with prior capability. If it already fails, inspect task wording/model use instead of assuming intelligence from size.

Natural names, arbitrary IDs, and dynamic renaming are later paired mechanism groups, since semantics can alter difficulty. Base/Instruct contrasts show post-training associations, not pretraining-knowledge stability alone.

## Metrics and identifiable limits

First endpoint: early-answer rate across all long tests, checked against complete trajectories, including every success/failure rather than only macro-correct/flat-wrong cases. Also report exactly-two-segment endings, segment counts versus requirements, operation/arithmetic errors, answers, equivalent/chance-correct trajectories, and token/step caps.

Primary effects per scale: flat−macro early-stopping and macro−flat completion differences. Pair tasks, cluster program templates, and separate seeds. Trends need not be monotonic; do not impose improvement curves. Old tests replicate; new held-out templates confirm.

Stopping position is observed behavior. Prior preservation/attention tracking remain explanations requiring interpretation with random-label, position, and identity controls.

## Outcome branches

1. Little 32B flat early stopping and no label gain: narrow relevance to small models/specific recipes. Reestablish the error in real agents rather than train larger models until they fail.
2. Persistent 32B early stopping reduced by identity: the issue extends beyond ≤3B; proceed to real interaction validation.
3. Degradation only at high LR/prolonged fine-tuning: focus on dose-induced stopping bias, not an equivalent natural deficit.
4. Base struggles but Instruct improves: prioritize post-training/instruction differences rather than pure scale.
5. All 32B conditions have poor local execution: capability is unestablished; diagnose configuration/templates before interpreting scale.

## Resources

Eight local RTX PRO6000 Blackwell GPUs, approximately 96 GiB each, were idle at inspection. BF16 32.5B weights require approximately 65 GB (60.5 GiB), plus activations, LoRA gradients/optimizer, KV cache, and temporary storage. First test single-GPU small microbatches/checkpointing; arbitrary batches are not guaranteed to fit. If needed, use two-GPU training partitioning; inference device_map sharding is not automatically reliable training.

Calibrate loading, forward/backward, throughput, and memory, estimate six primary 32B jobs/other conditions, then launch the fixed matrix. Keep environments project-local and inspect long tasks infrequently by stage. Routine approved local choices need no repeated permission; do not request paid external services.
