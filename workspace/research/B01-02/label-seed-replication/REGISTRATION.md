# Training-seed replication of the label experiment: preregistration

Registered on 2026-09-26. The user authorized this study for 1.5B, 3B, and 7B only; 32B is excluded.

## Research question

Across the four labels on the earlier independent 480-example set, standard deviations over three training seeds were large, especially for fixed aliases versus original names. This study fixes data, models, training configurations, alias mapping, and evaluation protocol while adding training seeds to estimate accuracy and paired differences under training randomness. Neither a smaller standard deviation nor positive results are stopping criteria.

## Fixed design

- Qwen2.5 Base 1.5B, 3B, and 7B; four conditions: flat (uniform step), position (position numbering), alias (fixed toolA–I mapping), and macro (original names). Retain the first-stage Answer protocol.
- Fix the same 20 training seeds for every model/condition: reuse old seeds 11/22/33 read-only and add 17 seeds 100–116. New training totals 3×4×17=204 runs.
- Use the original 4096 training examples with 1–2 tools, 512 optimizer steps, effective batch32, LoRA r16/alpha32/dropout0, and learning rate 3e-4. Within each model, input/output construction follows the original four condition definitions. Original training-algorithm source remains unchanged; run snapshots are saved here.
- Fix the original 560-example test and earlier independent 480-example set. The primary result is strict full-trajectory success on the independent 480 examples; the original OOD384 examples provide a cross-check. Do not select checkpoints on test results.
- Pair all four conditions for every new seed. Inference is greedy, with independent-set batch4/max_new_tokens512. Reused seeds 11/22/33 use the same independent-set batch and token cap.
- Keep the earlier 2026092601 alias mapping. **This design estimates training-seed variation under a fixed mapping**, not variation across alias mappings.
- Primary adjacent paired differences: position−flat, alias−position, macro−alias. Also report macro−flat and alias−macro for comparison with earlier work.
- For every model×condition, report the 20-seed mean, sample SD, and range. For paired differences, report every seed, mean, sample SD, and 95% t interval. Intervals are descriptive estimates over training seeds; shared test examples are not 20×480 independent examples. Report all 20 seeds and failures. Do not stop early or add selected seeds after a desired direction appears. If direction remains unclear after 20 seeds, report uncertainty rather than changing endpoints or filtering seeds.

## Acceptance checks and interpretation limits

All 204 jobs must exit with code 0, with 512 steps and 16384 example exposures per run. Outputs must match frozen example IDs, inputs, and tool sequences; old-record hashes must remain unchanged and historical scores equivalent. Check matching same-seed initial adapters for the first new seed in each condition. Retain all raw outputs, logs, and failure records.

A training seed affects both LoRA initialization and data shuffling; their separate effects are not identified. Position numbering and fixed identity convey different types of information, so the four conditions are not a strictly monotonic information-content experiment. Position training sees only step1/2. New targets have approximately 2.96% more tokens than old macro targets, and alias inputs are longer; tokenization/length are unmatched. The earlier independent set has already been used and is not a fresh blind test. More training seeds cannot eliminate these confounds or establish real-agent or RSI benefits.

## Resources

Use only the 8 local RTX PRO6000 Blackwell GPUs, allocated dynamically as GPUs become free. Do not use returned remote machines. Based on measured per-job wall time, 204 jobs are expected to require approximately 65–80 allocated GPU-hours, or about 9–12 hours wall time if all 8 GPUs remain available; actual records determine final costs. Check routine runs approximately hourly and handle failures/completion promptly.
