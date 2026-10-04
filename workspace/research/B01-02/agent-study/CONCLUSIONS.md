# Real-agent first step: complete, without evidence of an identity-restatement benefit

This development smoke test is complete and audited: 24 tasks × 4 conditions, totaling 96 main trajectories. Every final workspace was rescored, and file states after replaying every tool action matched the original archives. Also retained are 12 single-requirement calibrations and 3 four-requirement calibrations after execution-compatibility repairs. The total is 111 model trajectories and approximately 2.801 GPU-hours, within the 8-hour budget. No SFT or RL training was performed.

**Decision: identity restatement should not yet enter SFT or Agentic RL as an already effective method.** These results show no advantage over controls, while tool-protocol and basic execution errors are common. The next step is a reliable native-tool baseline that passes multi-requirement short-task checks before testing genuinely long-horizon early stopping. This completes development validation and diagnosis, not a confirmatory study or validation of a production-agent method.

## What we ran

Frozen Qwen2.5-32B-Instruct, revision `5ede1c97bbab6ce5cda5812749b4c0bdf79b18dd`, BF16, one GPU, greedy decoding. Execution uses a project-built JSON tool loop with tool returns as user-role messages, rather than EvoScientist, the Codex product, or a mature agent SDK.

Three local task families: editing configurations across files, joining/filtering CSV data and producing reports, and implementing Python functions across modules. Each family has 8 tasks: 4 with 4 requirements and 4 with 12. Code tasks are small module collections, not large real repositories or complex dependency workflows. Short/long tasks with the same seed share some content, and there are only 3 generator families; the 24 examples are not 24 independent task templates. Batch operations are allowed, without forcing a tool-call count.

All four conditions share original requirements, tools, inputs, and budgets, differing only in status instructions: initial checklist, generic continue/check reminders, current task ID and name, or maintained to-do status. Task identity refers to user requirements, not merely tool names such as `write_file`. The model writes its own status; hidden acceptance checks never feed back to the running model. It can finish autonomously without a ground-truth completion gate.

Short/long cumulative generation budgets are 8,192/16,384 tokens, with 32/64 rounds and context cap 24,576. The original per-turn generation cap is 1,536. All generation costs are counted; each round retains input/output tokens, final token ID, and EOS/length-cap evidence. Workspaces and standard-library Python are isolated within the project, with network, subprocess, and out-of-bounds access empirically blocked.

## Four-condition results

| Condition | Actual completion | Declared completion while incomplete | Mean generated tokens | Mean total input tokens |
|---|---:|---:|---:|---:|
| Initial checklist | 9/24 (37.5%) | 3/24 | 1,582 | 6,093 |
| Generic reminder | 16/24 (66.7%) | 4/24 | 1,855 | 13,037 |
| Current task identity | 9/24 (37.5%) | 7/24 | 1,278 | 7,839 |
| To-do status | 10/24 (41.7%) | 5/24 | 1,079 | 4,666 |

Against the initial checklist, identity alone completes 5 tasks and checklist alone completes 5, a net difference of 0. Against generic reminders, identity alone completes 4 and reminders alone complete 11. Fewer output tokens alone do not establish better efficiency when completion differs. No confirmatory significance claim is made, and results are not selected by the most favorable family or length.

![Complete results and costs](figures/agent-smoke.png)

## Why low completion cannot simply be called long-horizon early stopping

Final categories for the 96 trajectories are 44 actual completions,19 incomplete voluntary finishes,26 execution/protocol failures,6 self-reported blocks, and 1 budget exhaustion. These describe terminal states, not mutually exclusive underlying causes.

Parsing or tool exceptions occurred in 59 trajectories;6 hit the per-generation cap. Every requirement in all 52 failures was attributed to unchanged files, missing outputs, or generated but incorrect outputs; detailed paths are in `analysis/failure-diagnostics.json`. Multi-requirement short tasks are themselves unreliable, so the model cannot be described as consistently capable except when tasks become long.

Examples:

- `code-n04-s0-v2 / identity`: the model emitted four file writes and finish together, and the single-object JSON protocol rejected the batch. After receiving the error, the model declared completion; all four TODO files were unchanged. This combines a protocol issue with incorrect self-assessment.
- `data-n12-s2-v2 / reminder`: all 12 report files existed, but regions were paired with wrong quantity thresholds and only 2/12 requirements passed. Missing files and incorrect contents must be separated.
- `files-n04-s2-v2 / identity`: the task was initially complete. A later whole-object comparison used an object containing only changed fields, incorrectly treated preserved extra fields as errors, and deleted required preserved fields. This is degradation after completion, not insufficient persistence.
- All 6 blocked claims concerned JSON organization, imports, or internal implementation. Required inputs were complete, with no missing external prerequisite requiring user input. Isolated Python not importing the working directory by default also contributed technical friction. These cases cannot all be called reasonable waits for a user.

Action-by-action replay found 16 trajectories with actions after first passing acceptance, totaling 25 actions: 8 file listings,11 checks,5 repeated writes/computations, and 1 destructive rewrite. Checks are not all idle looping; destructive rewriting is separate. This small sample also does not establish absence of infinite-loop risk.

Actual adherence to status instructions is retained in `analysis/status-audit.jsonl`. Invalid JSON rounds cannot automatically count as executed identity cues. All trajectories are reported by assigned condition, without filtering nonadherent samples to raise scores.

## Calibration, repairs, and the stopping branch

The first single-requirement calibration passed 4/6. Both CSV failures guessed paths/fields incorrectly and violated the required output structure. All failures are retained. After uniformly clarifying paths, headers, and aggregate JSON structure, new single-task seeds2/3 passed 6/6, and only then did the main 96 run. Correct answers and acceptance standards were unchanged.

Offline diagnosis of the main 96 found 29 fully parseable multi-JSON call sequences. Executing them sequentially in isolated copies passed task acceptance at that point in 23 cases. **This is not a new agent success rate:** the model did not continue under new feedback. It shows substantial interference from the single-object parser.

A separate compatibility check was therefore registered in `../agent-study-v3`: support full JSON call sequences, allow agent Python to import the working directory while keeping the hidden grader isolated, and raise the per-turn cap to 3,072 without changing the cumulative budget. All three changes occur together, so their separate effects are not identified. Original results remain intact and scores are not pooled.

The repaired setup first faced three four-requirement capability tasks with a3/3 threshold. Only files and code passed. Data first produced an invalid escape, then corrected code failed to create the reports directory and raised a tool error, yet issued finish in the same batch. Independent verification found all four reports absent. The registered stopping rule was followed: **the repaired second batch of 96 was not started**, and prompts were not tuned until positive results appeared.

## Recommendations for later training

1. Do not yet start identity-restatement SFT or Agentic RL. That would mix protocol learning, basic coding capability, and long-horizon stopping, leaving the source of gains unclear.
2. First validate a mature tool-calling setup with clear semantics for multiple calls, tool-result feedback, imports, and correct termination. Confirm capability on independent multi-requirement short tasks; single-requirement6/6 is insufficient.
3. After passing that gate, establish enough cases where budget remains, prior execution is correct, remaining requirements are feasible, yet the model stops voluntarily. Then compare task identity, generic reminders, to-do status, and position/remaining-count cues.
4. If stable independent gains emerge, use paired SFT with the same actions/tool results to isolate status representation, then consider Agentic RL. Current evidence neither proves the technique universally ineffective nor shows that it solves real Codex long-task failures.

The research claim remains: label effects were found in the earlier controlled numerical execution task; transfer to these file/data/code tasks is not yet supported. **Do not combine the two stages into a claim that agent early stopping or RSI has been solved.**

## Review and reproduction entry points

- `REPORT.md` and `analysis/results.json`: all four-condition summaries and paired results by family and length.
- `analysis/all-failures.json`, `failure-diagnostics.json`, `post-completion-review.json`: all failures, format factors, and post-completion actions.
- `analysis/verification.json`, `replay.json`: 96 independent checks, hashes, and action replays.
- `runs/main-*/*/`: raw messages, trajectory, summary, and final-workspace.
- `../agent-study-v3/analysis/calibration-verification.json`: compatibility-check calibration and evidence of failure to pass the threshold.
- `COMPLETION_AUDIT.md`: itemized goal acceptance; unrun branches are not claimed complete.
