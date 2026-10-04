# Second-stage methods and reproduction

This study addresses only oracle ablations of the original toy task: can name sequences and within-tool expansion be learned as separate supervision targets, and how do they differ from joint training? Models are Qwen2.5 Base 1.5B,3B,7B,32B with LoRA supervised fine-tuning. There is no Agentic RL or online invention of tools. Scripts in this directory directly train and evaluate the models.

## Task and two subtasks

Inputs contain four digits and an already ordered list of tool names, to be executed left to right. Each of 9 fixed tools contains 2 or 3 primitive operations; there are 6 primitive operation types, of which this library uses 5. Inputs describe primitive operations but do not supply tool definitions per example; fixed name-to-expansion mappings are learned from training examples. **Sequence task A repeats the complete input name list and terminates at the right point; it does not derive a plan from a goal.** Expansion task B requires correct operation lines, numbers, and tool-ending positions for every required tool.

For input digits `1 2 3 4` and tools `red black`, the correct output is:

```text
red:
rot 2 3 4 1
inc 3 4 5 2
EndTool
black:
inc 4 5 6 3
swap 5 4 6 3
EndTool
Done
```

All three training conditions see exactly the same correct text; losses differ:

|Condition|Model learns to predict|Program supplies during oracle inference|
|---|---|---|
|joint training|Names, operations, EndTool, Done|Nothing|
|order_oracle expansion-specialist training|Operations and EndTool|Every correct name and the final task-level Done|
|operation_oracle sequence-specialist training|Names and Done|Operations and EndTool for the tool actually selected by the model|

If a sequence specialist selects the wrong tool, the program executes that wrong tool rather than correcting it to the reference. Early Done is also scored wrong. Expansion specialists receive correct names but can still omit operations, miscompute numbers, emit EndTool early, or exceed budget. Parseable incorrect numbers are passed unchanged into subsequent states. All program-supplied segments have training label `-100`, with token-level source-boundary checks. They serve as context for later model tokens rather than counting as correct model predictions.

When program and model alternate, the model is called again from the full saved token history. Each call records actual token IDs, source, prefix length, and SHA256; old KV caches are not reused across program insertions. Explicit newline/EndTool/Done markers determine termination, never the reference operation-line count. The 16-tool cap prevents runaway generation rather than choosing the correct length. For each of four tokenizers, 5136 reference trajectories pass segmented-versus-whole encoding checks. Maximum header/body/full output/input-plus-output lengths are 2/33/282/412 tokens, below limits24/128/2048/4096. See REGISTRATION.md for budgets.

## Data, training, and paired comparisons

Training has 4096 examples:394 single-tool and 3702 two-tool examples, covering 90 programs. Four passes give 16384 examples and 512 optimizer steps. Long-call tests are not used for training. The original 560 tests contain 128 in-distribution,384 unseen long-composition, and 48 stress examples. Another 480 previously fixed independent confirmation inputs comprise 24 programs x4 inputs at each of 3/4/5/6/8 tools. Test inputs have no exact duplicates in training, and long programs do not overlap training programs. The independent confirmation set was fixed earlier, not newly constructed blind after these results. See analysis/data-audit.json for cross-checks.

Each scale x3 training conditions x seeds11/22/33 gives 36 training jobs. Each joint checkpoint receives two oracle evaluations in addition to autonomous inference; the two specialist checkpoints each receive their corresponding oracle evaluation. This gives 60 checkpoint/inference-mode combinations x1040 examples =62400 main trajectories. The 288 outputs per length are 96 inputs across 3 training seeds, not 288 independent programs.

The primary checkpoint is fixed in advance at step512; step64/128/256 are retained, with no test-based checkpoint selection. Conditions share inputs, order, batch, and training steps but differ in supervised-token counts. Over four passes, joint supervision uses 1,001,552 tokens, expansion 890,016, and sequence 111,536. This target-mask intervention does not separately isolate supervision quantity, loss weighting, gradient interference, or explicit modular structure.

The key training comparison is specialist checkpoint + oracle versus joint checkpoint + the same oracle, controlling inference assistance. The key inference comparison is one joint checkpoint + oracle versus the same checkpoint executing autonomously. Directly subtracting joint autonomous scores from specialist oracle scores changes both training and inference, not one causal factor.

## Interpreting products

For one joint model, complete correctness can be decomposed into events A and B, with probability exactly `P(A) × P(B|A)`. Substitution with `P(A) × P(B)` requires an additional statistical-independence assumption.

Here, specialist A and B come from different checkpoints and oracle environments. Comparing paired both-correct events on the same examples with the product of marginal probabilities within each seed checks association between these **test outputs**, not whether the joint model internally contains independent modules. The difference between the product and joint autonomous accuracy also changes training targets and inference environments and cannot be attributed wholly to correlation. Paired both-correct statistics are not an executed two-specialist agent, which was not tested in this study.

## Environment and evidence reproduction

All environments, caches, data, adapters, and logs are in this project. Small models ran on six servers with 8x5090 GPUs;32B ran on local PRO6000 96 GB GPUs. Within-scale comparisons use the same hardware type. Remote servers were returned; do not reconnect using old scheduling files. The ledger is infrastructure/SERVERS.md. Credentials are separated from research artifacts and omitted from public documents.

The shared environment is Python3.12.3, torch2.7.1+cu128, transformers4.51.3, peft0.15.2, accelerate1.6.0, numpy2.2.6. Each run contains config.json, training curves in train.jsonl, adapters in adapter/ and checkpoints/, raw inference in evaluation-*.jsonl, and training/evaluation-complete.json summaries. Package inventories and hashes are in infrastructure/; input/model-config/tokenizer/weight inventories are in analysis/reproducibility-inputs.json. Weight files record sizes and download manifests; SHA256 was not recomputed for every large weight file.

From the project root, rerun read-only result checks and refresh derived reports:

```bash
source training-env.sh
python workspace/research/B01-02/oracle-study/src/data_audit.py
python workspace/research/B01-02/oracle-study/src/reference_budget_audit.py
python workspace/research/B01-02/oracle-study/src/audit_results.py
python workspace/research/B01-02/oracle-study/src/token_replay.py
python workspace/research/B01-02/oracle-study/src/diagnostics.py
python workspace/research/B01-02/oracle-study/src/compare.py
python workspace/research/B01-02/oracle-study/src/products.py
python workspace/research/B01-02/oracle-study/src/product_uncertainty.py
python workspace/research/B01-02/oracle-study/src/mechanisms.py
python workspace/research/B01-02/oracle-study/src/intervention_pairs.py
python workspace/research/B01-02/oracle-study/src/report.py
.analysis-venv/bin/python workspace/research/B01-02/oracle-study/src/plots.py
python workspace/research/B01-02/oracle-study/src/completion_audit.py
```

These scripts neither retrain nor overwrite raw outputs. Plotting uses matplotlib3.10.1 in the existing project `.analysis-venv`, without changing the training environment. src/reproduce.py runs a fresh model process for 120 fixed examples per scale with original batch groupings; records are in analysis/reproduction/. Training and reproduction scripts refuse to overwrite existing output directories. Retraining requires independent runs in a new experiment directory, preserving these results. Full launch arguments and allocations are in infrastructure/allocation.json and logs/.

The only main scheduling change moved the queued 32B sequence-specialist seed33 to free GPU2 for training; the original queue waited for completion and then evaluated it. The main training-function AST is unchanged, as are data, hyperparameters, inference, and scoring. Lease, old source, and error-path checks are recorded. Other later scripts perform offline analysis without changing main outputs.
