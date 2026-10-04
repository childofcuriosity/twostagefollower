# Second-stage completion audit

2026-09-25. Authorized oracle training and ablations are complete. Acceptance covers four scales, three training conditions, three seeds, matched oracle-inference controls, and full analysis. It neither completes the broader real-agent/RSI research program nor proves a required mechanism.

|Check|Evidence|Result|
|---|---|---|
|36 main training jobs|All 512 steps and 16384 examples; four intermediate and final adapters present; finite losses/gradients; supervised-token counts match registered masks item by item|Pass|
|60 checkpoint/mode combinations|Each has 560 original tests +480 independent confirmation examples, with aligned IDs, inputs, and tool chains;62400 total|Pass|
|Independent scoring|Separately implemented primitive operations/state transitions and source checks recompute all 62400 outputs, matching original scores; original-file SHA256 saved|Pass|
|Program/model token handoffs|Every main event decoded token by token and context reconstructed; prefix lengths/hashes match and program segments re-encode identically|Pass|
|Training masks and references|Source/loss-mask checks on 4096 training examples per scale;1040 test references; two specialist masks partition joint supervision|Pass|
|Handoff error injection|10 checks including uncorrected wrong names, wrong-number propagation, missing-boundary failures, and batched asynchronous endings|Pass|
|Correct answers fit budgets|Segmented/whole encodings match on 5136 references per scale; maximum header/body/output/context lengths2/33/282/412 tokens|Pass|
|New-process model reruns|Seed11 joint checkpoint at each scale,40 inputs x3 modes; all 480 complete records match|Pass, limited to original fixed batches|
|No input/model-config drift|Data/model-config/tokenizer/download-manifest hashes and weight sizes checked; inference/protocol source hashes match all main runs|Pass; base-weight hashes not fully recomputed|
|Paired statistics and reports|104 matched-environment comparison cells,20 model/length product cells, full failure categories, seed differences, bootstraps, fixed-random bad cases|Complete|
|Resource release|Six 5090 servers previously verified released; all 8 local GPUs at 0 MiB; no study training/evaluation/rerun/watch processes|Complete|

Machine-readable acceptance: analysis/completion-audit.json. Original-score checks: analysis/results-audit.json. Token replay: analysis/token-replay.json. Final command records: analysis/final-audit-steps.json and logs/final-audit.log. Reproduction: [METHOD_AND_REPRODUCTION.md](METHOD_AND_REPRODUCTION.md).

## Exceptions, repairs, and interpretation limits

- All 36 main jobs exited normally, with no failed seed dropped or replaced by retries. The final 32B job moved from its queue to an external idle GPU for training, with the original queue taking over evaluation only. The main training-function AST is unchanged. See analysis/external-adoption-complete.json, handoff-source-check.json, and adoption-preflight.json for leases/checks.
- After all training/evaluation finished, the sleeping watcher that only polled every 15 minutes was stopped and the current process ran the complete final audit immediately. No training/evaluation was stopped. Recorded in analysis/supervisor-manual-handoff.json.
- Final plotting initially failed because the training environment lacked matplotlib. The existing project analysis environment then rendered PNG/SVG/PDF without changing training. That environment lacked pip, so package versions were read through importlib.metadata. See infrastructure/plotting-environment.json; figures were visually checked. These delivery-support errors changed no experimental inputs, raw outputs, or scores.
- Among 24,960 same-checkpoint oracle-intervention pairs,19 show model-output differences before intervention under identical token prefixes, concentrated in smaller models. They are not claimed as clean token interventions. All appear under exceptions in analysis/intervention-pairs.json. Fixed-batch reproduction does not establish cross-batch invariance. Sensitivity analysis excluding exceptions leaves primary denominators unchanged; see CONCLUSIONS.md.
- Specialist and joint training differ in supervised-token counts, ending-token supervision, and gradient weights. Results measure target-mask interventions, not a uniquely identified internal independent-learning mechanism. Mean gains vary by seed and reverse across some models; all are retained.

All 62,400 original results and 480 rerun records are retained. Total cost is approximately 22.76 single-GPU process-hours, including imports/loading/saving and calibration/reruns across two GPU types. Rerun time is estimated from completion-file timestamps, not pure active GPU-kernel time. See analysis/cost-total.json. CPU queue time waiting for external training is not double-counted as GPU training.

See [CONCLUSIONS.md](CONCLUSIONS.md) for final interpretation. No required second-stage implementation, runs, controls, audits, interpretation, or delivery work remains. New mechanism experiments and real-agent transfer are future research and are not falsely claimed complete.
