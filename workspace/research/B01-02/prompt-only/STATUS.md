# Current status: complete

2026-09-28. Full report: REPORT.md. Itemized acceptance: COMPLETION_AUDIT.md.

The registered short-task floor triggered the 14B fallback after 7B. Seven-length exploration is retained for both models. Only 14B L2 qualifies for formal evaluation: 512 examples × four groups = 2048 outputs; the full procedure contains 3040 outputs. All 60 dispatch jobs ended successfully. The eight local GPUs are idle with no restart queue.

Formal results: STEP 45.90%, POSITION 47.85%, ALIAS 57.42%, NAME 45.12%. The primary NAME−STEP difference is −0.78 points, 95% interval [−4.88,+3.32], with no evidence of improvement from repeating original names. The auxiliary ALIAS gain of +11.52 points [+6.84,+16.41] changes names in both input and output and cannot be attributed solely to header repetition.

Auxiliary first-error categories were transparently corrected; original labels and scores remain. Read top-level REPORT.md and analysis/formal-errors-reviewed.json. Initial operation-count labels in fallback14/REPORT.generated.md do not reliably identify actual call insertion/deletion.

Total allocation is 1.046 GPU-hours, including 0.198 for formal evaluation. Normal runs completed before hourly inspection was due. No extra repeated seeds or real tasks outside scope were launched. Earlier fine-tuning experiments are unchanged. Independent cross-model confirmation and real-task transfer remain for a later stage; results were not externally published.
