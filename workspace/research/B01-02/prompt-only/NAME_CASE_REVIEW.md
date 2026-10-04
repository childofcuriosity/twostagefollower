# NAME与STEP逐题案例复核

只读复核既有正式输出，没有重推理或改动评分。案例选择规则如下；这些例子用于解释具体错误，不用于替代512题总体统计。

NAME相对STEP纠正55题，同时新增59题失败；新增失败53题数字首错、6题工具/顺序首错。NAME失败281题：227数字、53工具/顺序、1格式；数字首错涉及inc85、neg46、swap45、rot29、rev17、Answer5，计数不是按操作暴露次数标准化的错误率。

## formal-L2-0009

STEP正确、NAME数字首错的首个题号。

输入：`4 6 1 0`；计划：`black → black`。

NAME原始输出（numeric）：
```text
black:
inc 5 7 2 1
swap 7 5 2 1
black:
inc 8 6 3 1
swap 6 8 3 1
Answer: 6 8 3 1
```

正确轨迹：
```text
black:
inc 5 7 2 1
swap 7 5 2 1
black:
inc 8 6 3 2
swap 6 8 3 2
Answer: 6 8 3 2
```

同题STEP原始输出（none）：
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

STEP正确、NAME工具/顺序首错的首个题号。

输入：`6 3 6 6`；计划：`gold → green`。

NAME原始输出（tool_or_order）：
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

正确轨迹：
```text
gold:
inc 7 4 7 7
rev 7 7 4 7
green:
rot 7 4 7 7
rot 4 7 7 7
Answer: 4 7 7 7
```

同题STEP原始输出（none）：
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

NAME数字首错且包含neg的首个题号；两组均错。

输入：`3 2 5 2`；计划：`white → gray`。

NAME原始输出（numeric）：
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

正确轨迹：
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

同题STEP原始输出（numeric）：
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

NAME正确、STEP工具/顺序首错的首个题号。

输入：`0 1 2 3`；计划：`black → green`。

NAME原始输出（none）：
```text
black:
inc 1 2 3 4
swap 2 1 3 4
green:
rot 1 3 4 2
rot 3 4 2 1
Answer: 3 4 2 1
```

正确轨迹：
```text
black:
inc 1 2 3 4
swap 2 1 3 4
green:
rot 1 3 4 2
rot 3 4 2 1
Answer: 3 4 2 1
```

同题STEP原始输出（tool_or_order）：
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

## 解释边界

可观测现象：写对工具标题仍可能写错数字、遗漏/增加原始操作；有些题NAME改善展开，有些题NAME退化。当前结果更支持“操作展开改善不足以抵消数字错误”这一输出层面判断，不能由案例断言注意力被分散、名称语义干扰或某个内部机制。原始NAME与STEP输出SHA分别为：
8e1a97c61311d0ade5b9308aac2500414dd9bd23fee084a500ff5109f8959e67
171d7e8bcf7e300e6e8842723712f58b993af44885790c334ddeee13a17004f0
