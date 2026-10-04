# Execution compatibility check

The original 96 trajectories remain intact in ../agent-study and have been audited/replayed. This is a development-stage check after discovering protocol interference, not a replacement for the original results. The four prompt conditions are unchanged. All now support full JSON multi-call sequences, imports from the agent working directory, and a per-turn cap of 3072. Cumulative budgets remain 8192/16384, tool rounds 32/64, and context 24576; there is no training. Three repairs change together, so their causal effects cannot be separated.

registration.json and preflight.json are locked; task-manifest contains the same 24 tasks as original v2. src/sandbox.py and tasks.py allow the agent to import /work while the grader does not add work to sys.path. The tasks symlink points to the original fixture directory. New cal-v3-files/data/code tasks each have 4 requirements and seed9029; old task contents are unchanged.

Launcher session90663 writes logs/launch.log. First run three calibrations on GPU0; continue to 96 only after 3/3 pass. Earlier work used 2.72665 GPU-hours. This batch caps calibration at 900 seconds and each of four main workers at 3600 seconds, leaving watchdog margin within 8 GPU-hours. Analysis scripts provide descriptive summaries only. Batch-trajectory audit/replay still needs to verify messages, tokens, every final-workspace, and actual termination; the original single-action verifier cannot be used directly. Routine checks are every 15 minutes.

## Finished under the capability-failure branch

The new four-requirement files/code calibrations passed, but data failed to create the reports directory, encountered a code error, and still issued finish in the same batch. The 2/3 result missed the 3/3 threshold, so main 96 was not started. All three archives were independently checked; token/hash checks are in analysis/calibration-verification.json. This used approximately 0.074026 GPU-hours, bringing the project total to 2.800671 GPU-hours. No GPU jobs are running. The overall deliverable is ../agent-study/CONCLUSIONS.md. Do not restart the main queue.
