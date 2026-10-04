# Stage 1/4: model freezing and environment preparation

Goal active. The user approved the agent early-stopping study and requested priority validation at tens of billions of parameters. Progress updates now begin with the stage, as requested.

Stage 1: download fixed 32B and 7B revisions and verify file SHA hashes.
Stage 2: separate forward/backward and memory calibration per model. Reduce microbatch from 16→8→4→2→1 only for OOM or insufficient memory margin.
Stage 3: flat/macro × seeds 11/22/33, totaling 12 formal training runs with fixed checkpoints. Use GPUs 0–2 for 32B and 4–6 for 7B.
Stage 4: full-test attribution, scale comparison, and research report. File markers do not establish reviewed delivery.

Download logs: root logs/training/scale-download-*.log. Latest launcher logs: scale-launch-*-v2.log. Retain the initial Python TLS failure; curl retrieves metadata instead. All environments and caches stay inside the project. Check long jobs infrequently by stage.

Training inherits original data, optimizer, and label comparisons. Only microbatch splitting and activation checkpointing change, with losses weighted by target-token counts in the original logical batch of 16 to preserve normalization in BF16. Registration: analysis/registration.json. No quantization or test-based best-checkpoint selection.


## Actual run log

Codex writes and executes Python scripts directly rather than driving the EvoScientist chat interface. Results must not be presented as an effect of Evo autonomous research. This was explicitly explained when the user asked.

32B revision: 1818d35814b8319459f4bd55ed1ac8709630f003; 7B revision: d149729398750b98c0af14eb82c78cfe92750796. Curl downloads through the company proxy experienced large-file interruptions and automatically retried/resumed. Monitor logical file size; remote filesystem du allocated blocks do not measure download progress. Write download-manifest.json and trigger calibration only after complete download.

The BF16 gradient check splitting microbatch 16 into four failed the chosen 3% tolerance at 4.35%; records remain. Retaining 16 and enabling only gradient checkpointing matches loss/gradients; analysis/checkpointing-check.json passed. Registration v2 enables evaluation KV cache; v3 prioritizes original microbatch 16. Both changes precede formal training. Smaller-microbatch fallback does not claim bitwise equivalence and requires disclosure of implementation differences.

Waiting queues are running: one launch.py per model waits for download, calibrates, then runs flat followed by macro on each of three GPUs (six jobs/model). One checkpoints.py per model waits for all six jobs, then evaluates checkpoints 0/16/64/128/256; train.py handles final step 512. finish.py waits for both checkpoint queues before full analysis and does not automatically complete the goal.

The test/audit entry point src/analyze.py passed on all 6,720 original 1.5/3B outputs and explicitly lists missing new models. ANALYSIS_COMPLETE marks automatic verification only. Delivery still needs reviewed prose, scale comparisons, intervals, figures, failure explanations, and goal status.

Active terminal sessions, to consult only as needed: downloads 32B=80588, 7B=18257; launchers 32B=63290, 7B=2777; checkpoint waits 32B=87821, 7B=35465; final-analysis wait=91372. Do not restart healthy waiting processes. Old launchers were terminated only while waiting; v2 is current.

Next: inspect download/calibration markers and diagnose actual failures. Retain the primary 32B comparison and 7B scale reference and deliver against the goal. Symmetric lower-learning-rate sensitivity, the 32B-Instruct bridge, and fresh longer-call confirmation are not yet launched/generated and cannot be called complete. Original-recipe scale results do not directly establish a prior-preservation mechanism.


## Latest progress on the scale objective

The 7B download and SHA manifest are complete. Initial calibration failed before loading because an argument after --tag began with a minus sign. Changed to --tag=value and retained logs; registration-v4 records it. Latest launcher logs are scale-launch-qwen7b-v3.log and scale-launch-qwen32b-v3.log, with sessions 60633 and 99713. Old v2 sessions ended without interrupting training.

7B microbatch-16 calibration passed: peak 21,976,851,456 bytes (20.47 GiB), 3.148 seconds for two optimization steps. Three formal flat seeds started, first evaluating step-0 development with/without definitions, then training 512 steps with checkpoint evaluation. Each seed runs macro after flat. qwen7b-token-audit.json confirms training token IDs match old 1.5B and per-example supervised lengths match across flat/macro.

Fresh confirmation is frozen in data/extended-test.jsonl: 480 examples, 120 distinct functions, 24 programs × four inputs at each length 3/4/5/6/8, functionally disjoint from historical train/dev/test. Registration: analysis/extended-data-registration.json. max_new_tokens512 prevents eight-call targets from being truncated at 256. Evaluate all four models. Frozen baselines receive definitions; trained models do not, requiring separate interpretation. extended.py first evaluates original 1.5/3B on GPUs 3/7, then 32B/7B after corresponding primary training. Sessions: lane0=94314, lane1=35533. Logs: runs/extended-*.log. Frozen generations can be long; inspect infrequently rather than restarting for delayed output.

Main analyze.py now uses independent per-example audit.py checks. inference.py produces program-clustered paired bootstrap and three-training-seed t intervals, plus full audits of the new 480 examples; repeated seeds on one example are not independent samples. finalize.py (session 29935) waits for main ANALYSIS_COMPLETE and all four extended evaluations, then reanalyzes and drafts REPORT plus REVIEW_READY. prepare_review.py (session 9825) then verifies 12 runs/84 checkpoint hashes and plots. Logs: scale-finalize.log and scale-prepare-review.log. Markers still require scientific review and CONCLUSIONS; they do not complete the goal automatically.

Open items: 32B weights are still downloading; avoid duplicate downloads/launches. Check actual training exceptions in 32B/7B, confirm final statistics/figures cover the objective, and add the 32B token audit. Symmetric low-LR sensitivity and the Instruct bridge are unrun, so their effects are not excluded. Decide and clearly report limits from evidence after the primary scale comparison.


## Third update: complete 32B download and supplementary-control queues

32B Base download is complete: 26 files, 65.54 GB. SHA256 hashes of all 17 local weight shards match Hub LFS hashes at the fixed revision; see analysis/qwen32b-remote-hash-audit.json. The 32B token audit also matches original 1.5B training IDs exactly. The launcher entered two-step microbatch-16 calibration; results still need inspection.

Three 7B flat jobs completed pretraining development baselines and are updating parameters with intermediate evaluations. Baseline waiting time must not be mistaken for absent training. Independent confirmation for old models is also proceeding normally.

Before final new-model scores were visible, supplementary experiments were registered in analysis/supplement-registration.json to implement dose/instruction controls: Qwen3B Base and 32B Base at lr=1e-4, each flat/macro × three seeds; 32B-Instruct at lr=3e-4, six runs plus a frozen baseline. Each run fixes 512 steps, retains intermediate adapters without repeated online evaluations, and evaluates all original 560 examples with/without definitions at the end. No best-setting selection from final scores. Instruct uses the official chat template consistently and is tabulated separately from Base.

32B-Instruct download started only after 32B Base finished, session 18865, log scale-download-instruct.log. Low-LR lane (session 73137) waits for primary 7B checkpoint evaluation, then runs 3B followed by 32B on GPUs 4–6. Instruct lane (session 2998) waits for primary 32B checkpoint evaluation and download, then calibrates, evaluates frozen baselines, and trains six runs on GPUs 0–2. Primary-study GPUs are not preempted. Extended 32B remains on GPU 3 and extended 7B on GPU 7.

Supplementary analyze_supplement.py (session 77592) waits for both supplementary lanes and primary ARTIFACTS_READY, then audits 18 runs, 126 adapter hashes, and 21,280 raw records (18×2×560 plus frozen 2×560), writing SUPPLEMENT.md and SUPPLEMENT_READY. train_supplement.py is separate; running primary train.py is unchanged. The draft main report still needs a final manual update of its unrun-supplement paragraph.

Goal completion now includes these queued controls from the approved plan. Main ARTIFACTS_READY alone is insufficient: verify SUPPLEMENT_READY, interpret low-LR/Instruct results, and complete costs, conclusions, and figures. No scale-study conclusion is yet available.


## Verified current state: formal training running

32B microbatch-16 calibration passed without fallback: peak 74,882,093,056 bytes (69.74 GiB), 10.8835 seconds for two steps. Three formal flat seeds on GPUs 0–2 are evaluating pretraining baselines. All three 7B seeds are running; seed 11 has passed step 256. All eight GPUs show real load; no healthy job was restarted. verify.py now checks finite loss/lr/grad_norm/elapsed values, continuous 512 steps, and effective batch 32, registered in verification-amendment.json. This strengthens delivery checks without changing training/testing.


## Matched-prompt pre/post-training comparison added to acceptance

New src/matched_context.py runs through verify.py when the waiting prepare_review reaches that stage. It compares frozen step 0 with final step 512 for 7B/32B, matching definitions with definitions and no definitions with no definitions. It reports answers, strict trajectories, two-tool stopping, prefix early stopping, budget hits, and 0→1/1→0 counts, checking id/chain/x/expected/split and frozen-output repeatability. It rechecks 26,880 records, including repeated frozen measurements rather than independent samples, without new inference. Registered in analysis/matched-context-registration.json. Syntax passes; full validation awaits evaluations. This prevents prompt-information differences from being misattributed to training-induced capability changes.


## Audit of stopping evidence

Original generation saves non-EOS counts (PAD=EOS), not token IDs, so direct stop reasons cannot retrospectively be claimed. audit.py adds stop_evidence: non-EOS count >= cap means length_limit_reached; cap-minus-one is boundary-ambiguous; below cap-minus-one implies EOS before cap under the EOS/length-only stopping configuration. The REPORT template states this limit and analyze.py groups counts by model/condition/test split. Reruns pass on all 6,720 old-model records; new 7/32B results remain explicitly missing. Training/generation code is unchanged. Registration: stop-evidence-registration.json.


## Complete local-error metrics

 audit.py adds first emitted-operation divergence, wrong operation, numeric-step error, extra formatting lines, and missing/multiple Answer metrics. These overlap and are not exclusive causal categories; suffix omission alone is not a wrong operation. analyze.py and REPORT include long-composition summaries; all 6,720 old records pass again. Registration: local-error-registration.json. All seven 1.5B confirmation evaluations, 3,360 records, and hashes pass; see qwen1.5b-confirmation-audit.json. Macro strict accuracy at 3/5/8 calls is 52.43/5.90/1.04%, versus zero throughout for flat. This does not yet establish a scale conclusion.


## Instruct download and template checks complete

Qwen2.5-32B-Instruct revision 5ede1c97bbab6ce5cda5812749b4c0bdf79b18dd downloaded successfully; the session exited 0. All 4,096 training examples have matching train/test prompt encodings and flat/macro target lengths. Maximum complete target-containing sequence length is 189 tokens, below the 320-token safeguard; EOS is 151645 im_end. Evidence: analysis/qwen32b-instruct-token-audit.json. This establishes format consistency, not completed training or stronger capability. Supplementary training still awaits primary 32B checkpoints. All 3,360 3B confirmation records/hashes pass in qwen3b-confirmation-audit.json; macro strict accuracy at 3/5/8 calls is 83.68/28.47/2.08%, with flat zero throughout.


## User-provided remote resources: first two hosts running

REDACTED_HOST:31585 has 8 × 5090 32 GB GPUs; shared paths and venv are verified. After calibration, remote_3b.py (PID 12935) runs six 3B low-LR jobs in parallel on GPUs 0–5 with observed load. The local LR waiter PID 1537599 ended while childless. New waiter session 35730 (PID 1721395) will adopt remote 3B completion and then run 32B low-LR locally on GPUs 4–6, avoiding duplicate 3B jobs. Launcher remote-claim adoption is new; training source is unchanged.

REDACTED_HOST:30929 has 4 × PRO6000 Blackwell 96 GB GPUs; shared paths and CUDA pass checks. The original local Instruct waiter PID 1537647 ended while childless. Remote launcher PID 11796 --lane instruct --remote-ready passed calibration, is running the frozen baseline, then will pair three-seed training on GPUs 0–2. Independent resources remove the primary-study wait. Formal train_supplement.py retains its registered hash. Logs: scale-remote-qwen3b.log and scale-remote-instruct.log. SSH reuse sockets are project-local; passwords are not saved.



## Updated remote allocation: supplementary training and primary checkpoint evaluation

All six 3B low-LR jobs on the first 5090 server succeeded; training and 6,720 outputs pass remote-qwen3b-completion-audit.json. No further tasks are assigned there. New server 172.169.20.70:31432 has 4 × PRO6000 Blackwell 96 GB GPUs with verified shared paths and matching torch/CUDA. Local LR waiter PID 1721395 ended while childless. Remote LR PID 444706 adopts completed 3B results and runs 32B low-LR on GPUs 0–2 without waiting for 7B checkpoints. train_supplement.py remains unchanged.

GPU 3 on both PRO6000 servers evaluates saved 32B flat checkpoints whose development outputs are already written: .65 PID 31809 handles seeds 11 then 33; .70 PID 449696 handles seed 22. The original checkpoints.py condition branch writes original paths with unchanged parameters/sampling. Original parent waiter PID 1499385 ended while childless. New session 79658 waits for primary training, adopts remote flat results, and evaluates macro locally on GPUs 0–2. Only parent scheduling gains a remote-adoption branch; condition evaluation is unchanged, registered in remote-checkpoints-claim.json. Primary training was not interrupted.

Remote logs: scale-remote-lr.log, scale-remote-instruct.log, scale-remote-checkpoints-11-33.log, and scale-remote-checkpoints-22.log. Do not restart old local LR/Instruct waiters or duplicate flat checkpoint evaluations. Routine checks remain approximately every 15 minutes; startup checks after new-resource setup can be prompt.


## 7B checkpoints complete; idle GPUs evaluate 32B macro early

All six 7B fixed-checkpoint groups succeeded. Three formal 32B flat jobs exited successfully; three macro seeds run on GPUs 0–2. After verifying empty memory on GPUs 4–6, early_macro_checkpoints.py (session 29564) evaluates macro checkpoints 0/16/64/128/256 in parallel there. Each checkpoint waits for its development output to ensure fully saved weights; generation is unchanged. All step-0 weights currently exist.

The childless 32B checkpoint parent waiter PID 1782127 was replaced; new log: scale-checkpoints-qwen32b-v3.log. After training, the new parent adopts remote flat and local early-macro results without duplicate evaluation. Registration: early-macro-checkpoints-claim.json. Early-macro wall time may include waiting for weights; final accounting must distinguish reserved GPU time from actual evaluation, rather than treating it as pure kernel compute.


## 5090 server returned to the user

The user requested use of the idle 5090 server or its return if unsuitable. A short four-GPU 32B BF16 probe on 172.169.20.32:31585 used batch 4 and original greedy settings on eight old development examples, with no long experiment launched. It took 36.30 seconds at 56.06 non-EOS tokens/s, peaking around 14–17 GiB per GPU without CPU/disk offload. Only 3/8 raw outputs exactly matched the original single-PRO6000 baseline, failing the agreement gate. Retain analysis/sharded32-probe.json and scale-sharded32-probe.log. Do not attribute differences uniquely to sharding or hardware without validation or mix them into primary results. After confirming 0 MiB and no compute processes on all eight cards, return the server and set remote-resources.json to returned_to_user_do_not_schedule. No further use without new authorization. Existing 3B low-LR results remain, with their 5090 hardware difference disclosed.


## Parallel local evaluation of 32B independent confirmation

The waiting extended32 child PID 1563753 and lane0 parent PID 1512033 ended before model loading or output-directory creation, interrupting no actual evaluation. New extended32_parallel.py (session 1954) still waits for all six primary jobs, then schedules the original seven confirmation evaluations across local GPUs 0/1/2/3/7. Each extended32_worker.py uses an evaluate function copied unchanged from extended.py. Each model occupies one PRO6000; batch 4, max 512, BF16, greedy decoding, and 480 examples are unchanged. Each evaluation loads the same base and assigned adapter independently, retaining output paths, seven metadata files, and completed.json format. Registration: parallel-extended32-registration.json; log: scale-extended32-parallel.log. The old lane0 marker is replaced by parallel-extended32-completed.json as dispatch evidence; the finalizer still uses extended/qwen32b/completed.json.

## Analysis closeout update

All final primary, independent-confirmation, and learning-rate/Instruct outputs are saved; SUPPLEMENT_READY exists. The 32B flat seed-33 checkpoint evaluator remains active on remote .65, PID 134272, using 64986 MiB. All other primary checkpoints are complete. Do not restart this job or access the returned 5090 server.

New outcome_diagnostics.py successfully audits 48,160 main/independent/supplementary raw outputs, classifying prescribed correct trajectories, globally equivalent functions, chance-correct current inputs, and answers lacking valid supporting trajectories. It also checks LoRA parameter counts for 24 primary runs. New mastery_diagnostics.py reads all 72 fixed development checkpoints. Because registration omitted numeric mastery thresholds, 90/95/99% analyses are explicitly post hoc sensitivity checks. Link selected test results after final evaluation finishes.

CONCLUSIONS.md contains measured findings and limits but remains a stage report. plots.py adds the primary correct-prefix early-stopping endpoint and fixed curves for IID mastery and OOD answer/trajectory/stopping metrics. Original prepare_review will generate plots after final data; rendering acceptance is pending. Remaining work: final checkpoints, verify coverage, generate/inspect figures, revise stale unrun-supplement text in report.py, and close protocol/resource audits. The goal remains active.


Final acceptance is strengthened: verify.py must check exact IDs, inputs, splits, and interpreter results in all 174 planned files/95,200 outputs, including 84 extra checkpoint/definition files, rather than counts alone. report.py now includes supplementary training and accounting. mastery_diagnostics.py links development-selected test results, with every 90/95/99% threshold labeled post hoc exploration. Registration: final-audit-amendment.json. Checks approximately 15 minutes apart confirm remote .65 PID 134272 remains active; seed 33 finished step 16 and is evaluating step 64. Final testing remains incomplete; no duplicate work started.


## Stage one fully complete

All planned jobs exited successfully, including the final 32B flat seed-33 checkpoints. Verification passes for 174 files/95,200 raw outputs and 84 primary adapters; 18 supplementary runs and 126 adapters also pass. All mastery sensitivity comparisons for 72 development checkpoints are available. Three figure groups were visually checked. Reports, explicit protocol deviations, and itemized acceptance are in CONCLUSIONS.md and COMPLETION_AUDIT.md; delivery manifest: analysis/DELIVERY_COMPLETE.json. No research compute processes remain locally or on the two PRO6000 servers. Await consolidated user review; do not launch real-agent stage two without authorization. This status supersedes preceding in-progress entries.
