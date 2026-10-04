# Methods and verification

See the [preregistration](REGISTRATION.md) for the scope, selection rule, and budget. The earlier experiments in the neighboring `grpo-binary` and `prompt-only` directories are referenced read-only. Training, data, and results for this study are stored separately.

## Fixed protocol

- Qwen2.5-7B-Instruct: revision `a09a35458c702b33eeacc393d103063234e8bc28`, fixed L3/L4/L5.
- Qwen2.5-14B-Instruct: revision `cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8`, fixed L5/L6/L7.
- Each setting uses STEP/NAME and seeds 301/302/303; each run has 100 updates with 16 examples × 8 candidates. Each length has 4096 training, 256 fixed validation, 512 fresh test, and 64 independent precheck examples. The 100 updates use 1600 training examples shuffled by seed, rather than a full epoch.
- The original nine tools, four-digit states, supplied call plans, prompts, and examples are retained. STEP requires `step:`; NAME requires the current tool's name. Full templates are in each task's `config/prompt-STEP.txt` and `prompt-NAME.txt`; reference originals are archived in `snapshots/reference-inputs`. The chat template comes from the original tokenizer configuration, whose SHA256 matches the download registration.
- Generation: sample each tool index and input digit independently and uniformly, then deduplicate by call chain and initial state. Training/validation/test/precheck sets are disjoint and exclude same-length examples from the 29 registered historical data sources. The four L5 sets are byte-identical across the two models. The fixed example is L2, distinct from all L3–L7 lengths in this study.

## Training and reward

We reuse the previous working implementation: a frozen BF16 base with LoRA r16, alpha32, dropout0, applied to the seven q/k/v/o/gate/up/down projections. LoRA parameters, branch computation, and optimizer states use FP32; PEFT casts branch outputs back to the base output dtype. There is no quantization, additional SFT, or previous adapter. Computation is therefore not entirely BF16.

Training uses two-GPU DDP with microbatch4; sampling batch32, temperature 1, top_p1, and top_k0. AdamW uses learning rate 1e-5, a 5-update linear warmup followed by a constant rate, betas(0.9,0.999), eps1e-8, and weight_decay0; the gradient norm is clipped at 1. Deterministic algorithms and the original SDPA and gradient-checkpointing settings are retained.

The task reward is strictly trajectory-level 0/1: the operation sequence, every intermediate state, and the unique final Answer must satisfy the historical scoring semantics to receive 1. Tool/heading compliance earns no reward. There are no character-level, prefix, or local-step rewards. Headings are normalized before the historical scorer is applied, and heading compliance is reported separately. The historical scorer permits some generic heading lines; the stricter requirement that Answer must be the last line is not added as a new primary scoring condition.

Each example has 8 candidates. Advantages are normalized by the group's sample reward standard deviation (ddof=1) plus 1e-4. All-0 and all-1 groups have zero advantage, though KL gradients may remain. Advantages apply to valid output tokens across the full response; the loss averages over valid tokens within each response, then across responses. Actual EOS tokens are included; prompt and padding tokens are excluded. Unit checks cover the resulting gradients.

Each fresh sample batch is followed by one optimizer update (μ=1). The implemented ratio has a forward value of 1, so clip_epsilon0.2 does not produce actual multiepoch policy clipping; this is not multiepoch PPO. The reference policy is the same frozen base with adapters disabled. The KL coefficient is 0.04, with estimator `exp(logp_ref-logp)- (logp_ref-logp)-1`. KL is an optimization regularizer, not an additional partial task reward.

For each seed, the two conditions use the same LoRA initialization, example order, effective batch, sampling configuration, and update count, and run sequentially in the same physical two-GPU slot. Generated trajectories and random-number consumption may differ. Actual output tokens and GPU time are reported separately; equal update counts do not imply equal compute.

## Prechecks, freezing, and evaluation

Each condition/task first runs 4 precheck updates, then resumes from step2 to step4. Resumed candidates, adapters, and optimizer states match in all 12 groups; the maximum adapter difference is 0. Each task also checks 128 correct trajectories and 3 mutations per trajectory, rewards on 1968 historical outputs, advantages, and mask/EOS gradients. Every main run starts afresh from the original initialization. Configurations are frozen together before main training, with no hyperparameter changes based on NAME's lead.

The generation budget is prechecked against correct target trajectories from all sets: `ceil((1.25×maximum correct-target tokens+64)/256)×256`. The cap is 256 for L3/L4 and 512 for L5/L6/L7, identical across conditions/models at the same length. Maximum input length plus the budget stays within the 32768-token context. Caps are not adjusted based on main results. The few incorrect generations that hit the cap are retained as truncations.

Adapters, optimizer states, and both ranks' RNG states are saved at step0/10/…/100. Each fixed checkpoint is evaluated on 256 validation examples. The original model at step0 is generated once per condition/task and shared across three seeds. All 36 step0 adapters have been verified to have all-zero LoRA B, justifying the shared original-policy evaluation. The fresh test set is evaluated only at step0 and step100, with 512 examples each; there is no best-checkpoint selection or best-of-retry selection. All evaluation is greedy, with eval batch32.

Validation thresholds of 60%, 70%, 80%, and 90% are fixed in advance; unreached thresholds remain unreached. Initial selection for follow-up uses only the three-seed mean STEP step100 validation success in the 20%–90% range, while retaining all six settings. This exploratory selection is not independent confirmation.

## Resources and exceptions

The local machine has 8 GPUs and each of two remote machines has 4, all RTX PRO6000 Blackwell Server Edition. Routine checks run hourly. Complete job records are in `infrastructure`, and monitoring records are in `logs/hourly-checks.jsonl`.

Main training had no OOMs, numerical failures, or interrupted restarts. The only nonzero controller exit was the deliberate stop of the old scheduler during resource reallocation in the first hour. Six running training jobs were unaffected; four old evaluation workers drained and exited normally before scheduling resumed from the persistent queue. `resource-reallocation-v2.json` and `v3.json` record the allocation of 7 training slots/2 evaluation GPUs and the addition of 2 evaluation GPUs near completion, respectively. Frozen training/evaluation code, configurations, and raw outputs were unchanged. Source code for both the old and replacement schedulers is retained.

## Checking existing artifacts

Run from the project root, replacing `GRPO_TASK_ROOT` with one of the six tasks. These commands do not generate model outputs or start training.

```bash
export GRPO_TASK_ROOT="$PWD/workspace/research/B01-02/grpo-length-study/14b-L5"
.analysis-venv/bin/python workspace/research/B01-02/grpo-length-study/postanalysis/analyze_task.py
.analysis-venv/bin/python workspace/research/B01-02/grpo-length-study/postanalysis/report_task.py
.analysis-venv/bin/python workspace/research/B01-02/grpo-length-study/postanalysis/error_details.py
```

After all six task analyses are complete: `aggregate.py` generates the combined report and figures; `audit_data_models.py` checks historical deduplication and complete original-model file hashes; `audit_lifecycle.py` checks freezes, jobs, data, and total occupancy time; `cost_and_tokens.py` verifies actual output tokens, EOS/cap endings, and costs record by record; finally, `endpoint_costs.py` adds greedy endpoint inference costs.

`audit_optimizer.py` uses the project's `.training-venv` (after `source training-env.sh`) to check actual step0/100 parameters and optimizer states on CPU, without a GPU. Audit results are saved in `analysis/*audit.json`. See [COMPLETION_AUDIT.md](COMPLETION_AUDIT.md) for the full acceptance checks and artifact inventory.
