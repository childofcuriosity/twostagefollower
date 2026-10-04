# Delivery verification

- All 439 registered trajectories are complete, covering every run queue, with no uncounted partial run directories.
- All 439 archived final workspaces have been regraded, matching original scores. Successes and all 73 failures are retained.
- Action replays match final file states and tool-error states. In the early unfixed interface, full tool-return text in 10 trajectories differs in time/host paths. These early cross-run differences cannot be interpreted as a single-method effect; see native-audit.json.
- All 21 trajectories under the new controlled interface also pass full tool-return text equality checks.
- Model outputs and tool returns match before intervention in nine repair pairs. A new-process repeat of the original 5/24 failure matches trajectory, results, and files item by item.
- Original prompts, tool calls, results, final files, receipts, context-management records, and all development failures are saved.
- Total model-process occupancy is 29.64 GPU-hours. All model workers have exited; local GPU memory at delivery is recorded in final-delivery-check.json.
- Model weights were unchanged, with no paid external inference calls or external publication. Work environments, cache references, and artifacts remain in the current project directory.

These checks establish record completeness and agreement of scoring/replays, not general conclusions across models or real tasks from a 3-task mechanism study. Gains from the original summary/deletion methods do not establish a unique identity-restatement effect. The deliverable is a reproducible engineering repair and mechanism evidence; research novelty still requires further checking.

Review entry: [CONCLUSIONS.md](CONCLUSIONS.md); full report: [REPORT.md](REPORT.md); structured results: [analysis/results.json](analysis/results.json); mechanism checks: [analysis/mechanism-audit.json](analysis/mechanism-audit.json).
