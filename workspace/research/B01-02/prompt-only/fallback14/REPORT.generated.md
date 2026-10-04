# Repeating tool identities with prompting alone: formal results

Model: Qwen/Qwen2.5-14B-Instruct Original weights, without adapters or training. The primary comparison is NAME−STEP. Success requires the complete operation sequence, every intermediate state, and the final Answer to be correct.

## Length selection and exploration

Formal lengths selected using STEP alone:2.Select the shortest and longest lengths within the 20%–90% range.

| Call length | STEP | NAME |
|---:|---:|---:|
| 2 | 21/32 (65.62%) | 20/32 (62.50%) |
| 5 | 3/32 (9.38%) | 5/32 (15.62%) |
| 10 | 0/32 (0.00%) | 0/32 (0.00%) |
| 15 | 0/32 (0.00%) | 0/32 (0.00%) |
| 20 | 0/32 (0.00%) | 0/32 (0.00%) |
| 30 | 0/32 (0.00%) | 0/32 (0.00%) |
| 40 | 0/32 (0.00%) | 0/32 (0.00%) |

## Four formal conditions

| L | Header | Strict success | Paired difference from STEP, 95% interval (percentage points) | All headers compliant | Output tokens/example | Input tokens/example | Generate time (seconds) |
|---:|---|---:|---|---:|---:|---:|---:|
| 2 | STEP | 235/512 (45.90%) | — | 100.00% | 67.99 | 473.00 | 101.47 |
| 2 | POSITION | 245/512 (47.85%) | +1.95 [-2.34, +6.25] | 97.07% | 68.34 | 493.00 | 105.81 |
| 2 | ALIAS | 294/512 (57.42%) | +11.52 [+6.84, +16.41] | 100.00% | 68.10 | 492.00 | 103.32 |
| 2 | NAME | 231/512 (45.12%) | -0.78 [-4.88, +3.32] | 95.31% | 67.47 | 477.00 | 100.57 |

Each example receives one greedy generation per condition, with the same underlying examples across all four conditions. The 95% intervals use 10,000 paired example-level bootstrap samples (seed 740001) and describe sampling uncertainty conditional on the fixed model, prompts, and example distribution. Repeated inference is not treated as training seeds. Auxiliary comparisons are not claimed as multiplicity-adjusted confirmatory findings.

## Primary comparison and costs

- L2: NAME−STEP -0.78 percentage points; NAME-only successes: 55; STEP-only successes: 59. Output: -0.52 tokens/example (-0.77%); total batch generate time: -0.90 seconds (-0.89%).

## First errors and termination reasons

| L | Condition | First-error counts | Termination reasons |
|---:|---|---|---|
| 2 | STEP | {"none": 235, "numeric": 182, "tool_or_order": 50, "extra_call": 37, "omitted_call": 7, "format": 1} | {"eos": 512} |
| 2 | POSITION | {"none": 245, "numeric": 207, "extra_call": 27, "omitted_call": 26, "tool_or_order": 7} | {"eos": 512} |
| 2 | ALIAS | {"none": 294, "numeric": 214, "tool_or_order": 2, "extra_call": 1, "format": 1} | {"eos": 512} |
| 2 | NAME | {"none": 231, "numeric": 227, "tool_or_order": 38, "extra_call": 15, "format": 1} | {"eos": 512} |

First-error labels: numeric = arithmetic or final-number error; tool_or_order = incorrect primitive expansion or order; omitted_call/extra_call = premature Answer, missing/extra primitive operations, or identifiable deletion/insertion of complete calls; format = formatting error; none = no strict trajectory error. Omission/addition labels classify observable outputs, not internal causes. Header counts are reported separately and can overlap. Header noncompliance does not automatically fail the primary metric.

## Scope and evidence

This experiment tests a synthetic execution task with nine supplied tools and four-digit states. With no training-length range, in-domain/out-of-domain terminology does not apply. ALIAS changes names in both inputs and outputs, so it is not an output-header-only intervention. Label forms, tokenization, prompts, and demonstration choices lack independent replication. Effects cannot be attributed uniquely to identity information or generalized to real agents.

Output-token counts include generated EOS tokens (text_tokens are stored separately). Generate time is GPU-synchronized batch wall time, not independent per-example latency. Concurrent GPU workloads and sequence lengths affect costs. The dispatch ledger also records allocated GPU time for loading, saving, and other work.

Evidence: top-level REGISTRATION.md; four templates in prompts/; frozen configurations and examples in data/; raw text, token IDs, termination reasons, and completeness markers in runs/; analysis/scores-*, graded-*, length-selection.json, and completion-audit.json; and logs/. Cross-model validation and real-task transfer remain future work. Results have not been externally published.
