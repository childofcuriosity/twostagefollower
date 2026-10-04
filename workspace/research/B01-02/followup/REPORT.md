# B01-02 follow-up: do abstraction proposals improve with execution learning?

Completed at (UTC): 2026-09-24T03:23:17Z. The user authorized continuation; this round is complete and awaits review.

## Judgment

**Passes the prespecified screen against random proposals but remains substantially below the frozen base. This does not support better useful-abstraction proposals after one execution-learning stage. Stop expanding this execution-training route and retain it as a counterexample and diagnostic.**

These are measurements with existing Qwen2.5-1.5B and flat/macro adapters, not newly trained proposal policies. Negative results do not exclude specially trained innovation strategies; positive results would not establish multi-round improvement. The protocol was fixed before generation, and analysis source separately registered before utility inspection.

## Actual design

- Eight independent families, each with three hidden short-operation patterns semantically distinct from the previous nine macros, 16 support programs, and 128 tests. Support/test functions are exactly disjoint; test functions need not be distinct from one another. Families are equally weighted.
- Models see support programs without hidden boundaries and generate 16 length-2–3 candidates. A finite-token trie constrains 252 valid candidates. Duplicates/identities consume budget without replacement.
- Three runs each for base/flat/macro, plus three macro mismatched-context controls. Training seeds are 11/22/33; base repeats vary sampling only.
- All methods select up to three semantically distinct macros using the same support-greedy rule and definition costs, without test-based selection. Random also has 16 proposals; frequency/full-enumeration references use different compute.
- Twelve model jobs and 1,536 actual proposals, with no new parameter training or reruns of the earlier 30 training jobs.

## Main results

Compression is net description-length reduction on unseen programs, not neural accuracy. Search discovery is external symbolic breadth-first discovery of complete target functions within 3,000 action expansions.

| Method | Test net compression | Search discovery | Mean library size | Distinct semantics per 16 proposals* |
|---|---:|---:|---:|---:|
| Frozen base | 37.95% | 67.48% | 2.25 | 10.08 |
| Greedy over all 252 candidates | 45.20% | 72.36% | 3.00 | 120.00 |
| After flat-trace training | 1.35% | 51.63% | 0.29 | 3.00 |
| Support-frequency heuristic | 57.04% | 76.27% | 3.00 | 15.00 |
| After macro-label training | 19.43% | 60.77% | 1.12 | 5.33 |
| Macro model + mismatched context | 2.05% | 51.07% | 0.25 | 5.38 |
| No macro library | 0.00% | 49.12% | 0.00 | 0.00 |
| 16 uniform random proposals | 11.74% | 53.45% | 1.25 | 14.50 |

*Full enumeration uses 252 candidates, no-library uses zero, and other methods use 16. Deterministic heuristics/no-library repeat in paired analyses across three seeds, not three independent experiments. Macros and primitives each count as one search action, but macros execute more primitives; see family-level raw counts.

| Comparison | Compression difference (points) | Three seed differences | Family-bootstrap 95% interval | Search difference (points) |
|---|---:|---|---|---:|
| macro − flat | +18.09 | +16.54 / +20.22 / +17.50 | +9.71 to +27.34 | +9.15 |
| macro − base | -18.52 | -17.85 / -15.94 / -21.76 | -26.76 to -10.01 | -6.71 |
| macro − random | +7.69 | +9.10 / +9.75 / +4.23 | -3.11 to +18.13 | +7.32 |
| macro − mismatch | +17.38 | +16.23 / +18.00 / +17.92 | +9.56 to +26.32 | +9.70 |
| macro − frequency | -37.61 | -39.36 / -35.08 / -38.39 | -47.45 to -27.46 | -15.49 |

Prespecified screen: macro exceeds random mean compression by at least two points, improves across all three seeds, and loses no more than two points in search discovery. Decision: **Pass**. Intervals cluster eight families conditional on checkpoints; 1,536 proposals are not independent training repetitions.

## Why the overall judgment remains against this route

Macro beats random compression by +7.69 points, but the family-bootstrap interval is approximately −3.11 to +18.13, with substantial family uncertainty. Passing a screen does not mean significant superiority. More importantly, macro is 18.52 points below frozen base, declining for every seed, with interval approximately −26.76 to −10.01. Search discovery is also 6.71 points below base. Better execution did not transfer to better proposing.

Macro beats flat and mismatched context, indicating retained context adaptation rather than superiority to pretraining. Distinct semantics per 16 proposals fall from approximately 10.08 for base to 5.33 for macro and 3.00 for flat. Diversity contraction co-occurs with lower utility but is not identified as its cause, nor does it diagnose loss of all general capabilities. The support-frequency heuristic compresses 57.04%, substantially better but with different candidate-acquisition compute.

## Post hoc sensitivity checks

Two issues were added after primary results without overwriting them; see [amendments](analysis/amendments.md) and [complete 2×2 controls](analysis/sensitivity.json).

- Original semantic deduplication retained the first spelling, while compression requires literal matching. Selecting support gains first and excluding semantic equivalents afterward yields base 38.79%, macro 19.60%, flat 1.53%, random 11.74%, preserving direction. Full enumeration rises to 57.04%, matching the frequency heuristic. Its earlier disadvantage reflected representative selection, not inherently harmful extra candidates.
- With original selection but a 3,000-primitive-execution budget, search rates are base 58.95%, macro 55.96%, random 49.22%, flat 49.48%. Macro remains below base, including when both modifications apply.

Do not add larger models or more similar execution training. Continuing would require training directly for proposal utility, testing unseen families, and controls preserving base proposing. That next-stage design awaits review and was not started here.

## Interpretation limits

1. Earlier models learned execution traces without efficient-abstraction rewards or supervision. This tests transfer of that training; an untrained skill failure does not establish unlearnable innovation.
2. All methods share executor-generated correct support, not autonomously solved successes. The artificial DSL has only 252 macro candidates.
3. Contiguous-primitive compression need not accelerate search because macros increase branching. Report search separately rather than substituting the better metric for a failed one.
4. Budgets match proposal counts and downstream selection, not model/random/frequency compute. Equal action expansions are not equal primitive-execution costs.
5. Tasks differ from the old library but share six primitives. This is not natural-language, real-code, or cross-primitive transfer.
6. Do not tune prompts, temperature, candidate counts, or families on this test. Retain all proposals, duplicates, and negative-utility candidates.

## Audit and reproduction

- [Preregistration](PROTOCOL.md), [mechanism limits](MECHANISM.md), [initial hashes](analysis/registration.json), [evaluation registration](analysis/evaluation-registration.json).
- [Machine-readable results](analysis/results.json), [method/seed/family records](analysis/rows.jsonl), [verification/hashes](analysis/verification.json).
- `runs/*/proposals.jsonl` retains complete prompts, raw generations, candidate indices, and token counts. `data/tasks.json` retains support/tests and hidden patterns; `data/candidates.json` contains the candidate universe.
- Reuse parent `runs/*/adapter` and root `.training-venv`; all new files stay in this subtree. Base/adapter hashes are in parent `analysis/artifact-verification.json`.
- Total device reservation approximately 0.104 GPU-hours; CPU analysis wall time 0.9 seconds. Reservation includes loading/waiting, not kernel-active time. Independent jobs use separate GPUs without NCCL training.

From the project root, first `source training-env.sh`. Build data with `python workspace/research/B01-02/followup/src/common.py`. `src/launch.py` dispatches generation and refuses to overwrite existing runs. Run `src/analyze.py`, `src/verify.py`, and `src/report.py` for statistics, verification, and reporting. Use new run directories for reproduction to retain original evidence.
