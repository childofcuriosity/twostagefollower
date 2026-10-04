# 7b-L3：错误与标题核验

以下只解释已保存输出，不改变严格主评分。互斥归类按Answer数量、未知行、操作序列、数字步骤、仅最终Answer的固定优先顺序进行；不是按时间定位首错。原始可重叠错误标志保存在analysis/results.json。

| 条件/seed | 失败/512 | Answer数量 | 未知行 | 操作序列 | 数字步骤 | 仅最终Answer | 仅额外Trace标题 | 其他标题问题 | 截断 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| STEP/base | 492 | 7 | 7 | 341 | 137 | 0 | 0 | 58 | 0 |
| STEP/301 | 467 | 2 | 8 | 312 | 143 | 2 | 0 | 31 | 0 |
| STEP/302 | 469 | 6 | 2 | 319 | 140 | 2 | 0 | 34 | 0 |
| STEP/303 | 473 | 5 | 7 | 314 | 145 | 2 | 0 | 49 | 0 |
| NAME/base | 475 | 46 | 12 | 207 | 210 | 0 | 0 | 53 | 0 |
| NAME/301 | 364 | 6 | 7 | 115 | 233 | 3 | 0 | 28 | 0 |
| NAME/302 | 343 | 0 | 4 | 109 | 226 | 4 | 0 | 24 | 0 |
| NAME/303 | 326 | 0 | 3 | 101 | 219 | 3 | 0 | 24 | 0 |

base为原始模型step0，其余为对应seed的step100。额外Trace标题可能与严格成功同时出现；它不代表新增工具调用。操作序列不匹配涵盖原始操作遗漏、增加、替换和顺序改变，不能直接反推遗漏了几次高层工具调用。EOS只说明主动结束，不保证执行完整。互斥优先级归类存在遮蔽：操作序列改善后，更多失败会落入数字错误类别；不能仅凭该类别计数增加就判断数字计算变差，应同时查看主报告中的可重叠数字错误标志。

案例按每个条件/seed/错误类别的最小题目ID选取，展示原始与标准轨迹；类别频率以上表为准。

## STEP seed301 L3-test-00000：numeric_step

严格正确=0；标题合规=1；输入=[9, 3, 2, 8]；工具索引=[1, 6, 1]。

实际输出：
```text
step:
rev 8 2 3 9
rot 2 3 9 8
inc 3 4 0 8
step:
inc 4 5 1 9
neg 6 5 9 0
inc 7 6 0 9
step:
rev 9 0 6 7
rot 0 6 7 9
inc 1 7 8 0
Answer: 1 7 8 0
```

标准轨迹：
```text
step:
rev 8 2 3 9
rot 2 3 9 8
inc 3 4 0 9
step:
inc 4 5 1 0
neg 6 5 9 0
inc 7 6 0 1
step:
rev 1 0 6 7
rot 0 6 7 1
inc 1 7 8 2
Answer: 1 7 8 2

```

## STEP seed301 L3-test-00001：operation_sequence

严格正确=0；标题合规=1；输入=[5, 3, 6, 8]；工具索引=[3, 0, 6]。

实际输出：
```text
step:
inc 6 4 7 9
rev 9 7 4 6
step:
rot 7 4 6 9
inc 8 5 7 0
step:
inc 9 6 8 1
neg 1 7 9 9
Answer: 1 7 9 9
```

标准轨迹：
```text
step:
inc 6 4 7 9
rev 9 7 4 6
step:
rot 7 4 6 9
inc 8 5 7 0
step:
inc 9 6 8 1
neg 1 4 2 9
inc 2 5 3 0
Answer: 2 5 3 0

```

## STEP seed301 L3-test-00104：final_Answer_only

严格正确=0；标题合规=1；输入=[8, 0, 3, 5]；工具索引=[1, 4, 5]。

实际输出：
```text
step:
rev 5 3 0 8
rot 3 0 8 5
inc 4 1 9 6
step:
rot 1 9 6 4
inc 2 0 7 5
swap 0 2 7 5
step:
inc 1 3 8 6
swap 3 1 8 6
Answer: 1 3 8 6
```

标准轨迹：
```text
step:
rev 5 3 0 8
rot 3 0 8 5
inc 4 1 9 6
step:
rot 1 9 6 4
inc 2 0 7 5
swap 0 2 7 5
step:
inc 1 3 8 6
swap 3 1 8 6
Answer: 3 1 8 6

```

## STEP seed301 L3-test-00125：unrecognized_extra_lines

严格正确=0；标题合规=1；输入=[9, 8, 3, 0]；工具索引=[5, 1, 2]。

实际输出：
```text
step:
inc 0 9 4 0
swap 9 0 4 0
step:
rev 0 4 0 9
rot 4 0 9 0
inc 5 1 10 0
step:
rot 1 10 0 5
rot 10 0 5 1
inc 1 1 6 1
Answer: 1 1 6 1
```

标准轨迹：
```text
step:
inc 0 9 4 1
swap 9 0 4 1
step:
rev 1 4 0 9
rot 4 0 9 1
inc 5 1 0 2
step:
rot 1 0 2 5
rot 0 2 5 1
Answer: 0 2 5 1

```

## STEP seed301 L3-test-00181：missing_or_multiple_Answer

严格正确=0；标题合规=1；输入=[6, 2, 7, 2]；工具索引=[2, 2, 1]。

实际输出：
```text
step:
rot 2 7 2 6
rot 7 2 6 2
step:
rot 2 6 2 7
rot 6 2 7 2
step:
rev 2 7 2 6
rot 7 2 6 2
inc 8 3 3 3
```

标准轨迹：
```text
step:
rot 2 7 2 6
rot 7 2 6 2
step:
rot 2 6 2 7
rot 6 2 7 2
step:
rev 2 7 2 6
rot 7 2 6 2
inc 8 3 7 3
Answer: 8 3 7 3

```

## STEP seed302 L3-test-00000：numeric_step

严格正确=0；标题合规=1；输入=[9, 3, 2, 8]；工具索引=[1, 6, 1]。

实际输出：
```text
step:
rev 8 2 3 9
rot 2 3 9 8
inc 3 4 0 9
step:
inc 4 5 1 0
neg 6 5 1 9
inc 7 6 2 0
step:
rev 0 2 6 7
rot 2 6 7 0
inc 3 7 8 1
Answer: 3 7 8 1
```

标准轨迹：
```text
step:
rev 8 2 3 9
rot 2 3 9 8
inc 3 4 0 9
step:
inc 4 5 1 0
neg 6 5 9 0
inc 7 6 0 1
step:
rev 1 0 6 7
rot 0 6 7 1
inc 1 7 8 2
Answer: 1 7 8 2

```

## STEP seed302 L3-test-00001：operation_sequence

严格正确=0；标题合规=1；输入=[5, 3, 6, 8]；工具索引=[3, 0, 6]。

实际输出：
```text
step:
inc 6 4 7 9
rev 9 7 4 6
step:
rot 7 4 6 9
inc 8 5 7 0
step:
inc 0 6 8 1
neg 0 7 9 1
Answer: 0 7 9 1
```

标准轨迹：
```text
step:
inc 6 4 7 9
rev 9 7 4 6
step:
rot 7 4 6 9
inc 8 5 7 0
step:
inc 9 6 8 1
neg 1 4 2 9
inc 2 5 3 0
Answer: 2 5 3 0

```

## STEP seed302 L3-test-00104：final_Answer_only

严格正确=0；标题合规=1；输入=[8, 0, 3, 5]；工具索引=[1, 4, 5]。

实际输出：
```text
step:
rev 5 3 0 8
rot 3 0 8 5
inc 4 1 9 6
step:
rot 1 9 6 4
inc 2 0 7 5
swap 0 2 7 5
step:
inc 1 3 8 6
swap 3 1 8 6
Answer: 1 3 8 6
```

标准轨迹：
```text
step:
rev 5 3 0 8
rot 3 0 8 5
inc 4 1 9 6
step:
rot 1 9 6 4
inc 2 0 7 5
swap 0 2 7 5
step:
inc 1 3 8 6
swap 3 1 8 6
Answer: 3 1 8 6

```

## STEP seed302 L3-test-00125：unrecognized_extra_lines

严格正确=0；标题合规=1；输入=[9, 8, 3, 0]；工具索引=[5, 1, 2]。

实际输出：
```text
step:
inc 0 9 4 0
swap 9 0 4 0
step:
rev 0 4 0 9
rot 4 0 9 0
inc 5 1 10 1
step:
rot 1 10 1 5
rot 10 1 5 1
inc 0 2 6 2
Answer: 0 2 6 2
```

标准轨迹：
```text
step:
inc 0 9 4 1
swap 9 0 4 1
step:
rev 1 4 0 9
rot 4 0 9 1
inc 5 1 0 2
step:
rot 1 0 2 5
rot 0 2 5 1
Answer: 0 2 5 1

```

## STEP seed302 L3-test-00189：missing_or_multiple_Answer

严格正确=0；标题合规=1；输入=[0, 3, 3, 7]；工具索引=[8, 5, 4]。

实际输出：
```text
step:
inc 1 4 4 8
inc 2 5 5 9
inc 3 6 6 0
step:
swap 3 3 6 0
step:
rot 3 6 0 3
inc 4 7 1 4
```

标准轨迹：
```text
step:
inc 1 4 4 8
inc 2 5 5 9
inc 3 6 6 0
step:
inc 4 7 7 1
swap 7 4 7 1
step:
rot 4 7 1 7
inc 5 8 2 8
swap 8 5 2 8
Answer: 8 5 2 8

```

## STEP seed303 L3-test-00000：numeric_step

严格正确=0；标题合规=1；输入=[9, 3, 2, 8]；工具索引=[1, 6, 1]。

实际输出：
```text
step:
rev 8 2 3 9
rot 2 3 9 8
inc 3 4 0 9
step:
inc 4 5 1 0
neg 6 5 1 9
inc 7 6 2 0
step:
rev 0 2 6 7
rot 2 6 7 0
inc 3 7 8 1
Answer: 3 7 8 1
```

标准轨迹：
```text
step:
rev 8 2 3 9
rot 2 3 9 8
inc 3 4 0 9
step:
inc 4 5 1 0
neg 6 5 9 0
inc 7 6 0 1
step:
rev 1 0 6 7
rot 0 6 7 1
inc 1 7 8 2
Answer: 1 7 8 2

```

## STEP seed303 L3-test-00001：operation_sequence

严格正确=0；标题合规=1；输入=[5, 3, 6, 8]；工具索引=[3, 0, 6]。

实际输出：
```text
step:
inc 6 4 7 9
rev 9 7 4 6
step:
rot 7 4 6 9
inc 8 5 7 0
step:
inc 9 6 8 1
neg 1 7 9 9
Answer: 1 7 9 9
```

标准轨迹：
```text
step:
inc 6 4 7 9
rev 9 7 4 6
step:
rot 7 4 6 9
inc 8 5 7 0
step:
inc 9 6 8 1
neg 1 4 2 9
inc 2 5 3 0
Answer: 2 5 3 0

```

## STEP seed303 L3-test-00104：final_Answer_only

严格正确=0；标题合规=1；输入=[8, 0, 3, 5]；工具索引=[1, 4, 5]。

实际输出：
```text
step:
rev 5 3 0 8
rot 3 0 8 5
inc 4 1 9 6
step:
rot 1 9 6 4
inc 2 0 7 5
swap 0 2 7 5
step:
inc 1 3 8 6
swap 3 1 8 6
Answer: 1 3 8 6
```

标准轨迹：
```text
step:
rev 5 3 0 8
rot 3 0 8 5
inc 4 1 9 6
step:
rot 1 9 6 4
inc 2 0 7 5
swap 0 2 7 5
step:
inc 1 3 8 6
swap 3 1 8 6
Answer: 3 1 8 6

```

## STEP seed303 L3-test-00125：unrecognized_extra_lines

严格正确=0；标题合规=1；输入=[9, 8, 3, 0]；工具索引=[5, 1, 2]。

实际输出：
```text
step:
inc 0 9 4 0
swap 9 0 4 0
step:
rev 0 4 0 9
rot 4 0 9 0
inc 5 1 10 0
step:
rot 1 10 0 5
rot 10 0 5 1
inc 1 1 6 1
Answer: 1 1 6 1
```

标准轨迹：
```text
step:
inc 0 9 4 1
swap 9 0 4 1
step:
rev 1 4 0 9
rot 4 0 9 1
inc 5 1 0 2
step:
rot 1 0 2 5
rot 0 2 5 1
Answer: 0 2 5 1

```

## STEP seed303 L3-test-00189：missing_or_multiple_Answer

严格正确=0；标题合规=1；输入=[0, 3, 3, 7]；工具索引=[8, 5, 4]。

实际输出：
```text
step:
inc 1 4 3 8
inc 2 5 4 9
inc 3 6 5 0
step:
swap 3 3 6 7
step:
rot 3 6 7 3
inc 4 7 8 4
```

标准轨迹：
```text
step:
inc 1 4 4 8
inc 2 5 5 9
inc 3 6 6 0
step:
inc 4 7 7 1
swap 7 4 7 1
step:
rot 4 7 1 7
inc 5 8 2 8
swap 8 5 2 8
Answer: 8 5 2 8

```

## NAME seed301 L3-test-00000：numeric_step

严格正确=0；标题合规=1；输入=[9, 3, 2, 8]；工具索引=[1, 6, 1]。

实际输出：
```text
blue:
rev 8 2 3 9
rot 2 3 9 8
inc 3 4 0 9
white:
inc 4 5 1 0
neg 6 5 1 9
inc 7 6 2 0
blue:
rev 0 2 6 7
rot 2 6 7 0
inc 3 7 8 1
Answer: 3 7 8 1
```

标准轨迹：
```text
blue:
rev 8 2 3 9
rot 2 3 9 8
inc 3 4 0 9
white:
inc 4 5 1 0
neg 6 5 9 0
inc 7 6 0 1
blue:
rev 1 0 6 7
rot 0 6 7 1
inc 1 7 8 2
Answer: 1 7 8 2

```

## NAME seed301 L3-test-00002：operation_sequence

严格正确=0；标题合规=1；输入=[9, 1, 1, 2]；工具索引=[2, 7, 3]。

实际输出：
```text
green:
rot 1 1 2 9
rot 1 2 9 1
inc 2 3 0 2
gray:
rot 3 0 2 2
rot 0 2 2 3
inc 1 3 3 5
gold:
inc 3 4 3 6
rev 6 3 4 3
Answer: 6 3 4 3
```

标准轨迹：
```text
green:
rot 1 1 2 9
rot 1 2 9 1
gray:
rot 2 9 1 1
rot 9 1 1 2
inc 0 2 2 3
gold:
inc 1 3 3 4
rev 4 3 3 1
Answer: 4 3 3 1

```

## NAME seed301 L3-test-00108：unrecognized_extra_lines

严格正确=0；标题合规=0；输入=[9, 4, 4, 7]；工具索引=[2, 3, 4]。

实际输出：
```text
green:
rot 4 4 7 9
rot 4 7 9 4
gold 5 8 0 5
pink 8 5 0 4
Answer: 8 5 0 4
```

标准轨迹：
```text
green:
rot 4 4 7 9
rot 4 7 9 4
gold:
inc 5 8 0 5
rev 5 0 8 5
pink:
rot 0 8 5 5
inc 1 9 6 6
swap 9 1 6 6
Answer: 9 1 6 6

```

## NAME seed301 L3-test-00181：missing_or_multiple_Answer

严格正确=0；标题合规=1；输入=[6, 2, 7, 2]；工具索引=[2, 2, 1]。

实际输出：
```text
green:
rot 2 7 2 6
rot 7 2 6 2
green:
rot 2 6 2 7
rot 6 2 7 2
blue:
rev 2 7 2 6
rot 7 2 6 2
inc 8 3 3 3
```

标准轨迹：
```text
green:
rot 2 7 2 6
rot 7 2 6 2
green:
rot 2 6 2 7
rot 6 2 7 2
blue:
rev 2 7 2 6
rot 7 2 6 2
inc 8 3 7 3
Answer: 8 3 7 3

```

## NAME seed301 L3-test-00194：final_Answer_only

严格正确=0；标题合规=1；输入=[2, 9, 5, 5]；工具索引=[3, 4, 8]。

实际输出：
```text
gold:
inc 3 0 6 6
rev 6 6 0 3
pink:
rot 6 0 3 6
inc 7 1 4 7
swap 1 7 4 7
brown:
inc 2 8 5 8
inc 3 9 6 9
inc 4 0 7 0
Answer: 3 9 6 0
```

标准轨迹：
```text
gold:
inc 3 0 6 6
rev 6 6 0 3
pink:
rot 6 0 3 6
inc 7 1 4 7
swap 1 7 4 7
brown:
inc 2 8 5 8
inc 3 9 6 9
inc 4 0 7 0
Answer: 4 0 7 0

```

## NAME seed302 L3-test-00000：numeric_step

严格正确=0；标题合规=1；输入=[9, 3, 2, 8]；工具索引=[1, 6, 1]。

实际输出：
```text
blue:
rev 8 2 3 9
rot 2 3 9 8
inc 3 4 0 9
white:
inc 4 5 1 0
neg 6 5 1 9
inc 7 6 2 0
blue:
rev 0 2 6 7
rot 2 6 7 0
inc 3 7 8 1
Answer: 3 7 8 1
```

标准轨迹：
```text
blue:
rev 8 2 3 9
rot 2 3 9 8
inc 3 4 0 9
white:
inc 4 5 1 0
neg 6 5 9 0
inc 7 6 0 1
blue:
rev 1 0 6 7
rot 0 6 7 1
inc 1 7 8 2
Answer: 1 7 8 2

```

## NAME seed302 L3-test-00002：operation_sequence

严格正确=0；标题合规=1；输入=[9, 1, 1, 2]；工具索引=[2, 7, 3]。

实际输出：
```text
green:
rot 1 1 2 9
rot 1 2 9 1
inc 2 3 0 2
gray:
rot 3 0 2 2
rot 0 2 2 3
inc 1 3 3 4
gold:
inc 2 4 3 5
rev 5 3 4 2
Answer: 5 3 4 2
```

标准轨迹：
```text
green:
rot 1 1 2 9
rot 1 2 9 1
gray:
rot 2 9 1 1
rot 9 1 1 2
inc 0 2 2 3
gold:
inc 1 3 3 4
rev 4 3 3 1
Answer: 4 3 3 1

```

## NAME seed302 L3-test-00133：unrecognized_extra_lines

严格正确=0；标题合规=1；输入=[0, 4, 7, 8]；工具索引=[0, 4, 4]。

实际输出：
```text
red:
rot 4 7 8 0
inc 5 8 9 1
pink:
rot 8 9 1 5
inc 9 0 2 6
swap 0 9 2 6
pink:
rot 9 2 6 0
inc a 3 7 1
swap 3 9 7 1
Answer: 3 9 7 1
```

标准轨迹：
```text
red:
rot 4 7 8 0
inc 5 8 9 1
pink:
rot 8 9 1 5
inc 9 0 2 6
swap 0 9 2 6
pink:
rot 9 2 6 0
inc 0 3 7 1
swap 3 0 7 1
Answer: 3 0 7 1

```

## NAME seed302 L3-test-00194：final_Answer_only

严格正确=0；标题合规=1；输入=[2, 9, 5, 5]；工具索引=[3, 4, 8]。

实际输出：
```text
gold:
inc 3 0 6 6
rev 6 6 0 3
pink:
rot 6 0 3 6
inc 7 1 4 7
swap 1 7 4 7
brown:
inc 2 8 5 8
inc 3 9 6 9
inc 4 0 7 0
Answer: 3 9 6 0
```

标准轨迹：
```text
gold:
inc 3 0 6 6
rev 6 6 0 3
pink:
rot 6 0 3 6
inc 7 1 4 7
swap 1 7 4 7
brown:
inc 2 8 5 8
inc 3 9 6 9
inc 4 0 7 0
Answer: 4 0 7 0

```

## NAME seed303 L3-test-00000：numeric_step

严格正确=0；标题合规=1；输入=[9, 3, 2, 8]；工具索引=[1, 6, 1]。

实际输出：
```text
blue:
rev 8 2 3 9
rot 2 3 9 8
inc 3 4 0 9
white:
inc 4 5 1 0
neg 6 5 1 9
inc 7 6 2 0
blue:
rev 0 2 6 7
rot 2 6 7 0
inc 3 7 8 1
Answer: 3 7 8 1
```

标准轨迹：
```text
blue:
rev 8 2 3 9
rot 2 3 9 8
inc 3 4 0 9
white:
inc 4 5 1 0
neg 6 5 9 0
inc 7 6 0 1
blue:
rev 1 0 6 7
rot 0 6 7 1
inc 1 7 8 2
Answer: 1 7 8 2

```

## NAME seed303 L3-test-00010：operation_sequence

严格正确=0；标题合规=1；输入=[8, 1, 4, 8]；工具索引=[1, 0, 3]。

实际输出：
```text
blue:
rev 8 4 1 8
rot 4 1 8 8
inc 5 2 9 9
red:
rot 2 9 9 5
inc 3 0 0 6
gold:
inc 4 1 1 7
Answer: 4 1 1 7
```

标准轨迹：
```text
blue:
rev 8 4 1 8
rot 4 1 8 8
inc 5 2 9 9
red:
rot 2 9 9 5
inc 3 0 0 6
gold:
inc 4 1 1 7
rev 7 1 1 4
Answer: 7 1 1 4

```

## NAME seed303 L3-test-00151：unrecognized_extra_lines

严格正确=0；标题合规=1；输入=[6, 5, 2, 4]；工具索引=[8, 2, 6]。

实际输出：
```text
brown:
inc 7 5 2 4
inc 8 6 3 5
inc 9 7 4 6
green:
rot 7 4 6 9
rot 4 6 9 7
white:
inc 5 7 10 8
neg 0 8 0 9
inc 1 9 1 0
Answer: 1 9 1 0
```

标准轨迹：
```text
brown:
inc 7 6 3 5
inc 8 7 4 6
inc 9 8 5 7
green:
rot 8 5 7 9
rot 5 7 9 8
white:
inc 6 8 0 9
neg 4 2 0 1
inc 5 3 1 2
Answer: 5 3 1 2

```

## NAME seed303 L3-test-00380：final_Answer_only

严格正确=0；标题合规=1；输入=[4, 7, 7, 2]；工具索引=[4, 2, 8]。

实际输出：
```text
pink:
rot 7 7 2 4
inc 8 8 3 5
swap 8 8 3 5
green:
rot 8 3 5 8
rot 3 5 8 8
brown:
inc 4 6 9 9
inc 5 7 0 0
inc 6 8 1 1
Answer: 5 7 0 0
```

标准轨迹：
```text
pink:
rot 7 7 2 4
inc 8 8 3 5
swap 8 8 3 5
green:
rot 8 3 5 8
rot 3 5 8 8
brown:
inc 4 6 9 9
inc 5 7 0 0
inc 6 8 1 1
Answer: 6 8 1 1

```

