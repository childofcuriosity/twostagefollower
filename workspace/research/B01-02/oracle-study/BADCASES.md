# 配对轨迹抽查
先统计全部同题收益/退化，再用固定随机种子20260925各抽3条。这里展示32B展开专用收益与7B展开专用退化，均为8工具、相同正确顺序oracle。样本用于核对错误内容，不替代全量统计。32B这次随机抽到的3条均来自seed11；三个seed的汇总必须另外查看。

## qwen32b / order_oracle / 8 / gain
全集81条配对事件，抽3条。

### seed11, id=100444
输入：[6, 5, 5, 1]；名称序列：green → green → brown → green → black → brown → blue → green
首个错误在第5个工具`black`；应为['inc', 'swap']，错误输出操作为['inc']。
整条正确：联合=False，专用=True。
联合模型该工具的原始body：
```text
inc 9 5 0 9
EndTool
```
专用模型同位置的原始body：
```text
inc 9 5 0 9
swap 5 9 0 9
EndTool
```
原始文件：`runs/qwen32b-joint-s11/evaluation-order_oracle-independent.jsonl`；`runs/qwen32b-order_oracle-s11/evaluation-order_oracle-independent.jsonl`。

### seed11, id=100452
输入：[9, 1, 3, 1]；名称序列：blue → green → gray → red → white → pink → brown → gray
首个错误在第5个工具`white`；应为['inc', 'neg', 'inc']，错误输出操作为['inc', 'neg']。
整条正确：联合=False，专用=True。
联合模型该工具的原始body：
```text
inc 5 3 5 7
neg 5 7 5 3
EndTool
```
专用模型同位置的原始body：
```text
inc 5 3 5 7
neg 5 7 5 3
inc 6 8 6 4
EndTool
```
原始文件：`runs/qwen32b-joint-s11/evaluation-order_oracle-independent.jsonl`；`runs/qwen32b-order_oracle-s11/evaluation-order_oracle-independent.jsonl`。

### seed11, id=100391
输入：[5, 7, 7, 5]；名称序列：red → pink → pink → green → pink → gold → red → brown
首个错误在第8个工具`brown`；应为['inc', 'inc', 'inc']，错误输出操作为['inc', 'inc']。
整条正确：联合=False，专用=True。
联合模型该工具的原始body：
```text
inc 4 2 2 4
inc 5 3 3 5
EndTool
```
专用模型同位置的原始body：
```text
inc 4 2 2 4
inc 5 3 3 5
inc 6 4 4 6
EndTool
```
原始文件：`runs/qwen32b-joint-s11/evaluation-order_oracle-independent.jsonl`；`runs/qwen32b-order_oracle-s11/evaluation-order_oracle-independent.jsonl`。

## qwen7b / order_oracle / 8 / loss
全集122条配对事件，抽3条。

### seed33, id=100479
输入：[8, 0, 1, 0]；名称序列：gold → green → blue → blue → brown → gray → blue → gold
首个错误在第4个工具`blue`；应为['rev', 'rot', 'inc']，错误输出操作为['rev', 'rot']。
整条正确：联合=True，专用=False。
联合模型该工具的原始body：
```text
rev 3 2 0 2
rot 2 0 2 3
inc 3 1 3 4
EndTool
```
专用模型同位置的原始body：
```text
rev 3 2 0 2
rot 2 0 2 3
EndTool
```
原始文件：`runs/qwen7b-joint-s33/evaluation-order_oracle-independent.jsonl`；`runs/qwen7b-order_oracle-s33/evaluation-order_oracle-independent.jsonl`。

### seed33, id=100409
输入：[0, 9, 4, 9]；名称序列：black → brown → pink → gold → white → brown → blue → brown
首个错误在第7个工具`blue`；应为['rev', 'rot', 'inc']，错误输出操作为['rev']。
整条正确：联合=True，专用=False。
联合模型该工具的原始body：
```text
rev 3 7 8 8
rot 7 8 8 3
inc 8 9 9 4
EndTool
```
专用模型同位置的原始body：
```text
rev 3 7 8 8
EndTool
```
原始文件：`runs/qwen7b-joint-s33/evaluation-order_oracle-independent.jsonl`；`runs/qwen7b-order_oracle-s33/evaluation-order_oracle-independent.jsonl`。

### seed33, id=100447
输入：[4, 2, 8, 7]；名称序列：gold → gold → gold → red → brown → green → gold → pink
首个错误在第4个工具`red`；应为['rot', 'inc']，错误输出操作为['rot']。
整条正确：联合=True，专用=False。
联合模型该工具的原始body：
```text
rot 1 5 7 0
inc 2 6 8 1
EndTool
```
专用模型同位置的原始body：
```text
rot 1 5 7 0
EndTool
```
原始文件：`runs/qwen7b-joint-s33/evaluation-order_oracle-independent.jsonl`；`runs/qwen7b-order_oracle-s33/evaluation-order_oracle-independent.jsonl`。