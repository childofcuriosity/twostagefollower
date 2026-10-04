# Scoring boundary cases and supplementary error categories

Strict scoring requires correct operations, all states, and the final Answer. Headings are an independent compliance metric. The table below interprets saved raw outputs without changing scores.

| Condition/seed | Strict failures | Numerical steps | Operation sequence | Final Answer only | Extra Trace heading (no primary-score penalty) |
|---|---:|---:|---:|---:|---:|
| STEP/301 | 13 | 12 | 0 | 1 | 0 |
| STEP/302 | 2 | 1 | 1 | 0 | 0 |
| STEP/303 | 4 | 4 | 0 | 0 | 0 |
| NAME/301 | 3 | 3 | 0 | 0 | 0 |
| NAME/302 | 6 | 6 | 0 | 0 | 49 |
| NAME/303 | 4 | 4 | 0 | 0 | 4 |

All 49 heading-noncompliant outputs for NAME seed302 and 4 for seed303 result from an extra `Trace:` heading. Removing that heading leaves compliant tool identities and order. The original scorer permits generic heading lines, so these are not unknown extra lines and incur no binary-reward penalty. A fully compliant heading rate of 90.43% must not be interpreted as only 90.43% correct tool names.

## STEP seed301, test-00474
Strict trajectory=0; full heading compliance=1. Input [3, 2, 1, 3], tool indices [4, 3].

Actual output:
```text
step:
rot 2 1 3 3
inc 3 2 4 4
swap 2 3 4 4
step:
inc 3 4 5 5
rev 5 5 4 3
Answer: 3 4 5 5
```

Reference output:
```text
step:
rot 2 1 3 3
inc 3 2 4 4
swap 2 3 4 4
step:
inc 3 4 5 5
rev 5 5 4 3
Answer: 5 5 4 3

```

## NAME seed302, test-00039
Strict trajectory=1; full heading compliance=0. Input [0, 1, 4, 4], tool indices [8, 6].

Actual output:
```text
Trace:
brown:
inc 1 2 5 5
inc 2 3 6 6
inc 3 4 7 7
white:
inc 4 5 8 8
neg 6 5 2 2
inc 7 6 3 3
Answer: 7 6 3 3
```

Reference output:
```text
brown:
inc 1 2 5 5
inc 2 3 6 6
inc 3 4 7 7
white:
inc 4 5 8 8
neg 6 5 2 2
inc 7 6 3 3
Answer: 7 6 3 3

```

