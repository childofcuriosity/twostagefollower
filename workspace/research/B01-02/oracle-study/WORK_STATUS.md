# Current task status

2026-09-25: the user-specified second-stage oracle ablation is complete and has passed acceptance checks.

- 4 scales x 3 conditions x 3 seeds =36 training jobs, each 512 steps;60 checkpoint/inference-mode combinations and 62400 main evaluations.
- Independent scoring and token-context replay passed for all 62400 outputs;480 new-process model reruns across four scales matched complete records.
- Deliverables include every scale/length/seed comparison, both subtask accuracies and their products, paired same-example success, error attribution, counterexamples, costs, reproduction environment, and figures.
- All six 5090 servers were returned and all 8 local GPUs cleared. Every training/evaluation/watch process from this study has ended. Raw data and environments remain here.
- See CONCLUSIONS.md for findings and recommendations and COMPLETION_AUDIT.md for full acceptance checks. No second-stage work remains; awaiting user review of these results. Do not automatically restart the older ticket study.

The Goal tool still stores an earlier paused broad agent-research objective and cannot resume/rewrite that objective. That different goal was not falsely marked complete. The explicit new scope and actual completion evidence for this study are in SECOND_STAGE_GOAL.json. The old tool state must not be read as evidence that this study was not run or only registered resources.
