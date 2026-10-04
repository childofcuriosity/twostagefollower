# 固定随机抽样：工具标签正确、统一标签错误的三条长调用案例

模型Qwen2.5-1.5B，训练seed=11；抽样seed=20260924。候选池117条，按题目ID排序后无放回抽3条。只按OOD、macro答案正确、flat答案错误筛选，未按错误类型挑选。

“统一标签”仍包含step:和全部生成步骤，不是没有任何标签。两组同题同输入。执行器重算真值，并严格解析完整Answer行；三条macro的完整原语顺序和每步状态也均正确。条件抽样不能代表所有错误比例。

## 题目 4354

输入：
```text
Execute functions from left to right on four digits. Show the primitive steps and final Answer.
Primitives: rev reverses; rot rotates left; inc adds 1 mod 10 to all; neg negates mod 10; swap swaps first two; ends adds 1 mod 10 to first and last.
Input: 5 9 5 8
Functions: black white red
Trace:
```

工具定义（供审核，实际题面不提供）：
- black: inc,swap
- white: inc,neg,inc
- red: rot,inc

正确答案：`5 5 2 1`

macro原始输出：
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

执行步骤数 7/7；首次操作偏离位置 None；相对于所生成操作的算术错误位置 []。

flat原始输出：
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

执行步骤数 5/7；首次操作偏离位置 6；相对于所生成操作的算术错误位置 []。

## 题目 4617

输入：
```text
Execute functions from left to right on four digits. Show the primitive steps and final Answer.
Primitives: rev reverses; rot rotates left; inc adds 1 mod 10 to all; neg negates mod 10; swap swaps first two; ends adds 1 mod 10 to first and last.
Input: 4 4 0 7
Functions: red pink white brown
Trace:
```

工具定义（供审核，实际题面不提供）：
- red: rot,inc
- pink: rot,inc,swap
- white: inc,neg,inc
- brown: inc,inc,inc

正确答案：`4 1 7 7`

macro原始输出：
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

执行步骤数 11/11；首次操作偏离位置 None；相对于所生成操作的算术错误位置 []。

flat原始输出：
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

执行步骤数 5/11；首次操作偏离位置 6；相对于所生成操作的算术错误位置 []。

## 题目 4475

输入：
```text
Execute functions from left to right on four digits. Show the primitive steps and final Answer.
Primitives: rev reverses; rot rotates left; inc adds 1 mod 10 to all; neg negates mod 10; swap swaps first two; ends adds 1 mod 10 to first and last.
Input: 7 0 4 9
Functions: blue white pink
Trace:
```

工具定义（供审核，实际题面不提供）：
- blue: rev,rot,inc
- white: inc,neg,inc
- pink: rot,inc,swap

正确答案：`3 0 1 6`

macro原始输出：
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

执行步骤数 9/9；首次操作偏离位置 None；相对于所生成操作的算术错误位置 []。

flat原始输出：
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

执行步骤数 6/9；首次操作偏离位置 7；相对于所生成操作的算术错误位置 []。
