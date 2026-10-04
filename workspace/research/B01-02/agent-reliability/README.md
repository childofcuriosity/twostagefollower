# Agent execution reliability and completion study

This directory continues the authorized B01-02 research. It uses the local frozen Qwen2.5-32B-Instruct checkpoint, Transformers, the model's native tool chat template, and a filesystem/Python sandbox. It does not update weights and is not an EvoScientist runtime experiment. All task data, environment references, raw trajectories and reports remain under the current project.

Current work and caveats: WORK_STATUS.md. Designs recorded before their respective runs: REGISTRATION.md, QUEUE_REGISTRATION.md, NOTES_REGISTRATION.md, QUEUE_NOTES_REGISTRATION.md. Prior custom-protocol experiments are preserved in ../agent-study and ../agent-study-v3.

From project root, activate `source training-env.sh`. Entry points in `src/`:

- `native.py`: native tool protocol for file/data/code tasks.
- `native_notes.py`: same native envelope with an explicit operational note argument.
- `native_queue.py`: sequentially released local shipment tickets, receipt-only submission.
- `native_queue_notes.py`: explicit notes plus shared efficient-file-reading instructions for sequential tasks.
- `launch_batch.py`: launch the frozen job list in a queues/*-batch.json configuration. Existing run directories are not overwritten; reruns need new tags.
- `audit_native.py`: independently regrade archived workspaces and replay actual tool actions, with no model inference or in-loop grading feedback.
- `analyze_native.py`: aggregate full results, paired comparisons, actual generated/input tokens and process costs.

Example for a new single-task rerun: create a JSON queue containing `[["dev-files-n04-s0", "plan"]]`, then run `CUDA_VISIBLE_DEVICES=0 python workspace/research/B01-02/agent-reliability/src/native.py --jobs <queue-path> --tag <new-tag> --mode zero`. The GPU must be free. Generated artifacts appear under runs/<new-tag>/; do not run the same tag twice.

Each completed run preserves summary.json, messages.json, trajectory.jsonl and final-workspace/. Sequential runs also preserve queue-state.json with exact submitted contents. The hidden grader never feeds success or expected answers back to the agent. Queue receipts report delivery counts, not correctness. The agent may terminate early in every main prompt comparison.

The sandbox runs standard-library Python under a chroot with restricted uid, seccomp, CPU/memory/output-file limits and no network/subprocess creation. Source CSV/README preservation and code behavior on unseen inputs are independently checked. This is a controlled local benchmark; neither realistic deployment breadth nor RSI improvement follows automatically from a higher completion rate.

Final controlled variants: native_queue_compact.py adds public-state handoff; native_queue_controlled.py fixes observed clock/error variability; native_queue_controlled_v2.py also preserves input schema; native_queue_controlled_v3.py adds the full-history role-text filtering ablation. Version1 calibration failure remains archived. fixed_tools.py controls the observed nondeterministic APIs inside child sandboxes only.

Review entry: CONCLUSIONS.md. Full evidence and boundaries: REPORT.md and COMPLETION_AUDIT.md. Primary-source context-management neighbors: LITERATURE.md. Exportable figures: figures/reliability.png, .svg and .pdf.
