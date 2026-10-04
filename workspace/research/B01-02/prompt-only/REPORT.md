# B01-02: prompt-only tool-identity repetition

Completed 2026-09-28. **This round found no evidence that repeating original tool names improves strict complete-trajectory success.** Formal evaluation used the authorized Qwen2.5-14B-Instruct fallback on 512 fresh L2 examples. NAME scored 45.12% and STEP 45.90%, a paired difference of −0.78 percentage points with a 95% interval of [−4.88,+3.32]. This does not establish equivalence or exclude gains with other prompts or tasks.

The fixed-renaming ALIAS condition produced an auxiliary positive result: 57.42%, or +11.52 points over STEP [+6.84,+16.41]. Because ALIAS changes input tool names and output headers together, its gain cannot be attributed solely to repeating identities before execution. Current evidence does not support directly extending the large fine-tuning gains to prompting alone.

## Model selection and call lengths

Original 7B weights first completed independent prechecks and all exploration. STEP scored 3/32 at L2 and 0/32 at L5. Precheck and raw-output audits found no definition, example, parsing, or budget defects; most errors involved arithmetic and operation expansion. The registered rule triggered the 14B fallback, which repeated the full procedure with **unchanged prompts**. All 7B results are retained. This is model selection, not independent cross-model confirmation.

| Call length | 7B STEP | 7B NAME | 14B STEP | 14B NAME |
|---:|---:|---:|---:|---:|
| 2 | 3/32 | 7/32 | 21/32 | 20/32 |
| 5 | 0/32 | 0/32 | 3/32 | 5/32 |
| 10 | 0/32 | 0/32 | 0/32 | 0/32 |
| 15 | 0/32 | 0/32 | 0/32 | 0/32 |
| 20 | 0/32 | 0/32 | 0/32 | 0/32 |
| 30 | 0/32 | 0/32 | 0/32 | 0/32 |
| 40 | 0/32 | 0/32 | 0/32 | 0/32 |

Only 14B L2 STEP accuracy lies within 20%–90%, so the rule selects that single length: **512 examples × four groups = 2,048 formal outputs**. A second length is not required. No adjacent tested lengths cross directly from above 90% to below 20%, and L40 is not saturated, so no additional exploration is triggered. L5 and longer lengths have only exploratory evidence; 32-example floor scores do not establish universal failure on long tasks.

## Formal results

| Condition | Strict success | Paired difference from STEP and 95% interval (percentage points) | Condition-only / STEP-only successes | All headers compliant |
|---|---:|---:|---:|---:|
| STEP | 235/512 (45.90%) | — | — | 512/512 (100%) |
| POSITION | 245/512 (47.85%) | +1.95 [−2.34,+6.25] | 67 / 57 | 497/512 (97.07%) |
| ALIAS | 294/512 (57.42%) | +11.52 [+6.84,+16.41] | 113 / 54 | 512/512 (100%) |
| NAME | 231/512 (45.12%) | −0.78 [−4.88,+3.32] | 55 / 59 | 488/512 (95.31%) |

Each example receives one greedy output per group; this is not a training-seed experiment. Intervals use analysis seed 740001 and 10,000 paired example-level bootstrap samples. They cover example-sampling uncertainty conditional on the fixed model, prompt, and test-generation distribution. Auxiliary controls have no multiple-comparison correction. Formal STEP accuracy differs from the 32-example exploratory estimate; formal results did not trigger length reselection or prompt changes.

## Which errors decreased?

The following are **reviewed first observable errors**, with one first error per failed output. Incorrect operation counts and expansions fall under tools/order; an extra primitive operation is not automatically an extra call.

| Condition | Tool expansion/order | Arithmetic/final numbers | Omitted complete call | Extra complete call | Format | Success |
|---|---:|---:|---:|---:|---:|---:|
| STEP | 93 | 182 | 0 | 0 | 2 | 235 |
| POSITION | 37 | 207 | 14 | 0 | 9 | 245 |
| ALIAS | 3 | 214 | 0 | 0 | 1 | 294 |
| NAME | 53 | 227 | 0 | 0 | 1 | 231 |

NAME reduces tool-expansion/order first errors from 93 to 53, but increases numeric first errors from 182 to 227, yielding no overall success gain. It corrects 55 STEP failures while turning 59 STEP successes into failures; 53 of the latter first err numerically.

ALIAS mainly improves expansion/order, reducing first errors from 93 to 3. It corrects 113 STEP failures: 71 originally first erred in tools/order, 41 numerically, and one in formatting. It also introduces 54 failures, all with numeric first errors. These are paired-output descriptions, not causal evidence about internal mechanisms.

First-error rules conservatively identify unambiguous complete-call deletion/insertion. Ambiguous operation alignments fall under tools/order. Overlapping checks are also retained: operation-sequence mismatches number 119/65/6/64 for STEP/POSITION/ALIAS/NAME, and intermediate numeric errors number 192/211/213/239. Header compliance is separate: 24 extra NAME `Trace:` headers do not imply 24 extra calls. **All 2,048 formal outputs end voluntarily with EOS; none hit the generation limit.** Exploration includes 3/448 capped 7B outputs and 10/448 capped 14B outputs, all retained without retries. All 48 precheck outputs per model end with EOS. Every exploratory length passed correct-target capacity checks, but model output errors and these truncations still affect long-task floor scores; no single mechanism is established.

Analysis correction: initial auxiliary `extra_call/omitted_call` labels from the frozen scorer conflated extra/missing primitives and intermediate Answer lines with call changes. Review corrected 99 auxiliary first-error labels while retaining original labels and raw outputs. Strict accuracy, paired differences, confidence intervals, prompts, and inference settings are unchanged. See `postanalysis/error_review.py` and `analysis/graded-formal-errors-reviewed.jsonl`.

## Output and inference costs

| Condition | Input tokens/example | Output tokens/example including EOS | Output relative to STEP | Total batch generate seconds for 512 examples | Generate relative to STEP |
|---|---:|---:|---:|---:|---:|
| STEP | 473 | 67.99 | — | 101.47 | — |
| POSITION | 493 | 68.34 | +0.50% | 105.81 | +4.28% |
| ALIAS | 492 | 68.10 | +0.15% | 103.32 | +1.83% |
| NAME | 477 | 67.47 | −0.77% | 100.57 | −0.89% |

NAME adds four input tokens per example and emits 0.52 fewer output tokens, with no observed output-cost increase. Its **correct targets** already have the same average token length as STEP; actual-output differences do not demonstrate more efficient correct execution. ALIAS adds 19 input tokens and 0.10 actual output tokens per example. Its correct targets average two extra tokens because of label tokenization.

Formal evaluation uses eight local PRO6000 GPUs, with two disjoint 256-example shards per condition and batch size 32. Generate time is measured after GPU synchronization; the table sums batch time across two GPUs rather than reporting per-example latency. Differences of approximately 1% may reflect hardware or scheduling variation and do not establish repeatable speedups. Formal dispatch wall time is 90.46 seconds and outer allocated GPU time is 0.198 hours. Including both models and all prechecks/exploration, total allocation is 1.046 GPU-hours. Allocation includes loading, saving, and polling intervals, not only kernel activity; downloads are excluded.

## Freezing, acceptance, and limits

7B revision: `a09a35458c702b33eeacc393d103063234e8bc28`; 14B revision: `cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8`. Both use official original weights, BF16, SDPA, no adapters, and no training. A single user message uses the official chat template, which adds the default Qwen system text. STEP/POSITION/NAME change only header rules and example headers. ALIAS applies the existing fixed renaming to both inputs and outputs.

Formal configuration was frozen at 2026-09-28 00:36:17 UTC before all eight formal jobs. The 512 fresh examples, 224 exploration examples, 12 precheck examples, and demonstration are pairwise disjoint in call-chain/four-digit-input pairs. Groups share underlying examples. The generation limit is 256 throughout; maximum correct targets are 76–78 tokens and maximum input length is 493, well below the 32,768-token context. Source/prompt hashes, token IDs and EOS, and exactly-once shard merging were verified.

All 3,040 outputs were rescored, with agreement between the original strict scorer and independent implementation. All 60 jobs exited with code 0; no OOM or interruption occurred. Every stage finished before the hourly inspection threshold. Final checks found 0 MiB on all eight local GPUs and no residual inference processes. Earlier training experiments are unchanged. See [COMPLETION_AUDIT.md](COMPLETION_AUDIT.md).

Conclusions apply to this model, prompt, mapping, and nine-tool synthetic task. The auxiliary ALIAS gain merits further study but does not validate a general identity-repetition method, real-agent transfer, or novelty. Independent cross-model replication and real execution tasks remain future work; results were not externally published.

Evidence: [preregistration](REGISTRATION.md), [7B exploration](7B_EXPLORATION.md), [formal prompts](fallback14/prompts/), [formal freeze and data](fallback14/data/formal-L2-manifest.json), [raw outputs](fallback14/runs/), [paired statistics](fallback14/analysis/scores-formal-L2.json), [reviewed errors](analysis/formal-errors-reviewed.json), and [overall audit and costs](analysis/final-research-audit.json).
