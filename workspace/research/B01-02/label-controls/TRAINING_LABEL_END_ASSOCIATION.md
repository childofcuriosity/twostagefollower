# Association between labels and training end positions: data description
This supplementary data audit was added after the first 1.5B results, not as a preregistered mechanism test. No experiments are changed. Ending here means that the labeled tool is the last tool in a training example, not the probability of predicting Answer immediately after the label.

|Condition|Label|Occurrences|Belongs to final tool|Fraction|
|---|---|---:|---:|---:|
|flat|step|7798|4096|52.53%|
|macro|gray|843|455|53.97%|
|macro|brown|879|441|50.17%|
|macro|black|910|474|52.09%|
|macro|green|847|436|51.48%|
|macro|gold|841|444|52.79%|
|macro|red|885|457|51.64%|
|macro|pink|857|462|53.91%|
|macro|white|853|450|52.75%|
|macro|blue|883|477|54.02%|
|position|step1|4096|394|9.62%|
|position|step2|3702|3702|100.00%|
|alias|toolG|843|455|53.97%|
|alias|toolD|879|441|50.17%|
|alias|toolE|910|474|52.09%|
|alias|toolA|847|436|51.48%|
|alias|toolI|841|444|52.79%|
|alias|toolH|885|457|51.64%|
|alias|toolF|857|462|53.91%|
|alias|toolC|853|450|52.75%|
|alias|toolB|883|477|54.02%|

In training, step2 is always the final tool for the position condition. Position failures may therefore involve both termination associations and extrapolation to untrained positions. Original NAME and aliases have identical end-position associations when matched by tool, but differ in word form, tokenization, and input representation. This description does not establish which mechanism the model actually uses.
