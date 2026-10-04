# Relation to prior work (limited novelty check)

This check covered the primary abstracts and official publication metadata below. Context compression, external task state, and learning when to edit/delete memories have clear prior work; these broad ideas are not original findings here.

| Prior work | Existing contribution | Constraint on current interpretation |
|---|---|---|
| [Context as a Tool / CAT](https://arxiv.org/abs/2512.22087), 2025-12 preprint | Separates stable task semantics, long-term memory, and recent interactions, and trains context management. | Hierarchically retaining goals, summaries, and recent actions is not itself new. |
| [InfiAgent](https://aclanthology.org/2026.findings-acl.1787/), Findings of ACL 2026 | Externalizes persistent state into files and reconstructs bounded context from state snapshots and recent actions. | Completing long tasks with a small context already has direct prior work. |
| [Memory as Action / MemAct](https://aclanthology.org/2026.findings-acl.956/), Findings of ACL 2026 | Treats context edits/deletions as learnable actions, using reinforcement learning to optimize information retention and task performance. | Future training of agent context management must be compared with existing memory-policy training; using Agentic RL alone is not a contribution. |

A more specific research lead is whether, with tool protocol, visible clock, input schema, and task budget fixed, model-generated pseudo-role/pseudo-tool observations fed back into history cause reproducible error accumulation and false completion, and whether removing only this invented text while preserving genuine tool history can repair it. Paired evidence exists on small controlled tasks, but generality across models and real tasks remains unestablished.

This distinction is our research judgment, not a difference established by the literature. Only abstracts and metadata were checked; the full papers or other work may already cover this exact failure chain. The current result should be described as reproducible mechanism cases and engineering repairs, with novelty and paper contributions still requiring verification. It should not be presented as a published result, a proven RSI bottleneck, or proof of a unique benefit from name restatement.
