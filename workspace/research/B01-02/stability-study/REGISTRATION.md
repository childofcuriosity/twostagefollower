# Stability and actual composition: preregistration

On 2026-09-25, the user authorized a thorough investigation of seed- and length-dependent instability in existing training and whether actual composition of separately trained models improves complete execution. Launching jobs, isolated positive results, or shallow negative diagnoses do not establish completion. Use only the local 8 × RTX PRO6000 96 GB GPUs; do not access the returned servers. Keep environments and artifacts in this directory.

## Fixed materials

Use the existing oracle-study Qwen2.5 Base 3B and 32B adapters: joint, operation_oracle (sequence-only training), and order_oracle (operation-only training), with seeds 11/22/33 and steps 64/128/256/512. Preserve original training configurations and data. Reuse the shared EndTool/Done protocol, generation boundaries, greedy decoding, batch size 8, budgets of 2048 generated tokens, 4096 context tokens, and 16 tools, and strict whole-task scoring. Training has already finished; this stage begins without retraining.

Fix the original 224-example development set (128 short and 96 long examples) and the 480-example independent confirmation set (96 examples at each length 3/4/5/6/8). Development data track training progression. The confirmation set has already been used and is not a new blind test. Report every checkpoint; do not select the best test checkpoint as the main result or derive early-stopping rules from these tests. Also inspect training-loss curves under the same training conditions.

## Training-progression matrix

For each model, seed, and checkpoint, test the joint model in autonomous, program-supplied sequence, and program-supplied operation modes, plus each specialist in its trained mode: five modes total. Two models × three seeds × four checkpoints × five modes × 704 examples = 84480 records. Reuse 7200 existing 32B step-512 confirmation outputs. Rerun 3B step-512 confirmation locally (see the calibration revision below); all step-512 development evaluations are new. This requires 77280 new curve-evaluation trajectories.

## Actual composition without reference answers

Load different LoRA adapters on the same base. Select the sequence adapter for names, including Done, and the operation adapter for tool operations. History consists entirely of actual generated tokens. Do not insert correct names or operations, repair states, or force termination at the target length. Reconstruct each generation context from the complete actual history. Adapter selection depends only on the protocol header/body stage; routing does not read reference chains or correctness scores.

At steps 256 and 512, test:
- Sequence specialist + operation specialist.
- Sequence specialist + joint model (replace only the sequence component).
- Joint model + operation specialist (replace only the operation component).

The common baseline is autonomous execution by the joint model at the same checkpoint. Using its adapter for both stages is algorithmically identical to original autonomous execution. Verify equivalence in a fresh process with fixed batches before reusing outputs; do not create a duplicate group. Two scales × three seeds × two checkpoints × three compositions × 704 examples = 25344 new main-evaluation trajectories. Together with the curves, coverage is 109824 trajectories, including 102624 new inference runs.

Same-seed pairing across the three seeds is the primary analysis. The 3 × 3 cross-seed matrix is not run, so chance pairing effects remain possible. Composition activates one adapter per generated token, rather than calling two LLMs for the same token; record actual model tokens and time. Two 512-step specialists cost approximately twice as much training as one 512-step joint model. Prespecify two 256-step specialists versus one 512-step joint model to approximately match cumulative training examples and optimization steps. Report same-step and exposure-matched comparisons separately.

## Acceptance criteria and interpretation

Before running, verify correct routing, model provenance for all composed tokens, no correction of wrong names, propagation of wrong numbers to the other model, permitted but failing premature Done, and failure on missing end boundaries. For seed 11 at each scale, compare 40 fixed-batch autonomous examples between direct single-adapter calls and multi-adapter routing to that same adapter on current hardware. Report comparisons with old outputs separately; calibration is outside the main matrix. Hash original training materials, inputs, adapter configurations, and source. Preserve failed records.

Independently recompute scores, token decoding, and prefix hashes for every new trajectory and verify coverage. Report whole-task accuracy, sequence accuracy, correctness of all emitted operations, first-error type and position, effective generated tokens, and time by length and seed. Primary conclusions use the fixed 512-step and prespecified exposure-matched comparisons; checkpoint curves are descriptive. A higher mean with substantial harm to one seed is not a stable improvement. A positive consistency signal requires higher aggregate independent long-task accuracy for all three seeds with no observed aggregate seed decline, accompanied by per-length results and program-clustered intervals. Three seeds cannot establish population-wide robustness.

If consistent gains appear, check the matched budget and error propagation and identify the contributing component. If gains disappear or reverse, use the single-component replacements and first token-level divergences to locate causes, preregistering targeted mechanism tests if needed. Do not switch tasks merely to obtain positive results. Completion requires the full matrix, trajectory audits, interpretation, resource release, and a reproducible report. Unrun mechanism fixes do not count as completed work.

## Calibration revision before the formal matrix

The first mock run failed because the module name run collided with upstream src/run.py. Loading by absolute source path fixed the issue; all seven local routing checks passed. Initial real replay matched 40/40 old 32B records and 37/40 old 3B records from the 5090, with one whole-task correctness change. Cross-hardware outputs cannot serve as strict implementation-equivalence references. Revised calibration compares direct single-adapter calls with routing to that same adapter after loading the others, all on current hardware. Rerun every 3B step-512 confirmation output instead of reusing the 5090 outputs. This revision preceded all new formal curve and composition results. Retain old calibration records, failures, and moved paths in calibration-attempts/v1.

Final main-matrix coverage remains 109824 records: 7200 reused old 32B step-512 confirmation outputs and 102624 new trajectories. Same-hardware routing calibration covers 40 examples × two call methods × two scales = 160 records, alongside the initial 80 calibration records. Report old-baseline differences separately; neither classify them as routing failures nor remove difficult examples from the main results.

The two 256-step specialists versus the 512-step joint model match cumulative training examples and optimization steps, not every resource. Two rank-16 adapters store approximately twice the trainable parameters of one rank-16 adapter, with one active per token. No new control matches total adapter capacity, so capacity effects are not excluded. The first short-development score of at least 99% is only a descriptive mastery-time marker, not a test-checkpoint selection rule.
