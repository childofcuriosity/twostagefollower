# Example-level review of NAME and STEP

This read-only review uses existing formal outputs without new inference or score changes. Selection rules are stated below. Cases illustrate specific errors and do not replace the aggregate statistics over 512 examples.

NAME corrects 55 STEP failures and introduces 59 new failures. Of the new failures, 53 first err numerically and six in tools/order. The 281 NAME failures comprise 227 numeric, 53 tool/order, and one formatting first error. Numeric first errors involve inc 85, neg 46, swap 45, rot 29, rev 17, and Answer 5; these counts are not normalized by operation exposure.

## formal-L2-0009

The first example ID where STEP succeeds and NAME first errs numerically.

Input: `4 6 1 0`; plan: `black → black`.

Raw NAME output (numeric):
```text
black:
inc 5 7 2 1
swap 7 5 2 1
black:
inc 8 6 3 1
swap 6 8 3 1
Answer: 6 8 3 1
```

Correct trajectory:
```text
black:
inc 5 7 2 1
swap 7 5 2 1
black:
inc 8 6 3 2
swap 6 8 3 2
Answer: 6 8 3 2
```

Raw STEP output for the same example (none):
```text
step:
inc 5 7 2 1
swap 7 5 2 1
step:
inc 8 6 3 2
swap 6 8 3 2
Answer: 6 8 3 2
```

## formal-L2-0016

The first example ID where STEP succeeds and NAME first errs in tools/order.

Input: `6 3 6 6`; plan: `gold → green`.

Raw NAME output (tool_or_order):
```text
gold:
inc 7 4 7 7
rev 7 7 4 7
green:
rot 7 4 7 7
rot 4 7 7 7
inc 5 8 0 7
Answer: 5 8 0 7
```

Correct trajectory:
```text
gold:
inc 7 4 7 7
rev 7 7 4 7
green:
rot 7 4 7 7
rot 4 7 7 7
Answer: 4 7 7 7
```

Raw STEP output for the same example (none):
```text
step:
inc 7 4 7 7
rev 7 7 4 7
step:
rot 7 4 7 7
rot 4 7 7 7
Answer: 4 7 7 7
```

## formal-L2-0013

The first example ID with a NAME numeric first error involving neg; both conditions fail.

Input: `3 2 5 2`; plan: `white → gray`.

Raw NAME output (numeric):
```text
white:
inc 4 3 6 3
neg 6 7 3 7
inc 7 8 4 8
gray:
rot 8 4 8 7
rot 4 8 7 8
inc 5 9 8 9
Answer: 5 9 8 9
```

Correct trajectory:
```text
white:
inc 4 3 6 3
neg 6 7 4 7
inc 7 8 5 8
gray:
rot 8 5 8 7
rot 5 8 7 8
inc 6 9 8 9
Answer: 6 9 8 9
```

Raw STEP output for the same example (numeric):
```text
step:
inc 4 3 6 3
neg 6 7 3 7
inc 7 8 4 8
step:
rot 8 4 8 7
rot 4 8 7 8
inc 5 9 0 9
Answer: 5 9 0 9
```

## formal-L2-0018

The first example ID where NAME succeeds and STEP first errs in tools/order.

Input: `0 1 2 3`; plan: `black → green`.

Raw NAME output (none):
```text
black:
inc 1 2 3 4
swap 2 1 3 4
green:
rot 1 3 4 2
rot 3 4 2 1
Answer: 3 4 2 1
```

Correct trajectory:
```text
black:
inc 1 2 3 4
swap 2 1 3 4
green:
rot 1 3 4 2
rot 3 4 2 1
Answer: 3 4 2 1
```

Raw STEP output for the same example (tool_or_order):
```text
step:
inc 1 2 3 4
swap 2 1 3 4
step:
rot 1 3 4 2
rot 3 4 2 1
inc 4 5 3 2
Answer: 4 5 3 2
```

## Interpretation limits

Correct tool headers can coexist with wrong numbers or missing/extra primitive operations. NAME improves expansion on some examples and worsens others. These outputs support the judgment that improved operation expansion does not offset numeric errors. Cases do not establish diverted attention, name-semantic interference, or another internal mechanism. SHA hashes of the original NAME and STEP outputs follow:
8e1a97c61311d0ade5b9308aac2500414dd9bd23fee084a500ff5109f8959e67
171d7e8bcf7e300e6e8842723712f58b993af44885790c334ddeee13a17004f0
