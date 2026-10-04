# Paired trajectory spot checks
First count all same-example improvements/degradations, then sample 3 from each with fixed random seed20260925. These examples show 32B expansion-specialist improvements and 7B expansion-specialist degradations, all with 8 tools and the same correct-sequence oracle. Samples verify error content rather than replace full statistics. All 3 randomly sampled 32B cases happen to come from seed11; consult the three-seed summaries separately.

## qwen32b / order_oracle / 8 / gain
Sampled 3 of 81 paired events.

### seed11, id=100444
Input: [6, 5, 5, 1]; name sequence: green → green → brown → green → black → brown → blue → green
First error at tool 5: `black`; expected ['inc', 'swap']; incorrect emitted operations: ['inc'].
Full trajectory correct: joint=False, specialist=True.
Raw body for this tool from the joint model:
```text
inc 9 5 0 9
EndTool
```
Raw body at the same position from the specialist:
```text
inc 9 5 0 9
swap 5 9 0 9
EndTool
```
Raw files: `runs/qwen32b-joint-s11/evaluation-order_oracle-independent.jsonl`; `runs/qwen32b-order_oracle-s11/evaluation-order_oracle-independent.jsonl`.

### seed11, id=100452
Input: [9, 1, 3, 1]; name sequence: blue → green → gray → red → white → pink → brown → gray
First error at tool 5: `white`; expected ['inc', 'neg', 'inc']; incorrect emitted operations: ['inc', 'neg'].
Full trajectory correct: joint=False, specialist=True.
Raw body for this tool from the joint model:
```text
inc 5 3 5 7
neg 5 7 5 3
EndTool
```
Raw body at the same position from the specialist:
```text
inc 5 3 5 7
neg 5 7 5 3
inc 6 8 6 4
EndTool
```
Raw files: `runs/qwen32b-joint-s11/evaluation-order_oracle-independent.jsonl`; `runs/qwen32b-order_oracle-s11/evaluation-order_oracle-independent.jsonl`.

### seed11, id=100391
Input: [5, 7, 7, 5]; name sequence: red → pink → pink → green → pink → gold → red → brown
First error at tool 8: `brown`; expected ['inc', 'inc', 'inc']; incorrect emitted operations: ['inc', 'inc'].
Full trajectory correct: joint=False, specialist=True.
Raw body for this tool from the joint model:
```text
inc 4 2 2 4
inc 5 3 3 5
EndTool
```
Raw body at the same position from the specialist:
```text
inc 4 2 2 4
inc 5 3 3 5
inc 6 4 4 6
EndTool
```
Raw files: `runs/qwen32b-joint-s11/evaluation-order_oracle-independent.jsonl`; `runs/qwen32b-order_oracle-s11/evaluation-order_oracle-independent.jsonl`.

## qwen7b / order_oracle / 8 / loss
Sampled 3 of 122 paired events.

### seed33, id=100479
Input: [8, 0, 1, 0]; name sequence: gold → green → blue → blue → brown → gray → blue → gold
First error at tool 4: `blue`; expected ['rev', 'rot', 'inc']; incorrect emitted operations: ['rev', 'rot'].
Full trajectory correct: joint=True, specialist=False.
Raw body for this tool from the joint model:
```text
rev 3 2 0 2
rot 2 0 2 3
inc 3 1 3 4
EndTool
```
Raw body at the same position from the specialist:
```text
rev 3 2 0 2
rot 2 0 2 3
EndTool
```
Raw files: `runs/qwen7b-joint-s33/evaluation-order_oracle-independent.jsonl`; `runs/qwen7b-order_oracle-s33/evaluation-order_oracle-independent.jsonl`.

### seed33, id=100409
Input: [0, 9, 4, 9]; name sequence: black → brown → pink → gold → white → brown → blue → brown
First error at tool 7: `blue`; expected ['rev', 'rot', 'inc']; incorrect emitted operations: ['rev'].
Full trajectory correct: joint=True, specialist=False.
Raw body for this tool from the joint model:
```text
rev 3 7 8 8
rot 7 8 8 3
inc 8 9 9 4
EndTool
```
Raw body at the same position from the specialist:
```text
rev 3 7 8 8
EndTool
```
Raw files: `runs/qwen7b-joint-s33/evaluation-order_oracle-independent.jsonl`; `runs/qwen7b-order_oracle-s33/evaluation-order_oracle-independent.jsonl`.

### seed33, id=100447
Input: [4, 2, 8, 7]; name sequence: gold → gold → gold → red → brown → green → gold → pink
First error at tool 4: `red`; expected ['rot', 'inc']; incorrect emitted operations: ['rot'].
Full trajectory correct: joint=True, specialist=False.
Raw body for this tool from the joint model:
```text
rot 1 5 7 0
inc 2 6 8 1
EndTool
```
Raw body at the same position from the specialist:
```text
rot 1 5 7 0
EndTool
```
Raw files: `runs/qwen7b-joint-s33/evaluation-order_oracle-independent.jsonl`; `runs/qwen7b-order_oracle-s33/evaluation-order_oracle-independent.jsonl`.
