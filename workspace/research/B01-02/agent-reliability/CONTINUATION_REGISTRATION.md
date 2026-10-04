# Follow-up verification registration

2026-09-25. The user again requested continued work on the problem. The earlier report records an interim stage rather than completion of the overall goal. This registration precedes follow-up runs; earlier source and trajectories remain unchanged.

## A: Executor and per-turn truncation checks

- Freeze the same Qwen2.5-32B-Instruct, tools, tasks, greedy decoding, and total generation budget 24000. Use the three earlier 24-ticket tasks as a diagnostic set, not independent held-out validation.
- v4 fixes only consecutive protocol-error counting: a fully parsed response with no calls that ends by length truncation is still an error; do not reset the counter before later checks. Preserve raw abnormal outputs and recovery messages.
- Four conditions: full/4096, sanitize/4096, full/8192, sanitize/8192. Each uses all 3 seeds20267001–20267003, totaling 12 trajectories. Retain every failure.
- Parameters other than the original per-turn cap are unchanged. The implementation reserves the next turn's maximum generation within the 30000 context budget, so the 8192 condition allows shorter maximum input. Check context-budget triggers record by record. If triggered, the comparison is not single-factor truncation evidence and requires another control with equal input limits.
- Primary metrics: actually correct ticket count and complete workflow success. Auxiliary metrics: delivered count, actual stopping reason, truncation/error events, first pseudo-role occurrence, tokens, and costs. Self-reported completion cannot replace acceptance checks.
- Compare the 4096 condition against earlier results to determine whether the counter repair changes behavior. The 8192 comparison tests truncation dependence; outcomes need not favor history filtering.

## Remaining overall work

This batch is diagnostic and does not complete the overall goal. Independent new tasks, deletion-length controls, other suitable models, decoding settings, and practical workflows with semantic subtasks and dependencies remain necessary. Freeze new tasks and formal controls separately before running them. If results are weak, investigate causes, revise the method while retaining failures, and use new held-out validation. The final report must distinguish identity restatement from history repair and examine cross-task utility, cost, and degradation, rather than end with selected positive examples.

## B: Independent held-out tickets (freeze data first)

- Fix 12 new seeds20268001–20268012, each with 24 tickets, disjoint from earlier seeds. Retain the data-generation algorithm to test independent in-distribution replication. Include every seed without performance-based additions or deletions.
- Generate and hash-freeze data now, before model runs. Register and freeze the history policies and deletion-length control before B inference starts. A diagnostics may only repair the executor and determine budgets; B results must not be inspected to select methods.
- Cross-task and cross-model validation remain separate; these 12 in-distribution samples do not replace them.
