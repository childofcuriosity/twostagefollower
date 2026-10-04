# Native protocol reliability development

Previous agent-study and v3 retained unchanged. Same frozen Qwen2.5-32B-Instruct revision 5ede1c97bbab6ce5cda5812749b4c0bdf79b18dd. No weight training in this stage.

Development set fixed before inference: files/data/code × two new seeds (20261001/2), four requirements each. Compare native zero-shot and one fixed unrelated fully executable demonstration, all six tasks in both conditions. Standard model chat template tools and assistant/tool role sequence, no finish function; final text only terminates after all prior tool results were delivered. 4096 per-turn limit, 8192 total generated tokens for short tasks. No hidden grading feedback to agent. Keep every attempt.

Select on development reliability, then freeze configuration for independent short validation (12 tasks, new seeds), with unchanged independent validators. A successful development run alone is not evidence of held-out reliability. If native changes remain insufficient, diagnose all failures and test justified alternatives, including coding-specialized/larger models. No requirement that the identity intervention must win. Long-task controlled comparison starts after short execution is reliable. Existing tasks are repeated independent requirements, not realistic sequential long workflows; add dependency-rich tasks before making long-agent claims.

This is a bundled engineering comparison to the previous protocol, not a causal estimate of template alone: finish semantics, per-turn output limit and prompting also changed. Zero-shot versus few-shot is paired within the new runtime.

Development result: 6/6 both variants. Freeze zero-shot as primary (no demonstration dependency), before examining independent validation. Evaluate 12 independent short tasks for both variants and original 24 tasks with zero-shot for paired regression; no claim isolating individual runtime changes. Short gate requires at least 11/12 complete and no systemic protocol failure, followed by longer controlled evaluation and broader short confirmation if needed.

Independent short validation: both zero-shot and few-shot 12/12. Original paired regression zero-shot 23/24, retaining code-n12-s3-v2 failure (writes wrappers referring to transient process functions, then finishes without imports/tests). Proceed to all four conditions on 12 frozen new long instances. Also evaluate all 24 original tasks with few-shot, not just the failure, to assess demonstration effect without favorable-instance selection.
