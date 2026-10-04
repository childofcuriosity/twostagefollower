# The two execution-training recipes are not equivalent

Stage A shows proposal degradation; the stage-B shared loop has not shown the same pattern. This limits scope rather than identifying a single causal factor.

| Dimension | Stage A: original macro-call training | Stage B: closed-loop execution training |
|---|---|---|
| Input | Macro-name chain without definitions | Explicit primitive-operation sequence |
| Output | Group labels plus primitives/states | Primitives/states without macro-name groups |
| Library | Nine fixed original model proposals | Up to three selected proposals per each of 12 families per round |
| Primitive coverage | Original library omits ends; separate coverage control | Selected library plus 20% uniform primitives; primitives only for empty libraries |
| Length | 1–2 macro calls | 2–3 selected fragments/primitives |
| Learning rate | 3e-4 with warmup/cosine decay | Constant 1e-4 |
| Updates | 512 steps × 32 examples = 16,384 presentations | Three rounds × 128 steps × 16 examples = 6,144 presentations |
| Optimizer | One continuous AdamW run | AdamW rebuilt each round; parameters retained |
| Evaluation | Unseen macro compositions without a library | Fixed unseen functions/family programs with primitive plans in the input |

Neither restoring primitive coverage nor supplying explicit plans alone has been shown to prevent degradation. The coverage experiment isolates one factor; other differences lack a full factorial analysis. Stage B has real parameter updates in a loop but does not recursively repeat the exact stage-A recipe.

P measures symbolic-reuse compression; G measures next-round neural execution-learning gains. Higher P need not produce a better curriculum for the current learner. Proposal-source interventions report G without substituting P. Even G differences require examining changed program lengths, semantic coverage, and training tokens before invoking a broad property such as innovation.
