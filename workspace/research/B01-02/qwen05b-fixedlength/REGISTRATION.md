# Qwen2.5-0.5B fixed-length label replication: preregistration

Date: 2026-09-27. User-authorized study. Retain the original four-label model, tools, prompts, targets, LoRA, optimizer, 512 steps, 16×2 batch, greedy decoding, and strict complete-trajectory criterion. Training and testing at each level contain **exactly** L calls. Four groups share 4096 underlying training examples and 512 test examples, without duplicate chain/four-digit-input pairs.

## Separating exploration and formal replication

Explore L=10,15,20,25,30 sequentially with three paired training seeds (11,22,33), initially comparing uniform STEP (flat) and original names (macro). Continue in increments of five if saturated; intermediate lengths may be added after abrupt performance drops. Freeze independent tests per level and retain unfavorable results. Prefer candidates with STEP mean strict success in the inclusive 10%–90% range, original-name mean gain of at least five points, and improvement in at least 2/3 seeds. This exploratory rule selects the next step and is not confirmatory evidence. If criteria do not jointly hold, continue planned lengths and select the most informative level from observed results/costs, disclosing selection. Stop and report persistent floors or uncontrolled costs.

Formal replication uses 20 **new** paired training seeds, 200–219, disjoint from exploration. Reuse the selected level of 4096 frozen training examples to isolate length/example changes. Generate 512 fresh formal tests with no chain/input overlap with training or exploration. Score all four labels on the same new tests. During normal formal runs, inspect approximately hourly; handle stage completion and failure immediately.

## Data and capacity

Draw each fixed-length chain independently and uniformly from nine tools, and each input digit uniformly. Resample duplicate chain/input pairs. Exploration training seed: 10000+L; exploration test seed: 20000+L; formal test seed: 30000+L. Use 4096 training and 512 test examples, freezing data and generator hashes before training.

Change only model/data directories, four-label targets, and necessary length-capacity assertions in the trainer; preserve the 512-step algorithm. Use the smallest predefined generation limit (256,512,1024,1536,2048,3072,4096) fitting every correct target across 512 tests and four conditions, shared across groups. Record any cap issues. Retain the old strict scorer and additionally record missing/extra tools, expansion/numeric errors, cap hits, generated tokens, and allocated GPU time. Do not tune decoding or training on test results.

Prompt-only controls, real-task extensions, and publication are outside this round.

## Resource update, 2026-09-27, during length-30 exploration

The user reclaimed remote servers `.70` and `.65`. No jobs from this round ran on them. Continue only on the eight local `.69` RTX PRO6000 GPUs. This resource change does not alter training, evaluation, or formal-replication design.

## Length-40 memory compatibility adjustment

Initial length-40 microbatch16/accum2 exploration hit CUDA OOM near step 20 for flat-s11 and macro-s11. Retain failed runs/logs; the other four completed. Retry the two failures in new `-retry1` directories with microbatch8/accum4, preserving effective batch 32, 512 steps, and 16384 examples. Length-40 exploration therefore mixes two microbatch implementations, so its three-seed variation is not a strict same-recipe estimate. If chosen for formal replication, all four conditions and 20 new seeds use 8/4. Lengths above 40 also begin at 8/4, documenting further adjustments. User-authorized capacity changes are limited here to the necessary memory repair.

## Formal candidate freeze after length-40 exploration scoring and before formal-test generation

STEP means at L10/15/20/25/30/35 are 99.93/100/98.89/99.02/96.48/92.90%. At L40, STEP is 74.02% and original names 98.96%, a paired +24.93-point difference with 3/3 seeds improving. L40 first satisfies STEP 10%–90%, name gain ≥5 points, and at least 2/3 improving seeds. Select L40 without exploring longer levels or reselecting from formal results. Formal seeds are 200–219; freeze 512 fresh tests using prespecified seed 30040 before any formal training. All four labels use 8×4, 512 steps, shared underlying training/formal tests, and generation limit 1536.
