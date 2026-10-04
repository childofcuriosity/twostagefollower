# Completion audit

All 24 added training/evaluation jobs exited with code 0: four scales x two new conditions x three seeds, each with 512 update steps and 16384 example exposures. Earlier flat/macro conditions were not retrained.

- Main and earlier independent evaluations contain 49920 records (24960 new, 24960 reused). Supplementary development and with-definition evaluations add 32256, totaling 82176 scored records, not independent examples.
- All 48 earlier raw-output files match historical hashes, and original scores on 24960 reused records are reproduced. After removing headings, operations and Answers in new data are unchanged example by example. Position prompts are unchanged; aliases apply only the consistent renaming map.
- Original trainer-source hashes, mechanical driver transformations, model revisions/environments/optimization parameters, per-run configs, and 512 finite loss/gradient records per run pass verification. All twelve new 7B/32B initial adapters match Original NAME adapters for the same seed file by file. All 1344 position step0 outputs at 32B match the earlier baseline.
- Generation code, preregistration, and scorer launch hashes remain unchanged. Correct reference lengths fit the original budgets, and all failures remain in denominators. No correct names or intermediate states are supplied by hand.
- A fixed random sample of 97 positive/negative paired cases was reviewed, including missed 32B calls, correct positions with wrong tools, and positive/negative 7B cases. Figures were visually checked.
- Routine monitoring was hourly, with completion events handled in sequence. New jobs totaled 21.98 allocated GPU-hours, including loading, training, and inference. The final nvidia-smi compute-process list was empty, with no new remote jobs.

Postprocessing failures are retained: after all training and core analysis succeeded, the initial scheduler analysis pipeline exited with code 1 because a plotting comparison key omitted condition. After fixing that index, plots.py, boundary_diagnostics.py, and auxiliary.py ran successfully on their own, without retraining or changing model outputs or the scorer. The boundary table also uses consistent decimal rounding (369/1440=25.625%, displayed as 25.63%). The original failure marker is archived at analysis/failures/initial-plot.json; recovery completion is recorded in analysis/pipeline-complete.json.

Core machine-audit results are in analysis/completion-audit.json; supplementary coverage is in analysis/auxiliary-audit.json; per-job records are in analysis/dispatch.json. GOAL.json records completion of this bounded study. The separate older paused agent goal in the system slot was not incorrectly marked complete.
