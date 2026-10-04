# What this study checks

This study asks when long-task performance emerges, deteriorates, and diverges across training seeds, and whether connecting separately trained sequence and operation models improves complete execution over a jointly trained model. See WORK_STATUS.md for progress. This document specifies the fixed method and does not establish completion.

## Comparisons

Joint training supervises both tool names and within-tool operations. Sequence-only training supervises names and the end of the complete sequence. Operation-only training supervises primitive operations, numeric results, and tool termination. All three use existing LoRA adapters; this stage begins without retraining.

The input supplies the correct tool list. The model repeats and executes that list in order rather than planning from a goal. Training examples contain one or two tools; long tests contain 3, 4, 5, 6, or 8. Execution continues from actual model outputs after an error; completely invalid formatting counts as failure.

## Training progression

For both 3B and 32B, evaluate three seeds at steps 64, 128, 256, and 512 and report every point. Test the joint model in three modes: autonomous execution, operation generation with program-supplied correct names, and name generation with program-executed correct operations. Test each specialist on its trained component. Short development examples track mastery; long examples track generalization. Do not choose checkpoints using test performance.

## Actual composed execution

One base model loads multiple LoRA adapters. The sequence adapter generates names; the operation adapter generates operations. Both stages see the same actual generation history. The program switches adapters and recognizes termination boundaries.

For a requested `red → black` sequence, the sequence model first writes a name, the operation model continues from that actual history, and the sequence model then writes another name or terminates. Incorrect names and numbers remain unchanged. Premature termination does not trigger forced continuation. The composition procedure does not consult reference solutions to choose subsequent content.

Compare four routes: the joint model handles both stages; a specialist replaces only name generation; a specialist replaces only operation generation; and specialists handle both stages. The single-component replacements help locate the source of differences beyond the aggregate composition score.

Two specialists trained for 512 steps use more total training than one joint model trained for 512 steps. A prespecified comparison therefore pairs two 256-step specialists against the 512-step joint model, approximately matching cumulative examples and optimization steps. Two LoRA adapters still require more parameter storage, so this does not match every cost. Only one adapter is active per generated token.

## Hardware and implementation checks

Use only the training environment in this directory and the local PRO6000 hardware. The original 3B runs used a 5090. Initial cross-hardware replay of 40 fixed 3B examples produced three text differences and one change in whole-task correctness, so all final 3B baselines are rerun locally. The original 32B hardware was the same local model; all 40 old replay records matched.

Before formal evaluation, call a single adapter directly on the current hardware, then load the other two adapters and route every call to the original adapter. All 40 complete records match at each scale, confirming unchanged behavior on this fixed calibration set. Mock checks also verify that wrong names remain uncorrected, wrong numbers enter subsequent history, premature termination fails, and missing tool-end markers fail. Retain the initial import failure and hardware differences rather than deleting failed calibrations.

## Interpretation

The primary measure is strict complete-task success from actual execution, not the product of two subtask accuracies. Report each seed, the mean, the worst-seed change, results by length, error positions, and generation costs. Improvement across three seeds is an observed positive consistency signal, not proof over all training randomness.

Show any early peaks and later declines in checkpoint curves, but do not choose a test-optimal checkpoint as the final method. The fixed effect comparisons are the prespecified 512-step comparison and the two 256-step specialists versus the 512-step joint model. Any subsequent training or early-stopping changes require a defined rule before validation.

Source code, fixed inputs, and parameter paths are in src/, data/, and analysis/job-configs/. Complete SHA256 hashes for all 72 adapters are in analysis/adapter-hashes.json; the formal generation source freeze is in analysis/formal-source-freeze.json. Original training configurations, logs, and checkpoints remain in oracle-study without duplication or overwriting. All mixed-model outputs retain actual tokens and prefix hashes, with program/model provenance recorded in the original format. Every token in composed outputs must be model-generated.
