# 14b-L5：错误与标题核验

以下只解释已保存输出，不改变严格主评分。互斥归类按Answer数量、未知行、操作序列、数字步骤、仅最终Answer的固定优先顺序进行；不是按时间定位首错。原始可重叠错误标志保存在analysis/results.json。

| 条件/seed | 失败/512 | Answer数量 | 未知行 | 操作序列 | 数字步骤 | 仅最终Answer | 仅额外Trace标题 | 其他标题问题 | 截断 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| STEP/base | 484 | 11 | 15 | 283 | 171 | 4 | 0 | 19 | 0 |
| STEP/301 | 387 | 16 | 16 | 251 | 100 | 4 | 0 | 18 | 1 |
| STEP/302 | 347 | 2 | 4 | 210 | 124 | 7 | 0 | 12 | 0 |
| STEP/303 | 296 | 0 | 2 | 112 | 179 | 3 | 1 | 15 | 0 |
| NAME/base | 458 | 1 | 1 | 126 | 327 | 3 | 7 | 57 | 0 |
| NAME/301 | 237 | 0 | 0 | 52 | 182 | 3 | 1 | 34 | 0 |
| NAME/302 | 111 | 0 | 0 | 45 | 65 | 1 | 0 | 26 | 0 |
| NAME/303 | 101 | 0 | 0 | 54 | 47 | 0 | 0 | 15 | 0 |

base为原始模型step0，其余为对应seed的step100。额外Trace标题可能与严格成功同时出现；它不代表新增工具调用。操作序列不匹配涵盖原始操作遗漏、增加、替换和顺序改变，不能直接反推遗漏了几次高层工具调用。EOS只说明主动结束，不保证执行完整。互斥优先级归类存在遮蔽：操作序列改善后，更多失败会落入数字错误类别；不能仅凭该类别计数增加就判断数字计算变差，应同时查看主报告中的可重叠数字错误标志。

案例按每个条件/seed/错误类别的最小题目ID选取，展示原始与标准轨迹；类别频率以上表为准。

## STEP seed301 L5-test-00000：numeric_step

严格正确=0；标题合规=1；输入=[1, 1, 7, 7]；工具索引=[1, 2, 1, 1, 5]。

实际输出：
```text
step:
rev 7 7 1 1
rot 7 1 1 7
inc 8 2 2 8
step:
rot 2 2 8 8
rot 2 8 8 2
step:
rev 8 8 2 2
rot 8 2 2 8
inc 9 3 3 9
step:
rev 9 3 3 9
rot 3 3 9 9
inc 4 4 0 0
step:
inc 5 5 1 1
swap 5 5 1 1
Answer: 5 5 1 1
```

标准轨迹：
```text
step:
rev 7 7 1 1
rot 7 1 1 7
inc 8 2 2 8
step:
rot 2 2 8 8
rot 2 8 8 2
step:
rev 2 8 8 2
rot 8 8 2 2
inc 9 9 3 3
step:
rev 3 3 9 9
rot 3 9 9 3
inc 4 0 0 4
step:
inc 5 1 1 5
swap 1 5 1 5
Answer: 1 5 1 5

```

## STEP seed301 L5-test-00001：missing_or_multiple_Answer

严格正确=0；标题合规=1；输入=[3, 3, 3, 3]；工具索引=[5, 4, 2, 7, 7]。

实际输出：
```text
step:
inc 4 4 4 4
swap 4 4 4 4
step:
rot 4 4 4 4
inc 5 5 5 5
swap 5 5 5 5
step:
rot 5 5 5 5
rot 5 5 5 5
step:
rot 5 5 5 5
inc 6 6 6 6
rot 6 6 6 6
inc 7 7 7 7
rot 7 7 7 7
inc 8 8 8 8
rot 8 8 8 8
inc 9 9 9 9
rot 9 9 9 9
inc 0 0 0 0
rot 0 0 0 0
inc 1 1 1 1
rot 1 1 1 1
inc 2 2 2 2
rot 2 2 2 2
inc 3 3 3 3
rot 3 3 3 3
inc 4 4 4 4
rot 4 4 4 4
inc 5 5 5 5
rot 5 5 5 5
inc 6 6 6 6
rot 6 6 6 6
inc 7 7 7 7
rot 7 7 7 7
inc 8 8 8 8
rot 8 8 8 8
inc 9 9 9 9
rot 9 9 9 9
inc 0 0 0 0
rot 0 0 0 0
inc 1 1 1 1
step:
rot 1 1 1 1
rot 1 1 1 1
inc 2 2 2 2
rot 2 2 2 2
inc 3 3 3 3
rot 3 3 3 3
inc 4 4 4 4
rot 4 4 4 4
inc 5 5 5 5
rot 5 5 5 5
inc 6 6 6 6
rot 
```

标准轨迹：
```text
step:
inc 4 4 4 4
swap 4 4 4 4
step:
rot 4 4 4 4
inc 5 5 5 5
swap 5 5 5 5
step:
rot 5 5 5 5
rot 5 5 5 5
step:
rot 5 5 5 5
rot 5 5 5 5
inc 6 6 6 6
step:
rot 6 6 6 6
rot 6 6 6 6
inc 7 7 7 7
Answer: 7 7 7 7

```

## STEP seed301 L5-test-00003：operation_sequence

严格正确=0；标题合规=1；输入=[8, 9, 0, 6]；工具索引=[8, 1, 6, 4, 5]。

实际输出：
```text
step:
inc 9 0 1 7
inc 0 1 2 8
inc 1 2 3 9
inc 2 3 4 0
step:
rev 0 4 3 2
rot 4 3 2 0
inc 5 4 3 1
step:
inc 6 5 4 2
neg 4 5 6 8
inc 5 6 7 9
step:
rot 6 7 9 5
inc 7 8 0 6
swap 8 7 0 6
step:
inc 9 8 1 7
swap 8 9 1 7
Answer: 8 9 1 7
```

标准轨迹：
```text
step:
inc 9 0 1 7
inc 0 1 2 8
inc 1 2 3 9
step:
rev 9 3 2 1
rot 3 2 1 9
inc 4 3 2 0
step:
inc 5 4 3 1
neg 5 6 7 9
inc 6 7 8 0
step:
rot 7 8 0 6
inc 8 9 1 7
swap 9 8 1 7
step:
inc 0 9 2 8
swap 9 0 2 8
Answer: 9 0 2 8

```

## STEP seed301 L5-test-00023：unrecognized_extra_lines

严格正确=0；标题合规=1；输入=[0, 4, 6, 5]；工具索引=[8, 4, 5, 5, 7]。

实际输出：
```text
step:
inc 1 5 7 6
inc 2 6 8 7
inc 3 7 9 8
brown 3 7 9 8
step:
rot 7 9 8 3
inc 8 0 9 4
swap 0 8 9 4
pink 0 8 9 4
step:
inc 1 9 0 5
swap 9 1 0 5
black 9 2 1 6
step:
inc 0 3 2 7
swap 3 0 2 7
black 3 1 0 8
step:
rot 1 0 8 3
rot 0 8 3 1
inc 1 9 4 2
gray 1 9 4 2
Answer: 1 9 4 2
```

标准轨迹：
```text
step:
inc 1 5 7 6
inc 2 6 8 7
inc 3 7 9 8
step:
rot 7 9 8 3
inc 8 0 9 4
swap 0 8 9 4
step:
inc 1 9 0 5
swap 9 1 0 5
step:
inc 0 2 1 6
swap 2 0 1 6
step:
rot 0 1 6 2
rot 1 6 2 0
inc 2 7 3 1
Answer: 2 7 3 1

```

## STEP seed301 L5-test-00105：final_Answer_only

严格正确=0；标题合规=1；输入=[1, 0, 3, 7]；工具索引=[5, 5, 6, 3, 4]。

实际输出：
```text
step:
inc 2 1 4 8
swap 1 2 4 8
step:
inc 2 3 5 9
swap 3 2 5 9
step:
inc 4 3 6 0
neg 6 7 4 0
inc 7 8 5 1
step:
inc 8 9 6 2
rev 2 6 9 8
step:
rot 6 9 8 2
inc 7 0 9 3
swap 0 7 9 3
Answer: 7 0 9 3
```

标准轨迹：
```text
step:
inc 2 1 4 8
swap 1 2 4 8
step:
inc 2 3 5 9
swap 3 2 5 9
step:
inc 4 3 6 0
neg 6 7 4 0
inc 7 8 5 1
step:
inc 8 9 6 2
rev 2 6 9 8
step:
rot 6 9 8 2
inc 7 0 9 3
swap 0 7 9 3
Answer: 0 7 9 3

```

## STEP seed302 L5-test-00000：numeric_step

严格正确=0；标题合规=1；输入=[1, 1, 7, 7]；工具索引=[1, 2, 1, 1, 5]。

实际输出：
```text
step:
rev 7 7 1 1
rot 7 1 1 7
inc 8 2 2 8
step:
rot 2 2 8 8
rot 2 8 8 2
step:
rev 8 8 2 2
rot 8 2 2 8
inc 9 3 3 9
step:
rev 9 3 3 9
rot 3 3 9 9
inc 4 4 0 0
step:
inc 5 5 1 1
swap 5 5 1 1
Answer: 5 5 1 1
```

标准轨迹：
```text
step:
rev 7 7 1 1
rot 7 1 1 7
inc 8 2 2 8
step:
rot 2 2 8 8
rot 2 8 8 2
step:
rev 2 8 8 2
rot 8 8 2 2
inc 9 9 3 3
step:
rev 3 3 9 9
rot 3 9 9 3
inc 4 0 0 4
step:
inc 5 1 1 5
swap 1 5 1 5
Answer: 1 5 1 5

```

## STEP seed302 L5-test-00001：operation_sequence

严格正确=0；标题合规=1；输入=[3, 3, 3, 3]；工具索引=[5, 4, 2, 7, 7]。

实际输出：
```text
step:
inc 4 4 4 4
swap 4 4 4 4
step:
rot 4 4 4 4
inc 5 5 5 5
swap 5 5 5 5
step:
rot 5 5 5 5
rot 5 5 5 5
step:
rot 5 5 5 5
inc 6 6 6 6
step:
rot 6 6 6 6
inc 7 7 7 7
Answer: 7 7 7 7
```

标准轨迹：
```text
step:
inc 4 4 4 4
swap 4 4 4 4
step:
rot 4 4 4 4
inc 5 5 5 5
swap 5 5 5 5
step:
rot 5 5 5 5
rot 5 5 5 5
step:
rot 5 5 5 5
rot 5 5 5 5
inc 6 6 6 6
step:
rot 6 6 6 6
rot 6 6 6 6
inc 7 7 7 7
Answer: 7 7 7 7

```

## STEP seed302 L5-test-00105：final_Answer_only

严格正确=0；标题合规=1；输入=[1, 0, 3, 7]；工具索引=[5, 5, 6, 3, 4]。

实际输出：
```text
step:
inc 2 1 4 8
swap 1 2 4 8
step:
inc 2 3 5 9
swap 3 2 5 9
step:
inc 4 3 6 0
neg 6 7 4 0
inc 7 8 5 1
step:
inc 8 9 6 2
rev 2 6 9 8
step:
rot 6 9 8 2
inc 7 0 9 3
swap 0 7 9 3
Answer: 7 9 3 0
```

标准轨迹：
```text
step:
inc 2 1 4 8
swap 1 2 4 8
step:
inc 2 3 5 9
swap 3 2 5 9
step:
inc 4 3 6 0
neg 6 7 4 0
inc 7 8 5 1
step:
inc 8 9 6 2
rev 2 6 9 8
step:
rot 6 9 8 2
inc 7 0 9 3
swap 0 7 9 3
Answer: 0 7 9 3

```

## STEP seed302 L5-test-00136：unrecognized_extra_lines

严格正确=0；标题合规=1；输入=[3, 3, 6, 9]；工具索引=[2, 5, 0, 3, 6]。

实际输出：
```text
step:
rot 3 6 9 3
rot 6 9 3 3
3 6 9 3
step:
inc 4 7 0 4
swap 7 4 0 4
7 4 0 4
step:
rot 4 0 4 7
inc 5 1 5 8
5 1 5 8
step:
inc 6 2 6 9
rev 9 6 2 6
9 6 2 6
step:
inc 0 7 3 7
neg 0 7 3 7
inc 1 0 4 8
Answer: 1 0 4 8
```

标准轨迹：
```text
step:
rot 3 6 9 3
rot 6 9 3 3
step:
inc 7 0 4 4
swap 0 7 4 4
step:
rot 7 4 4 0
inc 8 5 5 1
step:
inc 9 6 6 2
rev 2 6 6 9
step:
inc 3 7 7 0
neg 7 3 3 0
inc 8 4 4 1
Answer: 8 4 4 1

```

## STEP seed302 L5-test-00310：missing_or_multiple_Answer

严格正确=0；标题合规=1；输入=[9, 5, 0, 4]；工具索引=[8, 2, 1, 4, 6]。

实际输出：
```text
step:
inc 0 6 1 5
inc 1 7 2 6
inc 2 8 3 7
Answer: 2 8 3 7
step:
rot 8 3 7 2
rot 3 7 2 8
inc 4 8 3 9
Answer: 4 8 3 9
step:
rev 9 3 8 4
rot 3 8 4 9
inc 4 9 5 0
Answer: 4 9 5 0
step:
rot 9 5 0 4
inc 0 6 1 5
swap 6 0 1 5
Answer: 6 0 1 5
step:
inc 7 1 2 6
neg 3 9 8 4
Answer: 3 9 8 4
```

标准轨迹：
```text
step:
inc 0 6 1 5
inc 1 7 2 6
inc 2 8 3 7
step:
rot 8 3 7 2
rot 3 7 2 8
step:
rev 8 2 7 3
rot 2 7 3 8
inc 3 8 4 9
step:
rot 8 4 9 3
inc 9 5 0 4
swap 5 9 0 4
step:
inc 6 0 1 5
neg 4 0 9 5
inc 5 1 0 6
Answer: 5 1 0 6

```

## STEP seed303 L5-test-00000：numeric_step

严格正确=0；标题合规=1；输入=[1, 1, 7, 7]；工具索引=[1, 2, 1, 1, 5]。

实际输出：
```text
step:
rev 7 7 1 1
rot 7 1 1 7
inc 8 2 2 8
step:
rot 2 2 8 8
rot 2 8 8 2
step:
rev 8 8 2 2
rot 8 2 2 8
inc 9 3 3 9
step:
rev 9 3 3 9
rot 3 3 9 9
inc 4 4 0 0
step:
inc 5 5 1 1
swap 5 5 1 1
Answer: 5 5 1 1
```

标准轨迹：
```text
step:
rev 7 7 1 1
rot 7 1 1 7
inc 8 2 2 8
step:
rot 2 2 8 8
rot 2 8 8 2
step:
rev 2 8 8 2
rot 8 8 2 2
inc 9 9 3 3
step:
rev 3 3 9 9
rot 3 9 9 3
inc 4 0 0 4
step:
inc 5 1 1 5
swap 1 5 1 5
Answer: 1 5 1 5

```

## STEP seed303 L5-test-00001：operation_sequence

严格正确=0；标题合规=1；输入=[3, 3, 3, 3]；工具索引=[5, 4, 2, 7, 7]。

实际输出：
```text
step:
inc 4 4 4 4
swap 4 4 4 4
step:
rot 4 4 4 4
inc 5 5 5 5
swap 5 5 5 5
step:
rot 5 5 5 5
rot 5 5 5 5
step:
rot 5 5 5 5
inc 6 6 6 6
step:
rot 6 6 6 6
inc 7 7 7 7
Answer: 7 7 7 7
```

标准轨迹：
```text
step:
inc 4 4 4 4
swap 4 4 4 4
step:
rot 4 4 4 4
inc 5 5 5 5
swap 5 5 5 5
step:
rot 5 5 5 5
rot 5 5 5 5
step:
rot 5 5 5 5
rot 5 5 5 5
inc 6 6 6 6
step:
rot 6 6 6 6
rot 6 6 6 6
inc 7 7 7 7
Answer: 7 7 7 7

```

## STEP seed303 L5-test-00056：unrecognized_extra_lines

严格正确=0；标题合规=1；输入=[8, 9, 5, 6]；工具索引=[4, 6, 8, 4, 8]。

实际输出：
```text
step:
rot 9 5 6 8
inc 0 6 7 9
swap 6 0 7 9
step:
inc 7 1 8 0
neg 3 9 2 10
inc 4 0 3 1
step:
inc 5 1 4 2
inc 6 2 5 3
inc 7 3 6 4
step:
rot 3 6 4 7
inc 4 7 5 8
swap 7 4 5 8
step:
inc 8 5 6 9
inc 9 6 7 0
inc 0 7 8 1
Answer: 0 7 8 1
```

标准轨迹：
```text
step:
rot 9 5 6 8
inc 0 6 7 9
swap 6 0 7 9
step:
inc 7 1 8 0
neg 3 9 2 0
inc 4 0 3 1
step:
inc 5 1 4 2
inc 6 2 5 3
inc 7 3 6 4
step:
rot 3 6 4 7
inc 4 7 5 8
swap 7 4 5 8
step:
inc 8 5 6 9
inc 9 6 7 0
inc 0 7 8 1
Answer: 0 7 8 1

```

## STEP seed303 L5-test-00182：final_Answer_only

严格正确=0；标题合规=1；输入=[4, 5, 4, 4]；工具索引=[7, 3, 5, 6, 5]。

实际输出：
```text
step:
rot 5 4 4 4
rot 4 4 4 5
inc 5 5 5 6
step:
inc 6 6 6 7
rev 7 6 6 6
step:
inc 8 7 7 7
swap 7 8 7 7
step:
inc 8 9 8 8
neg 2 1 2 2
inc 3 2 3 3
step:
inc 4 3 4 4
swap 3 4 4 4
Answer: 4 3 4 4
```

标准轨迹：
```text
step:
rot 5 4 4 4
rot 4 4 4 5
inc 5 5 5 6
step:
inc 6 6 6 7
rev 7 6 6 6
step:
inc 8 7 7 7
swap 7 8 7 7
step:
inc 8 9 8 8
neg 2 1 2 2
inc 3 2 3 3
step:
inc 4 3 4 4
swap 3 4 4 4
Answer: 3 4 4 4

```

## NAME seed301 L5-test-00000：numeric_step

严格正确=0；标题合规=1；输入=[1, 1, 7, 7]；工具索引=[1, 2, 1, 1, 5]。

实际输出：
```text
blue:
rev 7 7 1 1
rot 7 1 1 7
inc 8 2 2 8
green:
rot 2 2 8 8
rot 2 8 8 2
blue:
rev 2 8 8 2
rot 2 8 2 8
inc 3 9 3 9
blue:
rev 9 3 2 8
rot 3 2 8 9
inc 4 3 9 0
black:
inc 5 4 0 1
swap 4 5 0 1
Answer: 4 5 0 1
```

标准轨迹：
```text
blue:
rev 7 7 1 1
rot 7 1 1 7
inc 8 2 2 8
green:
rot 2 2 8 8
rot 2 8 8 2
blue:
rev 2 8 8 2
rot 8 8 2 2
inc 9 9 3 3
blue:
rev 3 3 9 9
rot 3 9 9 3
inc 4 0 0 4
black:
inc 5 1 1 5
swap 1 5 1 5
Answer: 1 5 1 5

```

## NAME seed301 L5-test-00010：operation_sequence

严格正确=0；标题合规=1；输入=[9, 7, 7, 3]；工具索引=[5, 8, 8, 6, 7]。

实际输出：
```text
black:
inc 0 8 8 4
swap 8 0 8 4
brown:
inc 9 9 9 5
brown:
inc 0 0 0 6
white:
inc 1 1 1 7
neg 9 9 9 3
inc 0 0 0 4
gray:
rot 0 0 0 4
rot 0 0 4 0
inc 1 1 5 1
Answer: 1 1 5 1
```

标准轨迹：
```text
black:
inc 0 8 8 4
swap 8 0 8 4
brown:
inc 9 1 9 5
inc 0 2 0 6
inc 1 3 1 7
brown:
inc 2 4 2 8
inc 3 5 3 9
inc 4 6 4 0
white:
inc 5 7 5 1
neg 5 3 5 9
inc 6 4 6 0
gray:
rot 4 6 0 6
rot 6 0 6 4
inc 7 1 7 5
Answer: 7 1 7 5

```

## NAME seed301 L5-test-00105：final_Answer_only

严格正确=0；标题合规=1；输入=[1, 0, 3, 7]；工具索引=[5, 5, 6, 3, 4]。

实际输出：
```text
black:
inc 2 1 4 8
swap 1 2 4 8
black:
inc 2 3 5 9
swap 3 2 5 9
white:
inc 4 3 6 0
neg 6 7 4 0
inc 7 8 5 1
gold:
inc 8 9 6 2
rev 2 6 9 8
pink:
rot 6 9 8 2
inc 7 0 9 3
swap 0 7 9 3
Answer: 7 0 9 3
```

标准轨迹：
```text
black:
inc 2 1 4 8
swap 1 2 4 8
black:
inc 2 3 5 9
swap 3 2 5 9
white:
inc 4 3 6 0
neg 6 7 4 0
inc 7 8 5 1
gold:
inc 8 9 6 2
rev 2 6 9 8
pink:
rot 6 9 8 2
inc 7 0 9 3
swap 0 7 9 3
Answer: 0 7 9 3

```

## NAME seed302 L5-test-00000：numeric_step

严格正确=0；标题合规=1；输入=[1, 1, 7, 7]；工具索引=[1, 2, 1, 1, 5]。

实际输出：
```text
blue:
rev 7 7 1 1
rot 7 1 1 7
inc 8 2 2 8
green:
rot 2 2 8 8
rot 2 8 8 2
blue:
rev 2 8 8 2
rot 2 8 2 2
inc 3 9 3 3
blue:
rev 3 3 9 3
rot 3 9 3 3
inc 4 0 4 4
black:
inc 5 1 5 5
swap 1 5 5 5
Answer: 1 5 5 5
```

标准轨迹：
```text
blue:
rev 7 7 1 1
rot 7 1 1 7
inc 8 2 2 8
green:
rot 2 2 8 8
rot 2 8 8 2
blue:
rev 2 8 8 2
rot 8 8 2 2
inc 9 9 3 3
blue:
rev 3 3 9 9
rot 3 9 9 3
inc 4 0 0 4
black:
inc 5 1 1 5
swap 1 5 1 5
Answer: 1 5 1 5

```

## NAME seed302 L5-test-00016：operation_sequence

严格正确=0；标题合规=0；输入=[2, 8, 4, 2]；工具索引=[1, 7, 5, 3, 5]。

实际输出：
```text
blue:
rev 2 4 8 2
rot 4 8 2 2
inc 5 9 3 3
gray:
rot 9 3 3 5
rot 3 3 5 9
inc 4 4 6 0
black:
inc 5 5 7 1
swap 5 5 7 1
black:
inc 6 6 8 2
swap 6 6 8 2
gold:
inc 7 7 9 3
rev 3 9 7 7
black:
inc 4 0 0 8
swap 0 0 0 8
Answer: 0 0 0 8
```

标准轨迹：
```text
blue:
rev 2 4 8 2
rot 4 8 2 2
inc 5 9 3 3
gray:
rot 9 3 3 5
rot 3 3 5 9
inc 4 4 6 0
black:
inc 5 5 7 1
swap 5 5 7 1
gold:
inc 6 6 8 2
rev 2 8 6 6
black:
inc 3 9 7 7
swap 9 3 7 7
Answer: 9 3 7 7

```

## NAME seed302 L5-test-00281：final_Answer_only

严格正确=0；标题合规=1；输入=[9, 5, 1, 1]；工具索引=[7, 3, 1, 0, 5]。

实际输出：
```text
gray:
rot 5 1 1 9
rot 1 1 9 5
inc 2 2 0 6
gold:
inc 3 3 1 7
rev 7 1 3 3
blue:
rev 3 3 1 7
rot 3 1 7 3
inc 4 2 8 4
red:
rot 2 8 4 4
inc 3 9 5 5
black:
inc 4 0 6 6
swap 0 4 6 6
Answer: 4 0 6 6
```

标准轨迹：
```text
gray:
rot 5 1 1 9
rot 1 1 9 5
inc 2 2 0 6
gold:
inc 3 3 1 7
rev 7 1 3 3
blue:
rev 3 3 1 7
rot 3 1 7 3
inc 4 2 8 4
red:
rot 2 8 4 4
inc 3 9 5 5
black:
inc 4 0 6 6
swap 0 4 6 6
Answer: 0 4 6 6

```

## NAME seed303 L5-test-00013：numeric_step

严格正确=0；标题合规=1；输入=[6, 2, 9, 8]；工具索引=[5, 0, 3, 6, 2]。

实际输出：
```text
black:
inc 7 3 0 9
swap 3 7 0 9
red:
rot 7 0 9 3
inc 8 1 0 4
gold:
inc 9 2 1 5
rev 5 1 2 9
white:
inc 6 2 3 0
neg 4 8 7 0
inc 5 9 0 1
green:
rot 9 0 1 5
rot 0 1 5 9
Answer: 0 1 5 9
```

标准轨迹：
```text
black:
inc 7 3 0 9
swap 3 7 0 9
red:
rot 7 0 9 3
inc 8 1 0 4
gold:
inc 9 2 1 5
rev 5 1 2 9
white:
inc 6 2 3 0
neg 4 8 7 0
inc 5 9 8 1
green:
rot 9 8 1 5
rot 8 1 5 9
Answer: 8 1 5 9

```

## NAME seed303 L5-test-00016：operation_sequence

严格正确=0；标题合规=0；输入=[2, 8, 4, 2]；工具索引=[1, 7, 5, 3, 5]。

实际输出：
```text
blue:
rev 2 4 8 2
rot 4 8 2 2
inc 5 9 3 3
gray:
rot 9 3 3 5
rot 3 3 5 9
inc 4 4 6 0
black:
inc 5 5 7 1
swap 5 5 7 1
black:
inc 6 6 8 2
swap 6 6 8 2
gold:
inc 7 7 9 3
rev 3 9 7 7
black:
inc 4 0 0 8
swap 0 0 8 4
Answer: 0 0 8 4
```

标准轨迹：
```text
blue:
rev 2 4 8 2
rot 4 8 2 2
inc 5 9 3 3
gray:
rot 9 3 3 5
rot 3 3 5 9
inc 4 4 6 0
black:
inc 5 5 7 1
swap 5 5 7 1
gold:
inc 6 6 8 2
rev 2 8 6 6
black:
inc 3 9 7 7
swap 9 3 7 7
Answer: 9 3 7 7

```

