# Mechanistic claims, formalization, and identifiability

## Three distinct quantities
E(θ) is accuracy on a fixed execution distribution. P(θ) is utility of abstractions proposed on unseen tasks and selected using support data under a fixed candidate budget. G(θ, p) is fixed-test learning gain when proposal source p supplies training data to the same initial learner θ. Rising E with falling P is capability separation. Only an intervention on p that changes G connects proposal degradation to subsequent learning obstacles. Negative E/P correlation cannot substitute for this experiment.

Each round follows θ_{t+1}=Update(θ_t, Data(Select(Proposal(θ_t,S_t)))). Freezing the proposer replaces only parameters inside Proposal while retaining executor, selector, and learner budgets. A three-round loop still depends on a human-designed DSL, distribution, and exact executor; it is not open-ended RSI.

## Local gradient condition: an explanatory tool, not a new theorem
For execution loss L_E and differentiable proposal surrogate L_P, a small step θ'=θ−η∇L_E gives L_P(θ')−L_P(θ)≈−η〈∇L_P,∇L_E〉. A negative inner product permits an execution-loss descent step to increase proposal loss at first order. Actual optimization uses AdamW and finite steps, and the surrogate differs from sampled/selected utility P; the local inner product is not directly a long-term causal mechanism.

Primary causal evidence comes from same-start proposal-source branches and replay/joint versus shuffled-replay controls. Gradient angles are diagnostic. Absence of conflict should count against the simple local-gradient explanation, rather than trigger selection of favorable batches.

## Alternative explanations and controls
- Format/prompt mismatch: three prompts, grammar constraints, complete fixed-budget curves, and retained raw outputs.
- Sampling concentration rather than lost capability: K=4/16/64 and temperature 1.5. If larger budgets close the gap, describe lower finite-budget efficiency only.
- Extra supervision/compute: equal execution-example counts; auxiliary conditions add four proposal examples with full token accounting. Shuffled replay has the same prompt/target sets. Winning mixed objectives do not imply equal-compute optimality.
- Task diversity or curriculum changes: preserve proposals, libraries, training programs, and semantic coverage each round. Counterfactual branches fix learner starts to separate path dependence.
- Environment-provided training truth: supervision comes partly from an executor, so the loop is not purely model-generated bootstrapping.
- Strings and numbers share abstraction syntax but differ in execution semantics; they are not fully independent natural-task categories.

There is still no general natural-corpus SFT control, real-code benchmark, or large-model RL training. Even support for H1/H2/H3 would establish controlled closed-domain evidence only, neither excluding general forgetting nor proving a bottleneck in all RSI systems.
