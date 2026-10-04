# Tool-label success and uniform-label failure: complete case attribution

This analysis reads existing model outputs without training or generation. It covers first-stage execution experiments, not compression proposals.

## Dataset size and denominators

Each training run uses 4,096 examples: 394 one-call and 3,702 two-call examples (90.38%). Development has 224 examples: 128 short and 96 long. Tests contain 560: 128 short, 384 long compositions, and 48 stress examples. Development is excluded below.

Models are Qwen2.5-1.5B, Qwen2.5-3B, and SmolLM2-1.7B, each trained with seeds 11/22/33 and paired macro/flat runs. Align identical IDs, numeric inputs, and tool chains across all 560 tests, selecting correct macro final answers and incorrect flat final answers.

This yields 1,473 model/seed/example pairs covering 370 distinct IDs: 1,302 long, 171 stress, and zero short records. Repeated examples across models/seeds are not 1,473 independent tests for significance inference.

Code recomputes truth and checks final answers, primitive order, arithmetic, and format for every case. Manual review samples three cases per model/seed, adding rare types and macro-process anomalies, for 69 distinct cases with sampling seed 20260925. Not all 1,473 cases were manually read.

## Observable errors across all cases

| Flat error type | Count | Share of conditional sample |
|---|---:|---:|
| First two tools fully correct, then an answer | 1297 | 88.05% |
| Wrong operation sequence, correct arithmetic for emitted operations | 164 | 11.13% |
| Correct prefix, ending inside a tool | 8 | 0.54% |
| Errors in both operation sequence and arithmetic | 1 | 0.07% |
| Invalid step format (gold treated as a primitive in these cases) | 3 | 0.20% |

| Model, all three seeds | Conditional cases | Stops after two correct tools | Share |
|---|---:|---:|---:|
| qwen1.5b | 394 | 353 | 89.59% |
| qwen3b | 789 | 701 | 88.85% |
| smol1.7b | 290 | 243 | 83.79% |

Every one of the 1,473 flat outputs contains exactly two step: segments and voluntarily emits Answer. Outputs contain 55–85 tokens against a 256-token cap; none reach it. These are not truncations from exhausted generation budgets, and no record lacks Answer.

Among 164 wrong-operation-sequence cases, the first tool is always correct and divergence occurs later. Some skip the second tool for a later one; others mix another tool into the second segment. Eight incomplete-prefix cases also have two segments but do not all execute exactly the first two tools. The sole arithmetic-error case is qwen1.5b/seed33/example 4873: its first rev changes 8 8 8 8 to 6 8 8 8. Three formatting anomalies, qwen3b/seed11/examples 4626–4628, contain gold followed by numbers rather than missing final answers.

## Strict review of the successful side

Correct macro answers do not guarantee correct processes. Of 1,473 cases, 1,448 have fully correct operations and numbers; 25 use different operations but match the final answer. Twelve of those are semantically equivalent over every numeric input. Thirteen match only on the current test input and do not establish execution of the requested program.

Restricting to the 1,448 fully correct macro processes still leaves 1,281 flat outputs (88.47%) stopping after two correct tools. The remainder have 155 operation-sequence errors, eight incomplete prefixes, three format anomalies, and one combined operation/arithmetic error. The main observation does not depend on chance-correct answers or equivalent rewrites.

## Interpretation and limits

Two-segment output patterns and premature answers dominate these observed differences; arithmetic is not the main issue. Training has 90.38% exactly-two-call examples and none above two. A supported hypothesis is that uniform step labels learn a two-segment stopping pattern from training, while tool-identity labels help track unfinished calls.

This remains behavioral evidence and a mechanism hypothesis, not causal identification. Two segments do not imply an internal two-tool capacity, nor do error categories identify attention mechanisms. Distinguishing explanations requires interventions on call indices, remaining-call cues, or training-length distributions while holding other factors fixed. No such experiments were added here.

These proportions apply only conditional on macro-answer success and flat-answer failure, not all flat failures or macro successes. Symmetric stress inputs especially require both process and answer reporting.

## Files

- [All 1,473 raw input/output pairs and checks](all-discordant-pairs.jsonl)
- [Filterable case index](all-discordant-index.csv)
- [Model/split statistics and source hashes](attribution-summary.json)
- [69 manually reviewed samples](manual-review-sample.jsonl)
- [Reproducible analysis](analyze_pairs.py)

Historical training results are unchanged. This analysis and all exports remain here.
