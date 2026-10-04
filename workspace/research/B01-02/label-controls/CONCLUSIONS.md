# Label controls: final research conclusions

The bounded goal is complete: only position numbering and fixed arbitrary aliases were added, with 24 training/evaluation runs across four scales and three training seeds. Original STEP and Original NAME were reused read-only. The aim was to test whether gains on long execution require output progress cues, stable tool identity, or usable name forms, without assuming an identity explanation.

## What we ran

Qwen2.5 Base models at 1.5B/3B/7B/32B, using the original first-stage training configuration: 4096 training examples, 512 update steps, microbatch16 x accumulation 2, LoRA r16/alpha32, and learning rate 3e-4. Training contains only 1–2 tool calls, with the tool order supplied in the input. Models learn to execute nine fixed tools in sequence, rather than plan autonomously or invent tools.

- Original STEP outputs `step:` for every call: a boundary without output identity.
- Original NAME outputs `red:` and similar names: a boundary with identity.
- New position labels output `step1:`, `step2:`, and so on: boundaries and positions without output identity. Training has no third call, so use of `step3:` as a call heading is untrained.
- New aliases assign each tool a fixed random name from `toolA` to `toolI`, consistently renaming both input and output while preserving identity. One mapping is shared across all scales and training seeds.

All conditions still end with the original `Answer:`, without EndTool/Done, oracle-correct content, or changes to the training algorithm. Both added conditions have 271656 supervised target tokens per pass, 2.96% more than the original-name condition; alias inputs are longer too. These differences accompany the representation change, so token-length and tokenization effects are not fully excluded.

## Complete-task results

The table reports mean full-trajectory accuracy across three training seeds on the earlier independent 480-example test set: 96 examples each at lengths 3/4/5/6/8. Correctness requires the raw operation sequence, every numerical state, and the final Answer; labels are scored separately. The additional label-correct full-success score equals the primary score in this table. The 480 examples are 24 programs x 4 inputs x 5 lengths; inputs sharing a program and the three seeds are not all independent samples. This is also a previously used test set, not a fresh blind test.

|Model|Original STEP|Original NAME|Position numbering|Fixed aliases|
|---|---:|---:|---:|---:|
|1.5B|0.00%|16.25%|0.00%|16.81%|
|3B|0.00%|36.88%|0.97%|52.92%|
|7B|12.15%|37.01%|19.86%|58.33%|
|32B|25.63%|56.18%|39.17%|31.18%|

At length 8:

|Model|Original STEP|Original NAME|Position numbering|Fixed aliases|
|---|---:|---:|---:|---:|
|1.5B|0.00%|1.04%|0.00%|0.00%|
|3B|0.00%|2.08%|0.00%|10.07%|
|7B|0.00%|0.00%|0.00%|26.04%|
|32B|0.00%|24.65%|0.35%|0.69%|

On the original iid short-task test, all four conditions average 100% at all four scales. Alias models therefore can learn tasks at training lengths. This does not establish preserved general language ability.

Means alone are insufficient. Fixed aliases minus Original NAME gives seed differences of −9.38/+10.21/+0.83 percentage points at 1.5B; +17.92/−1.88/+32.08 at 3B; +32.71/−20.21/+51.46 at 7B; and −8.75/−11.04/−55.21 at 32B. All three 32B seeds show a disadvantage, while smaller-model mean advantages are not consistent across seeds. Position numbering minus STEP at 32B is +18.54/−0.62/+22.71, also short of a consistent improvement.

## Why this is not simply about attending to names

Original NAME and aliases both have input name = output name. The comparison changes the form of identity representation, not whether names match. Weaker aliases at 32B suggest name form may matter, but tokenization, the shared tool prefix, pretrained representations, input length, and supervised-token weighting remain possible explanations. The attention mechanism is not isolated.

On the same original ood set of 384 examples at lengths 3–5, the retained evaluation procedure also supplies tool definitions in the input. Three-seed means for the same examples and checkpoint are:

|Model|Input|Original STEP|Original NAME|Position numbering|Fixed aliases|
|---|---|---:|---:|---:|---:|
|7B|Without definitions|17.97%|57.90%|30.56%|74.13%|
|7B|With definitions|16.67%|50.09%|30.12%|42.01%|
|32B|Without definitions|44.27%|73.00%|58.77%|48.78%|
|32B|With definitions|63.45%|71.70%|81.16%|81.77%|

The 32B alias difference relative to Original NAME changes from −24.22 to +10.07 percentage points. This limits claims that Original NAME is universally better and suggests an interaction between name representation and access to knowledge. The opposite direction at 7B also rules out a claim that providing definitions always helps. These are supplementary evaluations already in the original protocol, not new training or checkpoint selection.

On the earlier independent 32B test, each condition has 1440 trajectories. Original NAME has 827 correct label sequences, including 809 fully correct executions; position numbering has 781 correct heading sequences, including 564 fully correct executions; aliases have 485 correct name sequences, including 449 fully correct executions. Even with every position label correct, the model can execute the wrong tool, so inability to write step3 cannot explain every failure. Statistics conditional on outputs have selection bias and serve as behavioral diagnostics, not unbiased causal effects or independent subtask probabilities.

## Reviewed examples and counterexamples

Using fixed random seed 2026092603, up to 3 cases were drawn from each improvement/degradation stratum, totaling 97. Success-rate denominators use all records. The examples below are not used as selected-case effect estimates:

- 32B alias failure relative to Original NAME, seed33/id100182: toolE→toolG→toolD→toolF is required, but toolD is skipped. Original NAME completes the same example correctly.
- 32B position failure relative to Original NAME, seed22/id100035: step1/2/3 are correct, but the third segment expands red as the rot/inc/swap operations of pink instead of rot/inc. The numerical computation itself is correct. Correct heading counts do not guarantee correct tool execution.
- 7B alias improvement, seed33/id100431: all 8 tools are executed correctly. Original NAME misses the repeated brown call and incorrectly expands the internal operations of white.
- 7B alias degradation, seed22/id100005: for toolF→toolC→toolF, the model executes only the first two calls before Answer; Original NAME completes all three. Aliases do not eliminate the earlier early-stopping pattern.

Full raw text, prompts, and scores are in [paired cases](analysis/paired-cases.json). Within-emitted-segment metrics use the required position rather than the tool identity actually written by the model. They are not accuracy on all required calls under oracle conditions and must not be combined directly with the previous-stage subtask products.

## Interpretation and next steps

The most defensible conclusion is: **The specific output-label representation substantially affects generalization from short training tasks to long execution. Effects depend on model scale, name form, and whether tool definitions are supplied. Position numbering alone does not reproduce all name benefits, and stable identity does not make arbitrary names equivalent.**

This supports further study of how output identity binds the next segment of operations. It does not establish independently learned two-stage components or an attention mechanism, nor improved persistence in real agents or RSI. Alias success in smaller models shows that the original color words are not universally necessary; alias degradation at 32B shows that stable identity is not unconditionally sufficient across representations. Without a boundary-free control, the causal effect of boundaries has not been isolated.

A recommended next study would focus on 32B, retain the task and budget, and use multiple fixed mappings with names matched for token length and distinguishability. It would test reproducibility of the representation-form x definition-availability interaction and separate input retrieval from output repetition. This study ran only the two authorized added conditions, without starting that extension or modifying training to obtain uniformly positive results. The application implication is to consider clear task identities together with accessible operation definitions, rather than recommending that every agent repeat arbitrary numbers.

[All lengths and seeds](REPORT.md) · [Summary and paired differences](RESULT_DIGEST.md) · [Figure](figures/label-controls.png) · [Supplementary evaluations](AUXILIARY_EVALUATIONS.md) · [Stopping behavior](BOUNDARY_DIAGNOSTICS.md) · [Completion audit](COMPLETION_AUDIT.md) · [Reproduction and costs](REPRODUCTION_AND_COST.md)
