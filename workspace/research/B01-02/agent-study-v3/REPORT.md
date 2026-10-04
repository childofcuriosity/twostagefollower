# Execution compatibility check: calibration failed; main comparison not started

After the original 96 trajectories were completed, full JSON-sequence parsing, working-directory import compatibility, and the per-turn generation cap (1536→3072) were changed together. The cumulative budget was unchanged and no model was trained. These three combined changes do not identify separate causal effects.

In the new four-requirement calibration, files and code passed but data failed: 2/3, below the preregistered 3/3 threshold. The first data trajectory contained an invalid JSON escape. Corrected code then failed to create the reports directory, raised FileNotFoundError, and still issued finish in the same batch. Independent verification confirmed that all four outputs were absent.

The second batch of 96 was therefore not started. This calibration batch cannot be pooled with the original four-condition results, and there is no post-repair four-condition comparison to report.

All trajectories, final-workspace copies, and raw errors are retained; `analysis/calibration-verification.json` records independent verification. Together with the original 96 and two single-requirement calibration batches, the total is approximately 2.801 GPU-hours. See the [first-stage conclusions](../agent-study/CONCLUSIONS.md) for the overall interpretation and recommendations.
