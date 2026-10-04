# 14b-L6：错误与标题核验

以下只解释已保存输出，不改变严格主评分。互斥归类按Answer数量、未知行、操作序列、数字步骤、仅最终Answer的固定优先顺序进行；不是按时间定位首错。原始可重叠错误标志保存在analysis/results.json。

| 条件/seed | 失败/512 | Answer数量 | 未知行 | 操作序列 | 数字步骤 | 仅最终Answer | 仅额外Trace标题 | 其他标题问题 | 截断 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| STEP/base | 497 | 6 | 3 | 355 | 131 | 2 | 0 | 121 | 0 |
| STEP/301 | 491 | 5 | 5 | 345 | 133 | 3 | 0 | 133 | 0 |
| STEP/302 | 489 | 6 | 3 | 354 | 123 | 3 | 0 | 119 | 0 |
| STEP/303 | 486 | 6 | 3 | 338 | 134 | 5 | 0 | 113 | 0 |
| NAME/base | 483 | 1 | 5 | 174 | 302 | 1 | 15 | 117 | 0 |
| NAME/301 | 363 | 1 | 1 | 122 | 233 | 6 | 13 | 92 | 0 |
| NAME/302 | 357 | 1 | 3 | 134 | 214 | 5 | 11 | 94 | 0 |
| NAME/303 | 221 | 0 | 0 | 77 | 138 | 6 | 96 | 44 | 0 |

base为原始模型step0，其余为对应seed的step100。额外Trace标题可能与严格成功同时出现；它不代表新增工具调用。操作序列不匹配涵盖原始操作遗漏、增加、替换和顺序改变，不能直接反推遗漏了几次高层工具调用。EOS只说明主动结束，不保证执行完整。互斥优先级归类存在遮蔽：操作序列改善后，更多失败会落入数字错误类别；不能仅凭该类别计数增加就判断数字计算变差，应同时查看主报告中的可重叠数字错误标志。

案例按每个条件/seed/错误类别的最小题目ID选取，展示原始与标准轨迹；类别频率以上表为准。

## STEP seed301 L6-test-00000：operation_sequence

严格正确=0；标题合规=1；输入=[8, 0, 1, 7]；工具索引=[2, 3, 7, 6, 3, 6]。

实际输出：
```text
step:
rot 0 1 7 8
rot 1 7 8 0
inc 2 8 9 1
step:
inc 3 9 0 2
rev 2 0 9 3
step:
rot 0 9 3 2
rot 1 3 2 0
inc 2 4 3 1
step:
inc 3 5 4 2
neg 7 6 7 9
inc 8 7 8 0
step:
inc 9 8 9 1
rev 1 9 8 9
step:
inc 2 0 9 0
neg 8 1 9 1
inc 9 2 0 2
Answer: 9 2 0 2
```

标准轨迹：
```text
step:
rot 0 1 7 8
rot 1 7 8 0
step:
inc 2 8 9 1
rev 1 9 8 2
step:
rot 9 8 2 1
rot 8 2 1 9
inc 9 3 2 0
step:
inc 0 4 3 1
neg 0 6 7 9
inc 1 7 8 0
step:
inc 2 8 9 1
rev 1 9 8 2
step:
inc 2 0 9 3
neg 8 0 1 7
inc 9 1 2 8
Answer: 9 1 2 8

```

## STEP seed301 L6-test-00004：numeric_step

严格正确=0；标题合规=1；输入=[4, 1, 1, 1]；工具索引=[8, 3, 6, 6, 5, 0]。

实际输出：
```text
step:
inc 5 2 2 2
inc 6 3 3 3
inc 7 4 4 4
step:
inc 7 4 4 4
rev 4 4 4 7
step:
inc 4 5 5 8
neg 4 5 5 2
inc 5 6 6 3
step:
inc 5 6 6 3
neg 5 6 6 4
inc 6 7 7 5
step:
inc 6 7 7 5
swap 7 6 7 5
step:
rot 6 7 5 7
inc 7 8 6 8
Answer: 7 8 6 8
```

标准轨迹：
```text
step:
inc 5 2 2 2
inc 6 3 3 3
inc 7 4 4 4
step:
inc 8 5 5 5
rev 5 5 5 8
step:
inc 6 6 6 9
neg 4 4 4 1
inc 5 5 5 2
step:
inc 6 6 6 3
neg 4 4 4 7
inc 5 5 5 8
step:
inc 6 6 6 9
swap 6 6 6 9
step:
rot 6 6 9 6
inc 7 7 0 7
Answer: 7 7 0 7

```

## STEP seed301 L6-test-00018：missing_or_multiple_Answer

严格正确=0；标题合规=1；输入=[9, 5, 8, 9]；工具索引=[8, 1, 3, 3, 7, 0]。

实际输出：
```text
step:
inc 0 6 9 0
inc 1 7 0 1
inc 2 8 1 2
Answer: 2 8 1 2
step:
inc 3 9 2 3
inc 4 0 3 4
inc 5 1 4 5
Answer: 5 1 4 5
step:
rev 5 4 1 5
rot 4 1 5 5
inc 5 2 6 6
Answer: 5 2 6 6
step:
inc 6 3 7 7
rev 7 7 3 6
Answer: 7 7 3 6
step:
rot 7 3 6 7
rot 3 6 7 7
inc 4 7 8 8
Answer: 4 7 8 8
step:
rot 7 8 8 4
inc 8 9 9 5
Answer: 8 9 9 5
Answer: 8 9 9 5
```

标准轨迹：
```text
step:
inc 0 6 9 0
inc 1 7 0 1
inc 2 8 1 2
step:
rev 2 1 8 2
rot 1 8 2 2
inc 2 9 3 3
step:
inc 3 0 4 4
rev 4 4 0 3
step:
inc 5 5 1 4
rev 4 1 5 5
step:
rot 1 5 5 4
rot 5 5 4 1
inc 6 6 5 2
step:
rot 6 5 2 6
inc 7 6 3 7
Answer: 7 6 3 7

```

## STEP seed301 L6-test-00191：unrecognized_extra_lines

严格正确=0；标题合规=0；输入=[5, 9, 8, 3]；工具索引=[2, 6, 4, 2, 7, 5]。

实际输出：
```text
step:
rot 9 8 3 5
rot 8 3 5 9
inc 9 4 6 0
step:
inc 0 5 7 1
neg 0 5 7 1
inc 1 6 8 2
step:
rot 6 8 2 1
inc 7 9 3 2
swap 9 7 8 2
step:
rot 9 8 2 7
rot 8 2 7 9
inc 9 3 8 0
step:
rot 3 8 0 9
rot 8 0 9 3
inc 9 1 0 4
black
inc 0 2 1 5
swap 2 0 1 5
Answer: 2 0 1 5
```

标准轨迹：
```text
step:
rot 9 8 3 5
rot 8 3 5 9
step:
inc 9 4 6 0
neg 1 6 4 0
inc 2 7 5 1
step:
rot 7 5 1 2
inc 8 6 2 3
swap 6 8 2 3
step:
rot 8 2 3 6
rot 2 3 6 8
step:
rot 3 6 8 2
rot 6 8 2 3
inc 7 9 3 4
step:
inc 8 0 4 5
swap 0 8 4 5
Answer: 0 8 4 5

```

## STEP seed301 L6-test-00285：final_Answer_only

严格正确=0；标题合规=1；输入=[4, 4, 6, 1]；工具索引=[7, 1, 8, 3, 6, 5]。

实际输出：
```text
step:
rot 4 6 1 4
rot 6 1 4 4
inc 7 2 5 5
step:
rev 5 5 2 7
rot 5 2 7 5
inc 6 3 8 6
step:
inc 7 4 9 7
inc 8 5 0 8
inc 9 6 1 9
step:
inc 0 7 2 0
rev 0 2 7 0
step:
inc 1 3 8 1
neg 9 7 2 9
inc 0 8 3 0
step:
inc 1 9 4 1
swap 9 1 4 1
Answer: 1 4 1 9
```

标准轨迹：
```text
step:
rot 4 6 1 4
rot 6 1 4 4
inc 7 2 5 5
step:
rev 5 5 2 7
rot 5 2 7 5
inc 6 3 8 6
step:
inc 7 4 9 7
inc 8 5 0 8
inc 9 6 1 9
step:
inc 0 7 2 0
rev 0 2 7 0
step:
inc 1 3 8 1
neg 9 7 2 9
inc 0 8 3 0
step:
inc 1 9 4 1
swap 9 1 4 1
Answer: 9 1 4 1

```

## STEP seed302 L6-test-00000：operation_sequence

严格正确=0；标题合规=1；输入=[8, 0, 1, 7]；工具索引=[2, 3, 7, 6, 3, 6]。

实际输出：
```text
step:
rot 0 1 7 8
rot 1 7 8 0
inc 2 8 9 1
step:
inc 3 9 0 2
rev 2 0 9 3
step:
rot 0 9 3 2
rot 1 3 2 0
inc 2 4 3 1
step:
inc 3 5 4 2
rev 2 4 5 3
step:
rot 4 5 3 2
rot 5 3 2 4
inc 6 4 3 5
step:
inc 7 5 4 6
neg 3 6 7 4
inc 4 7 8 5
Answer: 4 7 8 5
```

标准轨迹：
```text
step:
rot 0 1 7 8
rot 1 7 8 0
step:
inc 2 8 9 1
rev 1 9 8 2
step:
rot 9 8 2 1
rot 8 2 1 9
inc 9 3 2 0
step:
inc 0 4 3 1
neg 0 6 7 9
inc 1 7 8 0
step:
inc 2 8 9 1
rev 1 9 8 2
step:
inc 2 0 9 3
neg 8 0 1 7
inc 9 1 2 8
Answer: 9 1 2 8

```

## STEP seed302 L6-test-00004：numeric_step

严格正确=0；标题合规=1；输入=[4, 1, 1, 1]；工具索引=[8, 3, 6, 6, 5, 0]。

实际输出：
```text
step:
inc 5 2 2 2
inc 6 3 3 3
inc 7 4 4 4
step:
inc 7 4 4 4
rev 4 4 4 7
step:
inc 4 5 5 8
neg 4 5 5 2
inc 5 6 6 3
step:
inc 5 6 6 3
neg 5 6 6 4
inc 6 7 7 5
step:
inc 6 7 7 5
swap 7 6 7 5
step:
rot 6 7 5 7
inc 7 8 6 8
Answer: 7 8 6 8
```

标准轨迹：
```text
step:
inc 5 2 2 2
inc 6 3 3 3
inc 7 4 4 4
step:
inc 8 5 5 5
rev 5 5 5 8
step:
inc 6 6 6 9
neg 4 4 4 1
inc 5 5 5 2
step:
inc 6 6 6 3
neg 4 4 4 7
inc 5 5 5 8
step:
inc 6 6 6 9
swap 6 6 6 9
step:
rot 6 6 9 6
inc 7 7 0 7
Answer: 7 7 0 7

```

## STEP seed302 L6-test-00073：missing_or_multiple_Answer

严格正确=0；标题合规=1；输入=[8, 1, 4, 3]；工具索引=[8, 5, 4, 5, 7, 1]。

实际输出：
```text
step:
inc 9 2 5 4
inc 0 3 6 5
inc 1 4 7 6
Answer: 1 4 7 6
step:
inc 2 5 8 7
inc 3 6 9 8
inc 4 7 0 9
Answer: 4 7 0 9
step:
rot 7 0 9 4
inc 8 1 0 5
swap 1 8 0 5
Answer: 1 8 0 5
step:
inc 2 9 1 6
swap 9 2 1 6
Answer: 9 2 1 6
step:
rot 2 1 6 9
rot 1 6 9 2
inc 2 7 0 3
Answer: 2 7 0 3
step:
rev 3 0 7 2
rot 0 7 2 3
inc 1 8 3 4
Answer: 1 8 3 4
```

标准轨迹：
```text
step:
inc 9 2 5 4
inc 0 3 6 5
inc 1 4 7 6
step:
inc 2 5 8 7
swap 5 2 8 7
step:
rot 2 8 7 5
inc 3 9 8 6
swap 9 3 8 6
step:
inc 0 4 9 7
swap 4 0 9 7
step:
rot 0 9 7 4
rot 9 7 4 0
inc 0 8 5 1
step:
rev 1 5 8 0
rot 5 8 0 1
inc 6 9 1 2
Answer: 6 9 1 2

```

## STEP seed302 L6-test-00111：final_Answer_only

严格正确=0；标题合规=1；输入=[4, 0, 3, 9]；工具索引=[8, 4, 0, 6, 5, 3]。

实际输出：
```text
step:
inc 5 1 4 0
inc 6 2 5 1
inc 7 3 6 2
step:
rot 3 6 2 7
inc 4 7 3 8
swap 7 4 3 8
step:
rot 4 3 8 7
inc 5 4 9 8
step:
inc 6 5 0 9
neg 4 5 0 1
inc 5 6 1 2
step:
inc 6 7 2 3
swap 7 6 2 3
step:
inc 8 7 3 4
rev 4 3 7 8
Answer: 8 3 7 4
```

标准轨迹：
```text
step:
inc 5 1 4 0
inc 6 2 5 1
inc 7 3 6 2
step:
rot 3 6 2 7
inc 4 7 3 8
swap 7 4 3 8
step:
rot 4 3 8 7
inc 5 4 9 8
step:
inc 6 5 0 9
neg 4 5 0 1
inc 5 6 1 2
step:
inc 6 7 2 3
swap 7 6 2 3
step:
inc 8 7 3 4
rev 4 3 7 8
Answer: 4 3 7 8

```

## STEP seed302 L6-test-00196：unrecognized_extra_lines

严格正确=0；标题合规=1；输入=[0, 1, 1, 1]；工具索引=[2, 1, 7, 0, 3, 8]。

实际输出：
```text
step:
rot 1 1 1 0
rot 1 1 0 1
1 1 0 1
step:
rev 1 0 1 1
rot 0 1 1 1
inc 1 2 2 2
1 2 2 2
step:
rot 2 2 2 1
rot 2 2 1 2
inc 3 3 2 3
3 3 2 3
step:
rot 3 2 3 3
inc 4 3 4 4
swap 3 4 3 4
3 4 3 4
step:
inc 4 5 4 5
rev 5 4 4 5
4 5 4 5
step:
inc 5 6 5 6
inc 6 7 6 7
inc 7 8 7 8
7 8 7 8
Answer: 7 8 7 8
```

标准轨迹：
```text
step:
rot 1 1 1 0
rot 1 1 0 1
step:
rev 1 0 1 1
rot 0 1 1 1
inc 1 2 2 2
step:
rot 2 2 2 1
rot 2 2 1 2
inc 3 3 2 3
step:
rot 3 2 3 3
inc 4 3 4 4
step:
inc 5 4 5 5
rev 5 5 4 5
step:
inc 6 6 5 6
inc 7 7 6 7
inc 8 8 7 8
Answer: 8 8 7 8

```

## STEP seed303 L6-test-00000：operation_sequence

严格正确=0；标题合规=1；输入=[8, 0, 1, 7]；工具索引=[2, 3, 7, 6, 3, 6]。

实际输出：
```text
step:
rot 0 1 7 8
rot 1 7 8 0
inc 2 8 9 1
step:
inc 3 9 0 2
rev 2 0 9 3
step:
rot 0 9 3 2
rot 1 3 2 0
inc 2 4 3 1
step:
inc 3 5 4 2
rev 2 4 5 3
step:
rot 4 5 3 2
rot 5 3 2 4
inc 6 4 3 5
step:
inc 7 5 4 6
neg 3 6 7 4
inc 4 7 8 5
Answer: 4 7 8 5
```

标准轨迹：
```text
step:
rot 0 1 7 8
rot 1 7 8 0
step:
inc 2 8 9 1
rev 1 9 8 2
step:
rot 9 8 2 1
rot 8 2 1 9
inc 9 3 2 0
step:
inc 0 4 3 1
neg 0 6 7 9
inc 1 7 8 0
step:
inc 2 8 9 1
rev 1 9 8 2
step:
inc 2 0 9 3
neg 8 0 1 7
inc 9 1 2 8
Answer: 9 1 2 8

```

## STEP seed303 L6-test-00004：numeric_step

严格正确=0；标题合规=1；输入=[4, 1, 1, 1]；工具索引=[8, 3, 6, 6, 5, 0]。

实际输出：
```text
step:
inc 5 2 2 2
inc 6 3 3 3
inc 7 4 4 4
step:
inc 7 4 4 4
rev 4 4 4 7
step:
inc 4 5 5 8
neg 4 5 5 2
inc 5 6 6 3
step:
inc 5 6 6 3
neg 5 6 6 4
inc 6 7 7 5
step:
inc 6 7 7 5
swap 7 6 7 5
step:
rot 6 7 5 7
inc 7 8 6 8
Answer: 7 8 6 8
```

标准轨迹：
```text
step:
inc 5 2 2 2
inc 6 3 3 3
inc 7 4 4 4
step:
inc 8 5 5 5
rev 5 5 5 8
step:
inc 6 6 6 9
neg 4 4 4 1
inc 5 5 5 2
step:
inc 6 6 6 3
neg 4 4 4 7
inc 5 5 5 8
step:
inc 6 6 6 9
swap 6 6 6 9
step:
rot 6 6 9 6
inc 7 7 0 7
Answer: 7 7 0 7

```

## STEP seed303 L6-test-00018：missing_or_multiple_Answer

严格正确=0；标题合规=1；输入=[9, 5, 8, 9]；工具索引=[8, 1, 3, 3, 7, 0]。

实际输出：
```text
step:
inc 0 6 9 0
inc 1 7 0 1
inc 2 8 1 2
Answer: 2 8 1 2
step:
inc 3 9 2 3
inc 4 0 3 4
inc 5 1 4 5
Answer: 5 1 4 5
step:
rev 5 4 1 5
rot 4 1 5 5
inc 5 2 6 6
Answer: 5 2 6 6
step:
inc 6 3 7 7
rev 7 7 3 6
Answer: 7 7 3 6
step:
rot 7 3 6 7
rot 3 6 7 7
inc 4 7 8 8
Answer: 4 7 8 8
step:
rot 7 8 8 4
inc 8 9 9 5
Answer: 8 9 9 5
Answer: 8 9 9 5
```

标准轨迹：
```text
step:
inc 0 6 9 0
inc 1 7 0 1
inc 2 8 1 2
step:
rev 2 1 8 2
rot 1 8 2 2
inc 2 9 3 3
step:
inc 3 0 4 4
rev 4 4 0 3
step:
inc 5 5 1 4
rev 4 1 5 5
step:
rot 1 5 5 4
rot 5 5 4 1
inc 6 6 5 2
step:
rot 6 5 2 6
inc 7 6 3 7
Answer: 7 6 3 7

```

## STEP seed303 L6-test-00111：final_Answer_only

严格正确=0；标题合规=1；输入=[4, 0, 3, 9]；工具索引=[8, 4, 0, 6, 5, 3]。

实际输出：
```text
step:
inc 5 1 4 0
inc 6 2 5 1
inc 7 3 6 2
step:
rot 3 6 2 7
inc 4 7 3 8
swap 7 4 3 8
step:
rot 4 3 8 7
inc 5 4 9 8
step:
inc 6 5 0 9
neg 4 5 0 1
inc 5 6 1 2
step:
inc 6 7 2 3
swap 7 6 2 3
step:
inc 8 7 3 4
rev 4 3 7 8
Answer: 8 7 3 4
```

标准轨迹：
```text
step:
inc 5 1 4 0
inc 6 2 5 1
inc 7 3 6 2
step:
rot 3 6 2 7
inc 4 7 3 8
swap 7 4 3 8
step:
rot 4 3 8 7
inc 5 4 9 8
step:
inc 6 5 0 9
neg 4 5 0 1
inc 5 6 1 2
step:
inc 6 7 2 3
swap 7 6 2 3
step:
inc 8 7 3 4
rev 4 3 7 8
Answer: 4 3 7 8

```

## STEP seed303 L6-test-00121：unrecognized_extra_lines

严格正确=0；标题合规=1；输入=[3, 1, 3, 4]；工具索引=[3, 2, 7, 0, 5, 7]。

实际输出：
```text
step:
inc 4 2 4 5
rev 5 4 2 4
step:
rot 4 2 4 5
rot 2 4 5 4
step:
rot 4 5 4 2
rot 5 4 2 4
inc 6 5 3 5
step:
rot 5 3 5 6
inc 6 4 6 7
step:
inc 7 5 7 8
swap 5 7 7 8
step:
rot 7 7 8 5
inc 8 8 9 6
gray 7 8 9 6
Answer: 7 8 9 6
```

标准轨迹：
```text
step:
inc 4 2 4 5
rev 5 4 2 4
step:
rot 4 2 4 5
rot 2 4 5 4
step:
rot 4 5 4 2
rot 5 4 2 4
inc 6 5 3 5
step:
rot 5 3 5 6
inc 6 4 6 7
step:
inc 7 5 7 8
swap 5 7 7 8
step:
rot 7 7 8 5
rot 7 8 5 7
inc 8 9 6 8
Answer: 8 9 6 8

```

## NAME seed301 L6-test-00000：numeric_step

严格正确=0；标题合规=1；输入=[8, 0, 1, 7]；工具索引=[2, 3, 7, 6, 3, 6]。

实际输出：
```text
green:
rot 0 1 7 8
rot 1 7 8 0
gold:
inc 2 8 9 1
rev 1 9 8 2
gray:
rot 9 8 2 1
rot 8 2 1 9
inc 9 3 2 0
white:
inc 0 4 3 1
neg 0 6 7 9
inc 1 7 8 0
gold:
inc 2 8 9 1
rev 1 9 8 2
white:
inc 2 0 9 3
neg 2 9 1 7
inc 3 0 2 8
Answer: 3 0 2 8
```

标准轨迹：
```text
green:
rot 0 1 7 8
rot 1 7 8 0
gold:
inc 2 8 9 1
rev 1 9 8 2
gray:
rot 9 8 2 1
rot 8 2 1 9
inc 9 3 2 0
white:
inc 0 4 3 1
neg 0 6 7 9
inc 1 7 8 0
gold:
inc 2 8 9 1
rev 1 9 8 2
white:
inc 2 0 9 3
neg 8 0 1 7
inc 9 1 2 8
Answer: 9 1 2 8

```

## NAME seed301 L6-test-00001：final_Answer_only

严格正确=0；标题合规=1；输入=[7, 0, 0, 1]；工具索引=[3, 1, 7, 0, 3, 5]。

实际输出：
```text
gold:
inc 8 1 1 2
rev 2 1 1 8
blue:
rev 8 1 1 2
rot 1 1 2 8
inc 2 2 3 9
gray:
rot 2 3 9 2
rot 3 9 2 2
inc 4 0 3 3
red:
rot 0 3 3 4
inc 1 4 4 5
gold:
inc 2 5 5 6
rev 6 5 5 2
black:
inc 7 6 6 3
swap 6 7 6 3
Answer: 7 6 6 3
```

标准轨迹：
```text
gold:
inc 8 1 1 2
rev 2 1 1 8
blue:
rev 8 1 1 2
rot 1 1 2 8
inc 2 2 3 9
gray:
rot 2 3 9 2
rot 3 9 2 2
inc 4 0 3 3
red:
rot 0 3 3 4
inc 1 4 4 5
gold:
inc 2 5 5 6
rev 6 5 5 2
black:
inc 7 6 6 3
swap 6 7 6 3
Answer: 6 7 6 3

```

## NAME seed301 L6-test-00003：operation_sequence

严格正确=0；标题合规=1；输入=[7, 7, 7, 5]；工具索引=[7, 4, 1, 2, 2, 2]。

实际输出：
```text
gray:
rot 7 7 5 7
rot 7 5 7 7
inc 8 6 8 8
pink:
rot 6 8 8 8
inc 7 9 9 9
swap 9 7 9 9
blue:
rev 9 9 9 7
rot 9 9 7 9
inc 0 0 8 0
green:
rot 0 8 0 0
inc 1 9 1 1
green:
rot 9 1 1 1
inc 0 2 2 2
green:
rot 2 2 2 0
inc 3 3 3 1
Answer: 3 3 3 1
```

标准轨迹：
```text
gray:
rot 7 7 5 7
rot 7 5 7 7
inc 8 6 8 8
pink:
rot 6 8 8 8
inc 7 9 9 9
swap 9 7 9 9
blue:
rev 9 9 7 9
rot 9 7 9 9
inc 0 8 0 0
green:
rot 8 0 0 0
rot 0 0 0 8
green:
rot 0 0 8 0
rot 0 8 0 0
green:
rot 8 0 0 0
rot 0 0 0 8
Answer: 0 0 0 8

```

## NAME seed301 L6-test-00043：extra_Trace_heading_only

严格正确=1；标题合规=0；输入=[9, 7, 3, 2]；工具索引=[8, 3, 1, 1, 3, 8]。

实际输出：
```text
Trace:
brown:
inc 0 8 4 3
inc 1 9 5 4
inc 2 0 6 5
gold:
inc 3 1 7 6
rev 6 7 1 3
blue:
rev 3 1 7 6
rot 1 7 6 3
inc 2 8 7 4
blue:
rev 4 7 8 2
rot 7 8 2 4
inc 8 9 3 5
gold:
inc 9 0 4 6
rev 6 4 0 9
brown:
inc 7 5 1 0
inc 8 6 2 1
inc 9 7 3 2
Answer: 9 7 3 2
```

标准轨迹：
```text
brown:
inc 0 8 4 3
inc 1 9 5 4
inc 2 0 6 5
gold:
inc 3 1 7 6
rev 6 7 1 3
blue:
rev 3 1 7 6
rot 1 7 6 3
inc 2 8 7 4
blue:
rev 4 7 8 2
rot 7 8 2 4
inc 8 9 3 5
gold:
inc 9 0 4 6
rev 6 4 0 9
brown:
inc 7 5 1 0
inc 8 6 2 1
inc 9 7 3 2
Answer: 9 7 3 2

```

## NAME seed301 L6-test-00179：unrecognized_extra_lines

严格正确=0；标题合规=0；输入=[9, 4, 1, 8]；工具索引=[5, 6, 1, 5, 3, 5]。

实际输出：
```text
black:
inc 0 5 2 9
swap 5 0 2 9
white:
inc 6 1 3 0
neg 4 9 7 10
inc 5 0 8 1
blue:
rev 1 8 0 5
rot 8 0 5 1
inc 9 1 6 2
black:
inc 0 2 7 3
swap 2 0 7 3
white:
inc 3 1 8 4
neg 7 9 2 5
inc 8 0 3 6
blue:
rev 6 3 0 8
rot 3 0 8 6
inc 4 1 9 7
gold:
inc 5 2 0 8
rev 8 0 2 5
black:
inc 9 3 3 6
swap 3 9 3 6
Answer: 3 9 3 6
```

标准轨迹：
```text
black:
inc 0 5 2 9
swap 5 0 2 9
white:
inc 6 1 3 0
neg 4 9 7 0
inc 5 0 8 1
blue:
rev 1 8 0 5
rot 8 0 5 1
inc 9 1 6 2
black:
inc 0 2 7 3
swap 2 0 7 3
gold:
inc 3 1 8 4
rev 4 8 1 3
black:
inc 5 9 2 4
swap 9 5 2 4
Answer: 9 5 2 4

```

## NAME seed301 L6-test-00461：missing_or_multiple_Answer

严格正确=0；标题合规=1；输入=[5, 8, 8, 6]；工具索引=[8, 8, 7, 7, 1, 2]。

实际输出：
```text
brown:
inc 6 9 9 7
inc 7 0 0 8
inc 8 1 1 9
Answer: 8 1 1 9
brown:
inc 9 2 2 0
inc 0 3 3 1
inc 1 4 4 2
Answer: 1 4 4 2
gray:
rot 4 4 2 1
rot 4 2 1 4
inc 5 3 3 5
Answer: 5 3 3 5
gray:
rot 3 3 5 5
rot 3 5 5 3
inc 4 6 6 4
Answer: 4 6 6 4
blue:
rev 4 6 6 4
rot 6 6 4 4
inc 7 7 5 5
Answer: 7 7 5 5
green:
rot 7 5 5 7
rot 5 5 7 7
Answer: 5 5 7 7
Answer: 5 5 7 7
```

标准轨迹：
```text
brown:
inc 6 9 9 7
inc 7 0 0 8
inc 8 1 1 9
brown:
inc 9 2 2 0
inc 0 3 3 1
inc 1 4 4 2
gray:
rot 4 4 2 1
rot 4 2 1 4
inc 5 3 2 5
gray:
rot 3 2 5 5
rot 2 5 5 3
inc 3 6 6 4
blue:
rev 4 6 6 3
rot 6 6 3 4
inc 7 7 4 5
green:
rot 7 4 5 7
rot 4 5 7 7
Answer: 4 5 7 7

```

## NAME seed302 L6-test-00000：numeric_step

严格正确=0；标题合规=1；输入=[8, 0, 1, 7]；工具索引=[2, 3, 7, 6, 3, 6]。

实际输出：
```text
green:
rot 0 1 7 8
rot 1 7 8 0
gold:
inc 2 8 9 1
rev 1 9 8 2
gray:
rot 9 8 2 1
rot 8 2 1 9
inc 9 3 2 0
white:
inc 0 4 3 1
neg 0 6 7 9
inc 1 7 8 0
gold:
inc 2 8 9 1
rev 1 9 8 2
white:
inc 2 0 9 3
neg 2 9 1 7
inc 3 0 2 8
Answer: 3 0 2 8
```

标准轨迹：
```text
green:
rot 0 1 7 8
rot 1 7 8 0
gold:
inc 2 8 9 1
rev 1 9 8 2
gray:
rot 9 8 2 1
rot 8 2 1 9
inc 9 3 2 0
white:
inc 0 4 3 1
neg 0 6 7 9
inc 1 7 8 0
gold:
inc 2 8 9 1
rev 1 9 8 2
white:
inc 2 0 9 3
neg 8 0 1 7
inc 9 1 2 8
Answer: 9 1 2 8

```

## NAME seed302 L6-test-00003：operation_sequence

严格正确=0；标题合规=1；输入=[7, 7, 7, 5]；工具索引=[7, 4, 1, 2, 2, 2]。

实际输出：
```text
gray:
rot 7 7 5 7
rot 7 5 7 7
inc 8 6 8 8
pink:
rot 6 8 8 8
inc 7 9 9 9
swap 9 7 9 9
blue:
rev 9 9 9 7
rot 9 9 7 9
inc 0 0 8 0
green:
rot 0 8 0 0
inc 1 9 1 1
green:
rot 9 1 1 1
inc 0 2 2 2
green:
rot 2 2 2 0
inc 3 3 3 1
Answer: 3 3 3 1
```

标准轨迹：
```text
gray:
rot 7 7 5 7
rot 7 5 7 7
inc 8 6 8 8
pink:
rot 6 8 8 8
inc 7 9 9 9
swap 9 7 9 9
blue:
rev 9 9 7 9
rot 9 7 9 9
inc 0 8 0 0
green:
rot 8 0 0 0
rot 0 0 0 8
green:
rot 0 0 8 0
rot 0 8 0 0
green:
rot 8 0 0 0
rot 0 0 0 8
Answer: 0 0 0 8

```

## NAME seed302 L6-test-00043：extra_Trace_heading_only

严格正确=1；标题合规=0；输入=[9, 7, 3, 2]；工具索引=[8, 3, 1, 1, 3, 8]。

实际输出：
```text
Trace:
brown:
inc 0 8 4 3
inc 1 9 5 4
inc 2 0 6 5
gold:
inc 3 1 7 6
rev 6 7 1 3
blue:
rev 3 1 7 6
rot 1 7 6 3
inc 2 8 7 4
blue:
rev 4 7 8 2
rot 7 8 2 4
inc 8 9 3 5
gold:
inc 9 0 4 6
rev 6 4 0 9
brown:
inc 7 5 1 0
inc 8 6 2 1
inc 9 7 3 2
Answer: 9 7 3 2
```

标准轨迹：
```text
brown:
inc 0 8 4 3
inc 1 9 5 4
inc 2 0 6 5
gold:
inc 3 1 7 6
rev 6 7 1 3
blue:
rev 3 1 7 6
rot 1 7 6 3
inc 2 8 7 4
blue:
rev 4 7 8 2
rot 7 8 2 4
inc 8 9 3 5
gold:
inc 9 0 4 6
rev 6 4 0 9
brown:
inc 7 5 1 0
inc 8 6 2 1
inc 9 7 3 2
Answer: 9 7 3 2

```

## NAME seed302 L6-test-00099：final_Answer_only

严格正确=0；标题合规=1；输入=[4, 8, 5, 3]；工具索引=[0, 3, 2, 1, 3, 5]。

实际输出：
```text
red:
rot 8 5 3 4
inc 9 6 4 5
gold:
inc 0 7 5 6
rev 6 5 7 0
green:
rot 5 7 0 6
rot 7 0 6 5
blue:
rev 5 6 0 7
rot 6 0 7 5
inc 7 1 8 6
gold:
inc 8 2 9 7
rev 7 9 2 8
black:
inc 8 0 3 9
swap 0 8 3 9
Answer: 8 0 3 9
```

标准轨迹：
```text
red:
rot 8 5 3 4
inc 9 6 4 5
gold:
inc 0 7 5 6
rev 6 5 7 0
green:
rot 5 7 0 6
rot 7 0 6 5
blue:
rev 5 6 0 7
rot 6 0 7 5
inc 7 1 8 6
gold:
inc 8 2 9 7
rev 7 9 2 8
black:
inc 8 0 3 9
swap 0 8 3 9
Answer: 0 8 3 9

```

## NAME seed302 L6-test-00179：unrecognized_extra_lines

严格正确=0；标题合规=0；输入=[9, 4, 1, 8]；工具索引=[5, 6, 1, 5, 3, 5]。

实际输出：
```text
black:
inc 0 5 2 9
swap 5 0 2 9
white:
inc 6 1 3 0
neg 4 9 7 10
inc 5 0 8 1
blue:
rev 1 8 0 5
rot 8 0 5 1
inc 9 1 6 2
black:
inc 0 2 7 3
swap 2 0 7 3
white:
inc 3 1 8 4
neg 7 9 2 6
inc 8 0 3 7
blue:
rev 7 3 0 8
rot 3 0 8 7
inc 4 1 9 8
gold:
inc 5 2 0 9
rev 9 0 2 5
black:
inc 0 3 3 6
swap 3 0 3 6
Answer: 3 0 3 6
```

标准轨迹：
```text
black:
inc 0 5 2 9
swap 5 0 2 9
white:
inc 6 1 3 0
neg 4 9 7 0
inc 5 0 8 1
blue:
rev 1 8 0 5
rot 8 0 5 1
inc 9 1 6 2
black:
inc 0 2 7 3
swap 2 0 7 3
gold:
inc 3 1 8 4
rev 4 8 1 3
black:
inc 5 9 2 4
swap 9 5 2 4
Answer: 9 5 2 4

```

## NAME seed302 L6-test-00461：missing_or_multiple_Answer

严格正确=0；标题合规=1；输入=[5, 8, 8, 6]；工具索引=[8, 8, 7, 7, 1, 2]。

实际输出：
```text
brown:
inc 6 9 9 7
inc 7 0 0 8
inc 8 1 1 9
Answer: 8 1 1 9
brown:
inc 9 2 2 0
inc 0 3 3 1
inc 1 4 4 2
Answer: 1 4 4 2
gray:
rot 4 4 2 1
rot 4 2 1 4
inc 5 3 3 5
Answer: 5 3 3 5
gray:
rot 3 3 5 5
rot 3 5 5 3
inc 4 6 6 4
Answer: 4 6 6 4
blue:
rev 4 6 6 4
rot 6 6 4 4
inc 7 7 5 5
Answer: 7 7 5 5
green:
rot 7 5 5 7
rot 5 5 7 7
inc 6 6 8 8
Answer: 6 6 8 8
Answer: 6 6 8 8
```

标准轨迹：
```text
brown:
inc 6 9 9 7
inc 7 0 0 8
inc 8 1 1 9
brown:
inc 9 2 2 0
inc 0 3 3 1
inc 1 4 4 2
gray:
rot 4 4 2 1
rot 4 2 1 4
inc 5 3 2 5
gray:
rot 3 2 5 5
rot 2 5 5 3
inc 3 6 6 4
blue:
rev 4 6 6 3
rot 6 6 3 4
inc 7 7 4 5
green:
rot 7 4 5 7
rot 4 5 7 7
Answer: 4 5 7 7

```

## NAME seed303 L6-test-00000：numeric_step

严格正确=0；标题合规=1；输入=[8, 0, 1, 7]；工具索引=[2, 3, 7, 6, 3, 6]。

实际输出：
```text
green:
rot 0 1 7 8
rot 1 7 8 0
gold:
inc 2 8 9 1
rev 1 9 8 2
gray:
rot 9 8 2 1
rot 8 2 1 9
inc 9 3 2 0
white:
inc 0 4 3 1
neg 0 6 7 9
inc 1 7 8 0
gold:
inc 2 8 9 1
rev 1 9 8 2
white:
inc 2 0 9 3
neg 2 9 1 7
inc 3 0 2 8
Answer: 3 0 2 8
```

标准轨迹：
```text
green:
rot 0 1 7 8
rot 1 7 8 0
gold:
inc 2 8 9 1
rev 1 9 8 2
gray:
rot 9 8 2 1
rot 8 2 1 9
inc 9 3 2 0
white:
inc 0 4 3 1
neg 0 6 7 9
inc 1 7 8 0
gold:
inc 2 8 9 1
rev 1 9 8 2
white:
inc 2 0 9 3
neg 8 0 1 7
inc 9 1 2 8
Answer: 9 1 2 8

```

## NAME seed303 L6-test-00003：operation_sequence

严格正确=0；标题合规=1；输入=[7, 7, 7, 5]；工具索引=[7, 4, 1, 2, 2, 2]。

实际输出：
```text
gray:
rot 7 7 5 7
rot 7 5 7 7
inc 8 6 8 8
pink:
rot 6 8 8 8
inc 7 9 9 9
swap 9 7 9 9
blue:
rev 9 9 9 7
rot 9 9 7 9
inc 0 0 8 0
green:
rot 0 8 0 0
inc 1 9 1 1
green:
rot 9 1 1 1
inc 0 2 2 2
green:
rot 2 2 2 0
inc 3 3 3 1
Answer: 3 3 3 1
```

标准轨迹：
```text
gray:
rot 7 7 5 7
rot 7 5 7 7
inc 8 6 8 8
pink:
rot 6 8 8 8
inc 7 9 9 9
swap 9 7 9 9
blue:
rev 9 9 7 9
rot 9 7 9 9
inc 0 8 0 0
green:
rot 8 0 0 0
rot 0 0 0 8
green:
rot 0 0 8 0
rot 0 8 0 0
green:
rot 8 0 0 0
rot 0 0 0 8
Answer: 0 0 0 8

```

## NAME seed303 L6-test-00021：extra_Trace_heading_only

严格正确=1；标题合规=0；输入=[6, 0, 9, 0]；工具索引=[8, 5, 0, 1, 8, 6]。

实际输出：
```text
Trace:
brown:
inc 7 1 0 1
inc 8 2 1 2
inc 9 3 2 3
black:
inc 0 4 3 4
swap 4 0 3 4
red:
rot 0 3 4 4
inc 1 4 5 5
blue:
rev 5 5 4 1
rot 5 4 1 5
inc 6 5 2 6
brown:
inc 7 6 3 7
inc 8 7 4 8
inc 9 8 5 9
white:
inc 0 9 6 0
neg 0 1 4 0
inc 1 2 5 1
Answer: 1 2 5 1
```

标准轨迹：
```text
brown:
inc 7 1 0 1
inc 8 2 1 2
inc 9 3 2 3
black:
inc 0 4 3 4
swap 4 0 3 4
red:
rot 0 3 4 4
inc 1 4 5 5
blue:
rev 5 5 4 1
rot 5 4 1 5
inc 6 5 2 6
brown:
inc 7 6 3 7
inc 8 7 4 8
inc 9 8 5 9
white:
inc 0 9 6 0
neg 0 1 4 0
inc 1 2 5 1
Answer: 1 2 5 1

```

## NAME seed303 L6-test-00099：final_Answer_only

严格正确=0；标题合规=1；输入=[4, 8, 5, 3]；工具索引=[0, 3, 2, 1, 3, 5]。

实际输出：
```text
red:
rot 8 5 3 4
inc 9 6 4 5
gold:
inc 0 7 5 6
rev 6 5 7 0
green:
rot 5 7 0 6
rot 7 0 6 5
blue:
rev 5 6 0 7
rot 6 0 7 5
inc 7 1 8 6
gold:
inc 8 2 9 7
rev 7 9 2 8
black:
inc 8 0 3 9
swap 0 8 3 9
Answer: 8 0 3 9
```

标准轨迹：
```text
red:
rot 8 5 3 4
inc 9 6 4 5
gold:
inc 0 7 5 6
rev 6 5 7 0
green:
rot 5 7 0 6
rot 7 0 6 5
blue:
rev 5 6 0 7
rot 6 0 7 5
inc 7 1 8 6
gold:
inc 8 2 9 7
rev 7 9 2 8
black:
inc 8 0 3 9
swap 0 8 3 9
Answer: 0 8 3 9

```

