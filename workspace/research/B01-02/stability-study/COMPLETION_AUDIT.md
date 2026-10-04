# Completion verification

Main matrix 109824 trajectories (102624 new,7200 reused), operation-context intervention 16896, and new-program confirmation 9600, totaling 136320 formal records, not independent examples. The two current calibration rounds retain 320 raw trajectories; the first archived calibration retains another 80, excluded from formal samples.

- Main matrix: analysis/completion-audit.json, analysis/formal-source-freeze.json, analysis/adapter-hashes.json.
- Operation context: context-intervention/analysis/completion-audit.json reconstructs actual generation inputs record by record. In full-history mode, the new and old evaluators match on 40 examples per scale.
- New-program confirmation: fresh-confirmation/analysis/completion-audit.json covers 9600 trajectories and 99481 generation events, with no_oracle_inputs and actual_generation_contexts_reconstructed explicitly true.
- Final analysis assembly: analysis/final-analysis-complete.json. Final figures, statistical definitions, fixed-sample success/failure cases, and relaxed-scoring sensitivity reviewed;144 subtask cells and 16 post hoc function-scope diagnostic groups completed.
- All failed calibrations and hardware differences retained.3B is consistently reevaluated locally to avoid mixing5090/PRO6000 numerical differences into method comparisons. Original provenance and token hashes are traceable.
- Resources: RESOURCE_ACCOUNTING.md records 78 completed evaluation/calibration jobs and 31.62 allocated GPU-hours, including loading and other wall time. No new training occurred. All three-stage scheduling/analysis processes exited; all 8 GPUs were checked with no memory occupied. Returned remote machines were not reused.

This completes the authorized stability study and registered follow-ups, not unverified broader real-agent/RSI goals. See CONCLUSIONS.md for final interpretation.
