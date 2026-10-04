# Completion checks and cost accounting

2026-09-28: main experiments and analysis are complete. Verification is based on [final-audit.json](analysis/final-audit.json), [results.json](analysis/results.json), and [resources-final.json](analysis/resources-final.json). See [CONCLUSIONS.md](CONCLUSIONS.md) for the final interpretation.

| Check | Evidence and result |
|---|---|
| Fixed task and starting point | Original Qwen2.5-14B-Instruct, revision `cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8`; fixed L2, nine tools, original STEP/NAME prompts, examples, and chat template; no SFT. Prompt and historical-scorer hashes verified. |
| Data isolation | 4096 training, 256 validation, 512 test, 64 precheck examples; deduplicated within and across sets by call chain plus input, excluding 4954 historical L2 pairs. Full data and source hashes are in [data/manifest.json](data/manifest.json). Each run uses the first 1600 examples after shuffling the training pool, with identical order across conditions. |
| Scoring and loss | Checks against 1968 historical outputs, 128 correct precheck trajectories, and 3 mutations per trajectory verify binary rewards, zero advantage for equal-reward groups, exclusion of prompt/padding from loss, inclusion of actual EOS, and aggregation by token mean within each response followed by candidate mean. See [implementation-tests.json](analysis/implementation-tests.json). |
| Prechecks and recovery | STEP/NAME each run 4 steps. After recovery from step2, step3/4 candidates and rewards match exactly, with maximum final-adapter difference 0. One configuration is selected by correctness, finite values, and reward discrimination, not NAME gain. See [precheck-complete.json](analysis/precheck-complete.json). |
| Configuration freeze | Freeze time precedes all 6 run starts; initialization hashes match for 3 paired seeds, and every step0 LoRA B is zero. All main runs start from original initialization, without main-run recovery or configuration changes. See [freeze-manifest.json](config/freeze-manifest.json), [frozen.json](config/frozen.json), and snapshots/formal-v1/. |
| Complete training | 6 runs of 100 updates, with 16 examples × 8 candidates per update, totaling 76800 candidates. Record-level reward recomputation, within-group advantages, and example-order checks pass. All 6 processes exit normally. Raw candidates, logs, and checkpoints are in runs/v1-*. |
| Fixed checkpoints | step0/10/…/100 per run, totaling 66. Adapter hashes, optimizer states, and both ranks' RNG states verified. |
| All scheduled evaluations | 280 shards and 19968 independent outputs: 1536 original step0 validation/test outputs, 15360 outputs from 60 post-training validations, and 3072 outputs from 6 step100 tests. step0 is explicitly shared rather than counted repeatedly as seed evidence. All raw scores match recomputation. Tests were not used to select checkpoints or alter prompts. |
| Pairing and curves | All seed endpoints, paired differences, means/sample SDs, and fixed 60/70/80/90% thresholds; 66 learning-curve points. Per-example table: [paired-test-items.csv](analysis/paired-test-items.csv); curve table: [learning-curves.csv](analysis/learning-curves.csv). Figures saved in PNG/PDF/SVG. |
| Errors and outputs | Operations, numerical errors, early stopping, extra outputs, and headings recorded separately, with supplementary final-Answer and extra-Trace boundary cases. All 76800 main candidates and 19968 evaluations ended with EOS; 0 truncations. |
| Resources and monitoring | Four GPUs each on .70/.65 for main training; 4 local GPUs for training + 4 for checkpoint evaluation. Normal training checked after 1 hour, recorded in [hourly-checks.jsonl](logs/hourly-checks.jsonl). All 6 training and 4 evaluation workers exit normally; measured final memory occupancy is 0 MiB on all 16 GPUs. |

## Timing results

Timing sources are training logs, each evaluation task's metadata, and job_runner process durations. See [cost-audit.json](analysis/cost-audit.json) for details.

| Scope | Measured GPU-hours | Definition |
|---|---:|---|
| Three main STEP runs | 6.954 | Two GPUs per run × process wall time, including startup/loading/saving/waiting |
| Three main NAME runs | 7.049 | Same definition, approximately +1.36% relative to STEP |
| Total main training | 14.003 | Actual allocated GPU wall time across six processes |
| Evaluation-task time | 1.550 | Sum of task wall time over 280 shards, including first model loading and checkpoint changes |
| Evaluation generation, included above | 1.503 | Sum of generate timings; not added again to the row above |
| Complete evaluation-worker lifecycle | 5.005 | Includes waiting for training checkpoints; contains evaluation-task time and must not be added to it |
| Prechecks/recovery with complete timing | 1.711 | Retained v1, v2, and both recovery tests; outside the main-training budget |

Main training generated 5,102,584 output tokens; evaluation generated 1,321,074. At a fixed 100 updates, output-token totals are nearly the same across conditions, while time still differs. Sampling/update GPU time on the curve axes excludes loading and saving; whole-run allocated time in the report includes them. These measures are kept separate, and allocated GPU time is not treated as active kernel time.

Two initial torchrun argument-parsing failures occurred under the earlier launcher and lack complete exit durations. Failure logs are retained without inventing GPU-hours. NCCL infrastructure probes and CPU data/analysis work are outside the model-job timings above. Idle evaluation GPUs were not filled with unrelated inference or seeds outside the protocol while workers waited.

## Retained failures and scope

The initial `--run` argument conflicted with a torchrun option and caused exit before training; it was renamed `--output-dir`. Precheck v1 showed numerical differences after recovery despite matching loaded weights and RNG states, with the earliest differences during backpropagation/updates. Enabling deterministic algorithms in v2 produced elementwise-identical recovered results before freezing the main configuration. NCCL initialization took approximately 225 seconds and once exceeded the SSH client wait time; handling followed the actual process state, without treating client timeout as training completion. Details are in [infrastructure/DIAGNOSTICS.md](infrastructure/DIAGNOSTICS.md).

All main training completed normally, without OOM, NaN, or interruption. STEP seed301 update 58 had a single-rank KL peak of 0.680 and pre-clipping gradient norm 3.824; NAME seed302 update 91 had a KL peak of 0.309 and pre-clipping gradient norm 1.977. Training continued with the original clipping configuration rather than stopping for isolated peaks. Subsequent curves showed no sustained collapse.

The first offline plotting attempt failed because the training venv lacked matplotlib. Plotting was completed using the existing project .analysis-venv (matplotlib3.10.1), without installing packages into or changing the frozen training environment and without retraining. Original failure logs and exit markers are retained, with final analysis completion recorded separately. Other historical experiments were unchanged.

Precision is a frozen BF16 base with FP32 LoRA branches and optimizer states, without quantization. See [METHOD.md](METHOD.md) for GRPO implementation, precision, KL, and advantage details. Completion covers only this fixed-L2 study with STEP/NAME and 3 paired seeds. No internal rewards, additional models/lengths/seeds, automatic prompt optimization, practical-task transfer, or external publication were added.
