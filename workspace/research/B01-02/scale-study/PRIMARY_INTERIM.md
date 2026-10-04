# Interim results for the primary 32B comparison

Planned primary training and final evaluation on 560 examples are complete: three flat/macro seeds for 32B at fixed step 512. All 13,440 final outputs across four models have been checked individually. This does not establish completion of the full goal; independent confirmation, complete checkpoint evaluation, and supplementary controls remain in progress.

On unseen long compositions, 32B flat/macro answer accuracy is 44.36%/73.70% and complete-trajectory accuracy 44.27%/73.00%. Paired seed answer gains are 23.18, 26.04, and 38.80 points, averaging 29.34, with a three-seed 95% t interval from 8.68 to 50.00 points. The interval is wide with only three training seeds.

| Calls | Flat answer accuracy | Macro answer accuracy |
|---|---:|---:|
| 3 | 94.79% | 96.09% |
| 4 | 33.07% | 73.18% |
| 5 | 5.21% | 51.82% |

The scale concern has evidence: 32B flat stops after exactly two correct tools on only 0.26% of examples, substantially reducing the small-model behavior. It still answers after a correct incomplete prefix: 38.37% for flat and 21.70% for macro. This reduction is inconsistent across seeds; macro stops early more often for seed 11. Mean accuracy gains cannot all be attributed to suppressed early stopping. Conditions are nearly tied at three calls, with gains mainly at four/five calls.

Initial interpretation should focus on completion over longer compositions and operation-sequence generalization, distinguishing scale, training dose, and formatting. Data do not establish a causal prior-preservation mechanism or validate real-agent long tasks.

Auditable data: analysis/primary32-interim.json, analysis/results.json, and analysis/final-case-audit.jsonl. Final conclusions must incorporate independent confirmation and supplementary results. This file is not the final report.
