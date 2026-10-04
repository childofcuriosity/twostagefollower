# 7B exploration and fallback decision

This is the complete exploration before switching to the fallback model, not an independent cross-model confirmation. Model revision: a09a35458c702b33eeacc393d103063234e8bc28. Prompts were unchanged.

| L | STEP /32 | NAME /32 |
|---:|---:|---:|
| 2 | 3 | 7 |
| 5 | 0 | 0 |
| 10 | 0 | 0 |
| 15 | 0 | 0 |
| 20 | 0 | 0 |
| 30 | 0 | 0 |
| 40 | 0 | 0 |

STEP scored 9.375% at L2 and 0% at L5, both below the registered 20% short-task floor. Among 48 independent precheck outputs, first errors were numeric in 30, operation/order in 15, and omission in one; two were correct. All ended with EOS. Checks of full definitions, examples, scoring/parsing, and generation capacity found no implementation defects. The previously authorized 14B fallback therefore repeated the original procedure. Neither model nor length was selected using NAME gains.

In L2 exploration, NAME scored 7/32 and STEP 3/32. This small exploratory sample does not establish formal effectiveness. Both conditions scored 0/32 at every other initial length. All raw responses are in runs/explore-* and example-level scores in analysis/graded-explore-*.
