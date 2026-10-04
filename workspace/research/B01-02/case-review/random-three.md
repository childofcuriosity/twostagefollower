# Fixed random sample: three long-call cases where tool labels succeed and uniform labels fail

Model: Qwen2.5-1.5B, training seed 11; sampling seed 20260924. Sort the 117 eligible examples by ID and sample three without replacement. Eligibility uses OOD, correct macro answer, and incorrect flat answer, without selecting error types.

Uniform labels still contain step: and all generated steps. Both groups use identical examples/inputs. The executor recomputes truth and strictly parses full Answer lines. All three macro primitive sequences and intermediate states are also correct. Conditional sampling does not estimate overall error shares.

## Example 4354

Input:
```text
Execute functions from left to right on four digits. Show the primitive steps and final Answer.
Primitives: rev reverses; rot rotates left; inc adds 1 mod 10 to all; neg negates mod 10; swap swaps first two; ends adds 1 mod 10 to first and last.
Input: 5 9 5 8
Functions: black white red
Trace:
```

Tool definitions for review; absent from the actual prompt:
- black: inc, swap
- white: inc, neg, inc
- red: rot, inc

Correct answer: `5 5 2 1`

Raw macro output:
```text
black:
inc 6 0 6 9
swap 0 6 6 9
white:
inc 1 7 7 0
neg 9 3 3 0
inc 0 4 4 1
red:
rot 4 4 1 0
inc 5 5 2 1
Answer: 5 5 2 1
```

Executed steps 7/7; first operation divergence: None; arithmetic error positions relative to emitted operations: [].

Raw flat output:
```text
step:
inc 6 0 6 9
swap 0 6 6 9
step:
inc 1 7 7 0
neg 9 3 3 0
inc 0 4 4 1
Answer: 0 4 4 1
```

Executed steps 5/7; first operation divergence: 6; arithmetic error positions relative to emitted operations: [].

## Example 4617

Input:
```text
Execute functions from left to right on four digits. Show the primitive steps and final Answer.
Primitives: rev reverses; rot rotates left; inc adds 1 mod 10 to all; neg negates mod 10; swap swaps first two; ends adds 1 mod 10 to first and last.
Input: 4 4 0 7
Functions: red pink white brown
Trace:
```

Tool definitions for review; absent from the actual prompt:
- red: rot, inc
- pink: rot, inc, swap
- white: inc, neg, inc
- brown: inc, inc, inc

Correct answer: `4 1 7 7`

Raw macro output:
```text
red:
rot 4 0 7 4
inc 5 1 8 5
pink:
rot 1 8 5 5
inc 2 9 6 6
swap 9 2 6 6
white:
inc 0 3 7 7
neg 0 7 3 3
inc 1 8 4 4
brown:
inc 2 9 5 5
inc 3 0 6 6
inc 4 1 7 7
Answer: 4 1 7 7
```

Executed steps 11/11; first operation divergence: None; arithmetic error positions relative to emitted operations: [].

Raw flat output:
```text
step:
rot 4 0 7 4
inc 5 1 8 5
step:
rot 1 8 5 5
inc 2 9 6 6
swap 9 2 6 6
Answer: 9 2 6 6
```

Executed steps 5/11; first operation divergence: 6; arithmetic error positions relative to emitted operations: [].

## Example 4475

Input:
```text
Execute functions from left to right on four digits. Show the primitive steps and final Answer.
Primitives: rev reverses; rot rotates left; inc adds 1 mod 10 to all; neg negates mod 10; swap swaps first two; ends adds 1 mod 10 to first and last.
Input: 7 0 4 9
Functions: blue white pink
Trace:
```

Tool definitions for review; absent from the actual prompt:
- blue: rev, rot, inc
- white: inc, neg, inc
- pink: rot, inc, swap

Correct answer: `3 0 1 6`

Raw macro output:
```text
blue:
rev 9 4 0 7
rot 4 0 7 9
inc 5 1 8 0
white:
inc 6 2 9 1
neg 4 8 1 9
inc 5 9 2 0
pink:
rot 9 2 0 5
inc 0 3 1 6
swap 3 0 1 6
Answer: 3 0 1 6
```

Executed steps 9/9; first operation divergence: None; arithmetic error positions relative to emitted operations: [].

Raw flat output:
```text
step:
rev 9 4 0 7
rot 4 0 7 9
inc 5 1 8 0
step:
inc 6 2 9 1
neg 4 8 1 9
inc 5 9 2 0
Answer: 5 9 2 0
```

Executed steps 6/9; first operation divergence: 7; arithmetic error positions relative to emitted operations: [].
