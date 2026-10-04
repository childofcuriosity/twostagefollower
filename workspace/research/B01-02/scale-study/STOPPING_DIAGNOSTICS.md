## Broad early-answer metric and output segments

The broad definition requires exactly one valid final Answer and fewer parseable primitive operations than the target. It includes incorrect prefixes and cannot alone distinguish stopping errors, skipped operations, or parsing omissions. The table covers all original long examples, with 1,152 outputs per condition (384 examples × three seeds). The correct-prefix metric is a more conservative, verifiable subset.

| Model | Label | Answers before emitting all operations | Early answer after correct prefix |
|---|---|---:|---:|
| qwen1.5b | flat | 100.00% | 87.59% |
| qwen1.5b | macro | 69.36% | 43.23% |
| qwen3b | flat | 100.00% | 89.15% |
| qwen3b | macro | 37.50% | 20.57% |
| qwen7b | flat | 77.17% | 58.68% |
| qwen7b | macro | 40.80% | 26.39% |
| qwen32b | flat | 52.43% | 38.37% |
| qwen32b | macro | 25.95% | 21.70% |

See the [CSV](analysis/output-segment-distribution.csv) for emitted segment counts relative to required calls. Header counts describe formatting only. Correct counts still require operation/state checks and do not measure completion.
