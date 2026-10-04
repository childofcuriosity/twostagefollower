# First real-agent development validation: acceptance audit

This verifies completion of the authorized goal, not effectiveness of the method. The scientific conclusion is that identity restatement has no supported advantage, and the current execution setup does not yet meet the prerequisites for a reliable long-task mechanism test.

| Requirement | Evidence | Assessment |
|---|---|---|
| Environment, model, tasks, and logs in the current directory | Project-local training-env, existing 32B-Instruct, and two agent-study directories; sandbox runtime also local | Met |
| Three task families, 24 tasks, 4/12 requirements, 4 instances of each per family | task-manifest and 30 main/single-requirement calibration task.json files; all 24 v2 main tasks retained | Met; code tasks are collections of modular functions, with scope limits stated |
| Reference solutions and independent grader | task-validation-v2 covers 30 tasks: unsolved initial states fail, reference solutions pass, and all 198 single-requirement deletions are detected; original v1 validation retained | Met |
| Isolation and executable tools | sandbox-check verifies normal Python/files and rejects out-of-bounds access, network, subprocesses, and writes to the runtime | Met; initial permission/hard-link failures retained |
| Frozen model, shared tools/budgets/loop | Main 96 uses the registered agent.py, sandbox.py, tasks.py with core hashes checked; greedy BF16, no optimizer or adapter training | Met |
| Basic capability and throughput | v1 single-requirement 4/6 result and failures retained; uniformly clarified inputs/outputs yield v2 single-requirement 6/6 on new seeds; per-trajectory time/tokens and peak memory retained | Development calibration met; insufficient to establish multi-requirement capability |
| Four conditions ×24 =96 main trajectories | results and verification cover the full task×condition matrix without duplicates/missing entries; all four workers finish normally | Met |
| Full trajectories and actual stopping reasons | messages/trajectory include raw rounds, tool_result, token counts, final token IDs, and EOS/length-limit; summaries include finish/budget/protocol terminal states | Met |
| Actual completion, false completion, and failure attribution | 44 completions,19 incomplete finishes,26 execution/protocol failures,6 self-reported blocks,1 budget exhaustion; all 52 failures analyzed requirement by requirement | Met; terminal states are not treated as mutually exclusive root mechanisms |
| Reasonable blocking | All 6 blocked claims and fixture inputs checked: no missing user prerequisites, all internal protocol/execution issues | Classification met for this batch; no positive external-blocking control set, so no general calibration claim |
| Post-completion behavior/idling | All 96 action sequences replayed to first completion; all 25 later actions classified, including 1 trajectory degraded after completion | Met; necessary verification is not counted as idling |
| Reproducible independent verification | All 96 archived final-workspaces regraded; replayed actions yield matching final hashes, with no grader side effects or error-state differences | Met |
| Costs and budget | Original main 96 plus two original calibrations: 2.726645 GPU-hours; repaired calibration approximately 0.074026; total 2.800671<8 | Met; process-held time, not pure active GPU-kernel time |
| Execution compatibility problems disclosed | Single-object JSON rejects complete multiple calls;1536 cap truncates responses; working-directory imports restricted;29 offline batch diagnostics excluded from new-agent success rates | Met |
| Post-repair capability threshold and stopping rule | agent-study-v3 registers three shared repairs; new four-requirement calibration scores2/3 and is independently checked; no main runs created after CALIBRATION_FAILED | Completed under the preregistered failure branch; second 96 not run, with no post-repair four-condition claim |
| Raw data, failures, and prompt changes retained | v1/v2 registrations, old calibration, original 96, and separate v3 directory retained; task clarification occurs only before the main experiment and is shared across conditions | Met |
| Figures and conclusions | REPORT, CONCLUSIONS, PNG/SVG/PDF; figures visually checked; tables use all 24 tasks, not selected subsets | Met |
| Decision on later SFT/RL | Deferred until reliable tool calling and multi-requirement short-task capability are accepted, before testing long-horizon stopping | Clear recommendation provided |
| Resources and user preferences | Routine long jobs checked approximately every 15 minutes; returned 5090 not reused; local model jobs finished | Met |

This goal completes first-step development validation, necessary compatibility diagnosis, and a reviewable decision. Independent capability checks with mature tool protocols/stronger models, complex real repositories, SFT, and Agentic RL were not run and are not research results of this study. Remaining budget is not a reason to continue until a positive result appears.
