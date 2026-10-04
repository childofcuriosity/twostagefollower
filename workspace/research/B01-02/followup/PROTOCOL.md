# B01-02 follow-up: does training improve abstraction-proposal utility?

The user authorized continuation. This protocol was fixed before proposal generation and result inspection.

## Hypothesis and scope
Compare frozen Qwen2.5-1.5B with earlier flat/macro checkpoints from three seeds on reusable-subprogram proposals for independent families. Earlier training supervised execution traces, not proposal policies. Test whether one execution-learning stage transfers naturally to utility, without claiming complete multi-round improvement. The artificial DSL does not establish scientific innovation.

## Independent task distribution
Use seed 91407 to build eight families, each with three inequivalent hidden length-2–3 subprograms, semantically distinct from the old nine macros. Mix these with random primitives. Each family has 16 support and 128 test traces, with AST and exact affine-function separation across support/test. Weight families equally. A correct executor supplies shared support traces; these are not model-solved successes. Models see primitive sequences without hidden boundaries or test data.

## Proposals and budgets
Run frozen base, flat, and macro three times with paired seeds 11/22/33; base repeats change sampling, not model identity. Add macro mismatched-context controls using another family cyclically for proposal context but original support for selection. Each method proposes 16 times per family. A finite-token trie restricts six-primitive programs to lengths 2–3, totaling 252 candidates, at temperature 1. Semantically invalid and duplicate proposals consume budget without replacement. Grammar removes earlier format failures while limiting open-ended discovery; disclose both.

Random controls independently draw 16 candidates uniformly from the same space. All proposal methods use the same support-set greedy compression rule to choose up to three semantically distinct, nonidentity macros with positive net gains. Tests never guide selection. Frequency heuristics count all support 2/3-grams, take 16, and apply the same selector; search compute differs. Greedy selection from all 252 candidates is another reference, not a globally optimal upper bound.

Equal budget means 16 proposals, a shared selector, and downstream verification, not equal LM/random/heuristic compute. Retain raw generations, candidates, seeds, and costs.

## Metrics
Primary: proportional description-length reduction on unseen test traces. Dynamic programming counts primitives and macro calls as one token each and subtracts one-time definition cost sum(len(macro)+1), also on support. Only exact contiguous primitive replacement is allowed, not arbitrary semantic rewriting. This measures reuse compression, not model accuracy.

Secondary: fixed deterministic breadth-first search with primitives and selected macros as actions, deduplicated by exact affine signature. Budget: 3000 action expansions; a macro counts as one, with actual primitive executions reported separately. Targets are complete functions of 128 test programs. Record discovery rate and steps. Order primitives first, then macros by index. This is not neural search; targets never enter proposing/selection. Compare no-macro, random, model, and heuristic sources. Fix the budget before results rather than tuning for significance.

Primary paired comparisons: macro−flat, macro−base, macro−random. Report families/seeds and bootstrap over eight family clusters conditional on checkpoints; proposals are not independent training seeds. Screening requires macro−random compression ≥2 points, positive differences for all three seeds, and search discovery no more than two points below random. Passing supports bounded-domain utility only. Failure stops expansion of this route. Gains over base without gains over flat/mismatched context cannot be attributed to macro organization or task adaptation.

## Expected resources and stopping
Reuse checkpoints for 12 proposal jobs, including three mismatch controls, with no new parameter training. Expect under two GPU-hours, CPU analysis separate; record actual costs. No replacement sampling of failures or test-based hyperparameter changes. Report completion and await review.
