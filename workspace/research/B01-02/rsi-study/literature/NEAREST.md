# Nearest work and potentially distinguishable questions

Literature check dated 2026-09-24, based on original-paper HTML. This is research positioning; absent search results do not prove novelty.

- [Absolute Zero: Reinforced Self-play Reasoning with Zero Data](https://arxiv.org/html/2505.03335v1), 2025. A shared model proposes/solves with joint rewards. Removing proposer training hurts performance, and authors discuss task interference. The need to train proposers and interference across roles are not original here.
- [Towards Understanding Self-play for LLM Reasoning](https://arxiv.org/html/2510.27072v1), 2025. Studies AZR role entropy and frozen proposers. Frozen variants have higher entropy; trained high-budget capability remains constrained by the base. Diversity decline alone is not a new mechanism.
- [Skill Self-Play](https://arxiv.org/html/2607.22529v1), 2026. Skills guide coevolving proposals, solving, and curricula. Skill-specific data can overspecialize; frozen-proposer/feedback-solver variants can hurt. Distinguish positive coevolution from our controlled single-execution-objective separation.
- [From Reasoning Traces to Reusable Modules](https://arxiv.org/html/2606.18089v1), 2026. Studies compositional modules/routing and SFT/RL roles. Initial trajectory labels do not establish open-ended concept discovery.

Differences still to establish: paired execution and independent proposal-utility changes from identical initialization; same-learner counterfactual proposal-source branches; aligned versus shuffled replay; complete counterexamples/failures and scope across prompts, budgets, models, and semantics. Without these, report a bounded observation rather than a new RSI theory.

Additional confound: [Understanding Catastrophic Forgetting in Language Models via Implicit Inference](https://arxiv.org/html/2309.10105v2), ICLR 2024. Fine-tuning can change implicit task inference, and prompts recover some apparent forgetting. Decline under three prompts does not prove parameter knowledge disappeared. We measure usable proposal utility under finite budgets and do not exclude other prompt recovery.

Sampling-budget reference: [Does Reinforcement Learning Really Incentivize Reasoning Capacity in LLMs Beyond the Base Model?](https://arxiv.org/abs/2504.13837), 2025. Uses high sampling budgets to compare base/trained coverage. Our K curves borrow that evaluation idea without claiming novelty or directly transferring RL conclusions to LoRA execution SFT.
