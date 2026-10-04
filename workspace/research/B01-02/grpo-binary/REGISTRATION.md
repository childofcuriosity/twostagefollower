# B01-02: binary-reward GRPO preregistration

2026-09-28. The user explicitly authorized implementation, independent prechecks, configuration freezing, 6 main runs, and all scheduled evaluations. Earlier experiments are read-only.

## Fixed inherited settings

Official original BF16 Qwen2.5-14B-Instruct weights, revision cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8. Inherit L2, nine tools, four-digit states, complete definitions and a single example, STEP/NAME prompts, and the official chat template from prompt-only/fallback14. Only heading requirements and example headings differ. There is no additional SFT, other label condition, model scale, or task length. Reward and primary evaluation reuse the historical strict-trajectory scoring semantics, with headings reported separately, rather than introducing stricter character-by-character matching.

## New data

At fixed L2, tool indices are drawn independently and uniformly from 0..8, and each of four input digits independently and uniformly from 0..9. Deduplicate by call chain plus input. Both conditions share 4096 training, 256 validation, 512 test, and 64 precheck examples. The four sets are mutually disjoint and exclude the demonstration example, as well as existing L2 (chain, x) pairs in underlying datasets and evaluation records in the research directory. Exclusion lists and hashes are saved in data-construction records. The previous formal set of 512 examples retains its historical test status and is not used for tuning.

Data seeds: training 910001, validation 910002, test 910003, precheck 910004. Main training seeds are 301, 302, and 303, paired across STEP/NAME. Data-generation seeds are not training replications. Each training seed independently determines example order; the two conditions share initialization and order for that seed. Precheck seed is 930001. Main training, validation, and fresh test examples are not used to select configurations.

## Updates and rewards

BF16 LoRA+GRPO starts from the original model, without prior SFT. Each update uses 16 examples × 8 complete responses per example, for 100 updates across 6 runs. Each run presents 1600 examples and 12800 candidates, totaling 76800 main training candidates. Conditions with the same seed share example order, initialization, effective batch, sampling parameters, and update budget; identical candidates are not required.

Reward is 1 only for a fully correct trajectory, otherwise 0. Historical scoring requires the operation sequence, all states, a unique correct Answer, and no disallowed extra lines. Existing heading normalization is retained; heading compliance does not affect reward. Advantages are centered and normalized within the 8 candidates for each example and applied to every valid token of the full response, including actual EOS but excluding prompt and padding. There are no segment-level or local rewards. KL regularizes the GRPO policy without changing the 0/1 task reward. Learning rate, LoRA, warmup, KL, clipping, advantage standard-deviation convention, and token/sequence aggregation are frozen together after independent prechecks.

## Prechecks and configuration selection

First inspect and reuse any existing working GRPO implementation. Check candidate rewards against historical scoring, sampling success/duplication/within-example mixed rewards, and valid-output masks; then test short updates and checkpoint saving/recovery. Select configurations based on correct implementation, finite losses/gradients, reasonable KL, and discriminative sampling rewards, not whether NAME leads. Main runs restart from original weights and paired initialization. Retain all prechecks and failure records. OOM may be handled by reducing microbatch size while preserving effective batch. Substantive changes to the main protocol require a separate version; do not pool different protocols into one result group.

## Checkpoints and evaluation

Save step0, 10, 20, …, 100. Evaluate every checkpoint greedily on 256 fixed validation examples. Evaluate the 512 fresh test examples only at step0 and step100, without selecting the best endpoint. step0 is the same original policy: one inference pass per condition may be referenced by three seeds, with reuse explicitly marked rather than counted as independent replication. Each run still saves its LoRA initialization checkpoint and hash. Validation thresholds are 60/70/80/90%, reported at the first scheduled checkpoint that reaches them. Unreached thresholds remain Not reached; no exact crossing update between evaluation points is claimed.

Report per-seed gains over step0, paired NAME−STEP differences, means and sample SDs, complete validation curves, and updates/compute costs to reach each threshold. Three seeds provide preliminary replication, not strong evidence of stability. Record generated tokens, actual candidates, sampling/update/evaluation time, and allocated GPU time. Equal update budgets are not equal compute. Separately record headings, operation expansion, numerical errors, early stopping, extra outputs, EOS, and truncation.

## Execution and completion

Use only the eight GPUs on local host .69 initially, with training and evaluation in parallel where possible. Check routine long jobs hourly and handle completion/exception events promptly. Do not stop for one KL change or a few all-0/all-1 batches; diagnose persistent anomalies, preserve their state, and continue. Normal completion requires all 6 runs of 100 updates, all fixed evaluations, and analysis reports, regardless of whether results are positive. Negative results must distinguish failures, unstable optimization, uninformative rewards, and no observed label benefit.

Internal or fine-grained rewards, prompt-optimization research, transfer to practical mathematics or other tasks, and extensions across models/lengths are follow-up work. Do not start them automatically or publish externally.

## Resource reauthorization (2026-09-28)

The user reassigned 172.169.20.70:31904 and 172.169.20.65:32350 for this study, each with 4 PRO6000 GPUs. This supersedes the earlier withdrawn/local-only resource restriction. The 8 local GPUs and both remote machines may be used for these 6 main runs and scheduled evaluations. Connection credentials are stored only in restricted project .config/private-servers files, not in logs or reports. Parallelize useful training/evaluation work where possible, without adding seeds or changing experimental budgets just to occupy GPUs. Check normal training hourly and handle exceptions/completion promptly.
