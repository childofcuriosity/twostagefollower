# Research plan: can task-identity repetition reduce premature agent termination?

Status, 2026-09-24: user-supported proposal, prioritizing tens-of-billions scale validation in stage one. No new training/agent evaluation has started. [SCALE_AMENDMENT.md](SCALE_AMENDMENT.md) supersedes the original small-model mechanism schedule. Existing results motivate the study. Keep assets, environments, and logs project-local.

## 1. Question and draft revisions

When local actions are within capability, tools work, and budget remains, do agents stop before satisfying requirements? Does binding each action to stable requirement identity reduce early termination and improve actual completion rather than merely lengthen output or create loops?

Frequent midway stopping by Codex-like agents is a user observation, not a representative quantitative fact about products. Separate early termination, mistaken completion, legitimate blocks, and tool failure without assuming laziness, deliberate hacking, or reward gaming.

Treat repetition effectiveness as a hypothesis. Existing evidence concerns short-to-long single-generation generalization, not interactive agents. The intervention appears in both SFT and inference, so it does not establish inference-only reminder gains.

Tools and tasks have different identities: shell may serve 20 tasks. Naming shell does not identify remaining requirements. The primary method states current requirement ID/name, optionally the tool. Ablate project name, tool name, task identity, and remaining lists separately.

Working hypothesis: local identity tied to original requirements helps maintain progress and termination criteria, reducing avoidable stopping. Discuss indirect long-autonomous-research/RSI implications only after evidence.

## 2. Evidence, gaps, and nearby work

Across three models × three seeds on 560 tests, first-stage analysis selects 1,473 macro-answer-correct/flat-answer-wrong records covering 370 IDs. Of these, 1,297 execute two tools correctly then answer; all 1,473 flat outputs have two segments without hitting caps. Training has 3,702 two-call examples out of 4,096. This conditional behavior is neither overall failure incidence nor identified causation. Twenty-five macro cases have correct answers without matching processes; also use strict trajectories.

Nearby sources, distinguishing publications, preprints, and engineering articles:

- Plan-and-Solve Prompting, ACL 2023: planning before execution and omitted steps. Planning first is not original. https://aclanthology.org/2023.acl-long.147/
- AgentBoard, NeurIPS 2024: fine-grained progress/final success; use state-based progress measures. https://proceedings.nips.cc/paper_files/paper/2024/file/877b40688e330a0e2a3fc24084208dfa-Paper-Datasets_and_Benchmarks_Track.pdf
- The Impact of Positional Encoding on Length Generalization, NeurIPS 2023: intermediate-step formatting affects generalization; the toy effect may concern formatting/indexing. https://proceedings.neurips.cc/paper_files/paper/2023/hash/4e85362c02172c0c6567ce593122d31c-Abstract-Conference.html
- The Unreliable Progress Bar, September 2026 preprint: progress-report reliability across stages, including τ²-bench/StageIF. Reporting progress does not guarantee correctness. https://arxiv.org/abs/2609.08589
- When May an Agent Stop? Evidence-Carrying Termination for Tool-Using LLMs, August 2026 preprint: evidence/replay control COMPLETE. Compare soft prompts and external gates; forbidding stopping does not establish a better model through zero early stops. https://arxiv.org/abs/2608.23623
- Anthropic engineering, Harness design for long-running application development, March 2026: decomposition, handoffs, completion criteria, and early wrap-up near context limits. https://www.anthropic.com/engineering/harness-design-long-running-apps
- Official ThinkingBox overview: assertions verify actual completion. Review public data, dependencies, and version pinning before using it. https://commandline.microsoft.com/thinkingbox-bench-agent-benchmarking/

Potential contribution: isolate original-plan identity from label diversity, positions, extra text, and generic reminders. Establish low-cost frozen-model completion gains in real interaction with explicit limits, rather than claiming discovery of early stopping or plan tracking.

## 3. Falsifiable hypotheses

H1, behavior: voluntary incomplete termination on feasible, sufficiently budgeted long tasks is reproducible and distinct from local errors.
H2, identity: stable identities linked to input plans reduce early stopping more than equal-length generic reminders or unlinked labels.
H3, deployment: brief identity repetition improves completion through inference protocols without weight updates.
H4, cost: gains survive token/call accounting without materially increasing post-completion loops, repeated side effects, or blind continuation under legitimate blocks.

Failure interpretations differ: failed H2 does not refute generic tracking; failed H3 rules out plug-and-play prompting claims. Narrow short-training effects concern distribution bias. Hard-gate-only gains belong to controllers, not identity repetition.

## 4. Defining early termination

Every task has visible requirements and program-verifiable final conditions. Tools/environment log events; hidden evaluation reads states/trajectories rather than model-reported done.

Primary event: a terminal response with required items unmet, no external block, and remaining preallocated budget. Controlled feasibility is constructed; real tasks require prior review and independent annotation. Unknown feasibility is separate, not labeled avoidable.

Exclusive endings: true completion; voluntary incomplete termination; token/action/time exhaustion; legitimate need for input/permission; infrastructure/tool failure. Separately record false completion claims. A progress message while background work continues is not termination.

Success includes timely stopping. Redundant calls, state-neutral loops, repeated writes, and unnecessary retries after completion count as costs/risks. Persistence cannot override safety/permission boundaries.

## 5. Stage A: minimal mechanism separation in the original environment

Test two-segment template reinforcement versus identity association. Fix data, initialization, primitives, steps, and states, varying segment markers. Match tokenizer lengths or disclose mismatches and add matched controls.

Five primary groups:
A0: uniform step labels.
A1: random distinct segment labels unlinked to input tools, resampled per example to prevent alternative tool-name learning.
A2: positions only, such as slot01/slot02, anticipating unseen-index vocabulary confounds.
A3: matching arbitrary tool IDs in input/output without required natural-language meaning.
A4: A3 plus positions to distinguish repeated tool calls.

Small diagnostics add consistent input/output renaming and output-only mismatches; deliberately wrong prompts are not strong primary baselines. If index vocabulary matters, use development-fixed compositional encodings rather than post-test changes.

Training has 1–2 calls; fix tests at 3/4/5 and longer 6/8. Old 384 examples replicate history; fresh training-semantically-disjoint programs confirm mechanisms. Report segment counts, full traces, first divergence, and stopping positions. Primary contrasts: A3−A1 and A3−A2, not only weakest A0.

Start five groups with original 1.5B and three seeds; replicate surviving findings in another family. Random diverse labels matching identities narrows explanation to template diversity. Add broader training-length distributions only for key pairs, matching supervised tokens to test 1–2-call bias. Register changes separately.

## 6. Stage B: frozen-model real interaction, priority investment

Use a tool-capable 7–14B instruction model plus a similarly capable other-family model. Freeze checkpoints/revisions before running based on compatibility, licenses, and local capability. A 1.5B base unable to call tools is not evidence of a long-horizon deficit. Paid APIs are not assumed; current servers offer eight approximately 96-GiB PRO6000 GPUs. Proprietary replication is an optional separate cost.

First target ≥90% development single-task completion. If unmet, simplify local operations or strengthen the model rather than lengthen tasks for low scores. Share loops, schemas, retries, context limits, and text/structured formats; verify compliance. Do not automatically block finish or use hidden truth to fill remaining work in primary trials.

Example produced by the model, not the hidden evaluator:
Current requirement: T07, add missing export fields to the inventory module.
Tool: edit_file.
Completion evidence: export function and related tests updated; cite visible evidence only.

Minimal intervention adds only current ID and short name. Add remaining lists/evidence separately to preserve attribution. Keep status in next-turn context without exposing private reasoning or flooding users with per-step updates.

Primary conditions:
B0: ordinary agent explicitly instructed to complete all requirements.
B1: same initial plan, written once.
B2: B1 plus equal-length generic continue/check reminders.
B3: B1 plus tool-name repetition each step.
B4: B1 plus current task ID/name repetition, the minimal primary method.
B5: B1 plus an updated conventional checklist, a strong practical baseline.
B6: B4 plus self-maintained remaining work/evidence, an extension distinct from B4.
B7: deterministic external completion gates, a verifiable-system reference rather than a same-information primary comparison.

Two levels: B1–B6 share a user-supplied checklist for mechanism tests, isolating planning. End-to-end tests let models plan and retain omitted requirements. Evaluate original user requirements, not model plans. Dependent tasks do not reveal optimal action sequences.

Compare fixed budgets, charging status text to generated tokens. Plot success against token/call costs; cap calls and record repeated-prefix inputs/context. Extra reasoning/calls are not pure formatting gains. Meaningless padding does not establish exact compute matching.

## 7. Task design

Three reproducible local families:
1. File batches: modify multiple files under explicit rules, including repeated tool use; verify every result and untouched unauthorized files.
2. SQLite/CSV workflows: clean data, maintain constraints, generate statistics, and validate outputs, including dependencies/branches rather than only independent actions.
3. Small repositories: requirements span modules, configuration, tests, and docs. Hidden tests plus file states verify completion. Keep tests outside agent-writable areas, without shortcuts through deleting tests or changing acceptance.

Use 4/8/16/32 requirements as length, recording calls independently. Separate independent lists/dependent tasks, including actions contingent on tool results. Hold local difficulty stable rather than increasing algorithm complexity with length.

Start clean. Later add recoverable errors, distracting logs, long context, and compression separately. Include complete, impossible, and user-input-required stop controls to detect endless-continuation side effects.

For external validity, assess offline-verifiable ThinkingBox/AgentBoard workflows first. Do not distort single-question benchmarks for scale. Prerecord selection criteria, versions, licenses, and environments rather than choose favorable benchmarks after results.

## 8. Initial scale, analysis, and stopping

Development smoke: 24 tasks (three families × two lengths × four instances), one model, B1/B2/B4/B5 = 96 trajectories. Check environment, budget, local ability, and failure types; these are not final significance evidence.

First locked batch: 96 fresh tasks (three families × four lengths × eight instances), B1/B2/B4/B5, two models, three decoding seeds = 2,304 trajectories. Schedule B0/B3/B6/B7 and extra mechanisms under development-fixed protocols, not favorable formal results. This feasibility batch does not guarantee power for five-point effects.

If consistent signals emerge, provisionally confirm on 400 family/length-stratified instances. Lock size through development-based paired-power simulation before opening confirmation. Hold generator variants out by template and cluster at the highest dependence level. Seeds are not independent tasks. Hold small real repositories out at least by repository and report wide intervals.

Primary: true completion of every requirement. Key secondary: voluntary incomplete termination. Report false completion, requirement fractions, budget exhaustion, legitimate blocks, post-completion loops, tool failures, and token/call/wall-time costs. Longer outputs/self-reported progress are not success.

Primary contrasts B4−B2 and B4−B5 compare identity with equal-length reminders and checklists. Use paired task/template bootstrap or permutation intervals, with prespecified comparisons/multiplicity handling. Report all lengths/families and model versions separately; seeds do not inflate sample size.

Tentative practical threshold: ≥5-point confirmation gains in at least two families, paired 95% lower bounds >0, reduced early stopping, ≤20% additional generation, and no deterioration beyond a prespecified two-point margin for post-completion loops/repeated actions. Lock after development, not reset from formal results. Without budget-curve advantage, more success from extra calls is not a low-cost repair.

If development early stopping <5%, stop treating it as the main cause. For tool inability/infrastructure failures, improve ability/environment instead of forced persistence. B4 not beating B5 is ordinary-tracking replication. Narrow-training-only effects do not generalize to real agents. Longer loops without better accepted completion mean failure.

## 9. Causal diagnostics and completion calibration

Copy trajectories from prespecified identical intermediate states; randomize identity, generic reminder, checklist, or no reminder. Compare next-action continue/stop and later accepted gains. Use condition-independent collection and task stratification, not states selected to defeat one method. Intermediate branches are not end-to-end gains.

Separate recovery tests compare “continue,” specific omissions, and identity from identical post-termination starts. Simple continuation recovering all gains weakens identity-specific value. Charge extra turns separately from primary no-user-intervention evaluations.

Check claimed-complete requirements against visible evidence/state for false checkmarks, omitted plan items, and repeats. Offline stop-choice probes on some complete/incomplete/blocked states distinguish knowing work remains from not knowing what remains, but answers are not real agent behavior.

Randomized behavioral intervention is primary causal evidence. Consider internal probes only after stable effects rather than prioritize attention heatmaps.

## 10. Is training needed?

First test frozen instruction-model prompting/protocol gains. If effective without training, inference protocol is the contribution; if SFT is needed, revise claims.

If necessary, render identical successful interaction traces with ordinary, diverse, and identity labels, keeping actions/results fixed. Use three-seed LoRA with matched budgets, IID/longer tests, and ordinary language/tool-following controls. Short execution training plus unrelated proposal tests does not establish innovation gains. Ablate gates, SFT, and extra long-horizon training separately.

## 11. Resources, delivery, and review

Estimates: environment/smoke 1–2 working days; mechanisms/frozen primary tests another 2–4; confirmation/public transfer 3–7. Total roughly 1–2 weeks depending on environment quality/trajectory length. Initial smoke cap: eight GPU-hours. After calibration, budget model × condition × task × seed × mean duration. Full local stage may need 50–200 GPU-hours. If exceeded, reduce models/nonprimary controls rather than shrink until significant. No paid external services by default.

Deliver specifications/independent validators, frozen prompts/plans, baseline stopping audits, all traces/end reasons, model/length/family results/cost curves, successes/failures, primary intervals, and a continue/drop judgment.

The user supports this direction and plan, prioritizing stage-one 32B validation per the amendment. Proceed within approval with infrequent stage-based checks. This is a plan, not a claim these experiments have run.
