# Second-stage oracle ablation: implementation registration

2026-09-25. Authorized by the user and registered before any new model results. The main question is whether two subtasks can be learned separately; decompositions of existing natural outputs are not treated as oracle experiments.

## Model and data

Qwen2.5-32B Base, original revision1818d35814b8319459f4bd55ed1ac8709630f003. Use the original 4096 training examples, development set,560 tests, and 480 independent confirmation examples. Primitive operations and 9 tool definitions are unchanged; no extra library definitions enter inputs. All conditions train independent LoRA adapters from the same base, seeds11/22/33, rank16 alpha32 dropout0,7 linear-layer types, lr3e-4,512 steps, effective batch32,20 warmup steps and original cosine schedule, AdamW weight_decay .01. Record oracle and predicted-token counts; equal examples/steps do not imply equal supervised-token counts.

## Protocol and three training conditions

Append one shared handoff protocol to the original prompt: each tool starts with its original name:\n; after complete operation lines, model/program emits EndTool\n, and the full name sequence ends with Done\n. There is no hard gate requiring a prescribed call count before termination. Digits are unchanged. Explicit EndTool ends free-generated segments; reference operation-line counts cannot truncate them. Done means the model believes it is finished, without forcing correct timing.

- joint: loss covers names, operations, EndTool, and Done.
- order_oracle: the program supplies and masks each correct name; the model learns operations and EndTool; the program supplies and masks task-level Done. At test time the model cannot choose wrong names, but may miscompute, omit, or add within-tool operations.
- operation_oracle: the model learns names and Done; the program supplies and masks operations and EndTool for the selected name. Inference executes the tool actually selected using the actual current numbers, without correcting names. Invalid names fail. Model-generated Done determines termination and may occur early or after too many calls.

All three conditions see exactly the same correct training text and differ only in supervision masks. Save offsets and token-source audits; oracle segments must not count as correct model predictions. EOS contributes to loss in joint/operation_oracle and is masked in order_oracle. A same-format joint control handles template changes; historical macro/step results are external references rather than single-factor controls.

## Inference and scoring

Regenerate from the complete concatenated history without reusing KV cache across oracle insertions. Record actual token IDs, raw text, source, stopping reason, and tool state for every segment. Generate headers to newline and bodies to EndTool newline. Any model-segment EOS/format error/budget exhaustion fails, without program correction. The 16-tool limit protects resources, not correct length. Caps are 24 header tokens,128 body tokens,2048 total output,4096 input+output, all comfortably above the longest 8-call reference and recorded per example. All models default to greedy decoding.

- order_oracle: correct expansion of every required call, including operation sequence and numbers; also report per-call performance. Parseable incorrect numbers pass through unchanged. Separate local and global correctness.
- operation_oracle: the full tool-name list is correct and Done occurs at the appropriate point. Program execution is not model capability.
- joint: complete sequence, all operations, numbers, and termination are correct under free calling; also extract both subtask scores.
- Joint models also run in both oracle environments to distinguish split training from inference assistance. First calibrate on a small scale to validate the executor, then run all scheduled evaluations without selecting checkpoints on tests.

## Stages and acceptance

First validate tokens, boundaries, and injected errors, then calibrate 32B with short forward/backward passes for memory and speed. If passed, run 9 training jobs (3 conditions x3 seeds). Save step64/128/256/512 adapters; the primary final result is fixed at 512. Intermediate checkpoints support development diagnostics only, not selection. Training volume should resemble the original 32B study, approximately 1.7 GPU-hours per original job; new protocol/segmented evaluation adds cost, with estimates updated after measurement. If the compute gate fails, repair and register a new version while retaining failures, without changing tasks/scoring to manufacture positive results.

Report subtask/joint success for lengths3/4/5/6/8, complete per-example trajectories, errors, supervision volume, costs, and three-seed dispersion. Oracles do not prove internal independence. Assess whether separately trained component ability approaches jointly trained ability and whether differences arise from protocol/context/supervision volume. Earlier natural-output B covers only generated calls; order_oracle here covers all required calls and is not directly equivalent.

## User-added small-model resources and pairing (preregistered)

Add Qwen2.5 Base 1.5B,3B,7B under the same protocol, each 3 conditions x3 seeds, for 27 small-model runs plus 9 at 32B, totaling 36. Six new 5090 servers each have 8 GPUs with 32 GB and share this directory. Environments/models are fixed; paired allocations are in infrastructure/allocation.json. Microbatch is 8 for 1.5B/3B and 4 for 7B/32B, with effective batch32 unchanged. First calibrate two joint forward/backward steps per scale. Program checks include batched asynchronous segment endings, uncorrected wrong tools, propagation of wrong numbers, and allowed early stopping. Calibration failures may change only runtime settings such as microbatch/accumulation, not learning rate, task, or acceptance standards; record changes.

Every main job automatically evaluates original 560 and independent 480 examples after training. Joint models run all three inference modes; specialists run only their matching oracle mode. Total 36 training jobs,60 model/mode combinations,62400 main trajectories. Record full inputs, program/model token segments, states, and scores. Reduce polling during normal long jobs; starting jobs is not completion.

## Scheduling change (training function unchanged)

Two initial 32B operation_oracle jobs finished and freed GPU2/5, while seed33 operation_oracle was queued behind all-mode joint evaluation on GPU0. To avoid idle GPUs, move this sole unstarted training job to GPU2. When the original GPU0 queue reaches it, wait for and validate external training, then evaluate. The main training-function AST in train.py is verified unchanged; only __main__ adds an explicit single-job lease takeover. Parameters remain microbatch4/512 steps/seed33. External owner PID and command are in analysis/external-qwen32b-operation_oracle-s33.json. Takeover neither overwrites partial directories nor blindly restarts without an owner; error paths are tested. Preserve prior source and hashes. Main evaluation code, training data, and scoring are unchanged.
