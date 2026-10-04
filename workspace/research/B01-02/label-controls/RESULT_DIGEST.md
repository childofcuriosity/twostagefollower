# Position and identity controls: automated summary
This study aims to separate progress information, stable tool identity, and name form. The two original conditions were not retrained; the two new conditions retain the original training and Answer protocols. Results below are computed at fixed step512 on the earlier independent 480-example set. See REPORT.md for all counterexamples and original tests.

|Model|Original STEP|Original NAME|Position numbering|Fixed aliases|
|---|---:|---:|---:|---:|
|qwen1.5b|0.00%|16.25%|0.00%|16.81%|
|qwen3b|0.00%|36.88%|0.97%|52.92%|
|qwen7b|12.15%|37.01%|19.86%|58.33%|
|qwen32b|25.63%|56.18%|39.17%|31.18%|

## Paired evidence at each scale

### qwen1.5b

|Comparison|Mean difference pp|Three training-seed differences pp|
|---|---:|---|
|Position numbering − Original STEP|+0.00|+0.00 / +0.00 / +0.00|
|Fixed aliases − Original STEP|+16.81|+7.29 / +30.83 / +12.29|
|Position numbering − Original NAME|-16.25|-16.67 / -20.62 / -11.46|
|Fixed aliases − Original NAME|+0.56|-9.38 / +10.21 / +0.83|
|Fixed aliases − Position numbering|+16.81|+7.29 / +30.83 / +12.29|

Positive and negative signs indicate observed directions. Means must not hide negative seeds, and three seeds do not adequately cover training randomness.

### qwen3b

|Comparison|Mean difference pp|Three training-seed differences pp|
|---|---:|---|
|Position numbering − Original STEP|+0.97|+0.00 / +0.62 / +2.29|
|Fixed aliases − Original STEP|+52.92|+53.96 / +38.33 / +66.46|
|Position numbering − Original NAME|-35.90|-36.04 / -39.58 / -32.08|
|Fixed aliases − Original NAME|+16.04|+17.92 / -1.88 / +32.08|
|Fixed aliases − Position numbering|+51.94|+53.96 / +37.71 / +64.17|

Positive and negative signs indicate observed directions. Means must not hide negative seeds, and three seeds do not adequately cover training randomness.

### qwen7b

|Comparison|Mean difference pp|Three training-seed differences pp|
|---|---:|---|
|Position numbering − Original STEP|+7.71|+3.33 / -3.75 / +23.54|
|Fixed aliases − Original STEP|+46.18|+51.04 / +18.54 / +68.96|
|Position numbering − Original NAME|-17.15|-15.00 / -42.50 / +6.04|
|Fixed aliases − Original NAME|+21.32|+32.71 / -20.21 / +51.46|
|Fixed aliases − Position numbering|+38.47|+47.71 / +22.29 / +45.42|

Positive and negative signs indicate observed directions. Means must not hide negative seeds, and three seeds do not adequately cover training randomness.

### qwen32b

|Comparison|Mean difference pp|Three training-seed differences pp|
|---|---:|---|
|Position numbering − Original STEP|+13.54|+18.54 / -0.62 / +22.71|
|Fixed aliases − Original STEP|+5.56|+11.67 / +15.00 / -10.00|
|Position numbering − Original NAME|-17.01|-1.88 / -26.67 / -22.50|
|Fixed aliases − Original NAME|-25.00|-8.75 / -11.04 / -55.21|
|Fixed aliases − Position numbering|-7.99|-6.88 / +15.62 / -32.71|

Positive and negative signs indicate observed directions. Means must not hide negative seeds, and three seeds do not adequately cover training randomness.

## Scope of interpretation

- The two added conditions have equal supervised output-token counts: 271656 per pass, compared with 263858 for Original NAME. New labels add approximately 2.96%; no padding or configuration changes hide this difference. Alias input prompts are also longer.
- Position labels step3 and later are label combinations unseen in training, although digit tokens themselves occur in numerical states. Failure alone cannot rule out the value of position information.
- Alias and Original NAME both use matching names in inputs and outputs, so this does not directly test matched versus mismatched names. If aliases are weaker, word-form distinguishability, a shared tool prefix, tokenization/pretrained representations, and learning difficulty are plausible explanations; a causal attention mechanism is not established.
- One fixed mapping is used across all seeds/scales, without replication over multiple mappings. The earlier test set has been used before and is not a fresh blind test.
- The original strict primary metric checks required operations and answers without requiring correct label identities. Label sequences and label-aware full-success rates are reported separately to preserve the original scoring standard.
- The task supplies the sequence; it does not directly test autonomous planning or mid-task stopping in real agents. Application transfer remains untested.

All 49920 main/independent trajectories (24960 new, 24960 reused) are independently scored. See analysis/completion-audit.json for data and source-freeze checks. All generation failures remain in denominators. The system goal slot still refers to the older paused task; this study marks GOAL.json complete only after final human review and delivery.

See [CONCLUSIONS.md](CONCLUSIONS.md) for final scientific review and limitations.
