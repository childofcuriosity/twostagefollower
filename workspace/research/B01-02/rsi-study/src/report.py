from common import *
import statistics,time
r=json.loads((ROOT/'analysis/robust-results.json').read_text());l=json.loads((ROOT/'analysis/loop-results.json').read_text());v=json.loads((ROOT/'analysis/verification.json').read_text());infer=json.loads((ROOT/'analysis/loop-inference.json').read_text())
assert r['completed_runs']==27 and l['completed_loops']==24 and len(l['branch_rows'])==18
cost={}
for phase in ['replications','robust','loops','branches','gradients','coverage','length','legacy','timecourse','original-gradients']:
 jobs=json.loads((ROOT/f'analysis/{phase}-completed.json').read_text());assert all(j['returncode']==0 for j in jobs)
 cost[phase]=sum(j['wall_seconds'] for j in jobs)/3600
(ROOT/'analysis/cost.json').write_text(json.dumps(dict(reserved_gpu_hours_by_phase=cost,total=sum(cost.values()),note='Sum of subprocess wall time on one GPU each; includes loading, CPU preparation and evaluation, not kernel busy time; excludes download and waiting for prerequisites.'),indent=2))
def pc(x):return f'{100*x:.2f}%'
def pp(x):return f'{100*x:+.2f}'
exec_table=[]
for m in ['qwen1.5b','qwen3b','smol1.7b']:
 for c in ['flat','macro']:
  base=PARENT if m=='qwen1.5b' else ROOT/'replications'/m
  ev=[json.loads((base/f'runs/{c}-original-s{s}/summary.json').read_text())['evaluation']['groups'] for s in [11,22,33]]
  p=r['summary'][m]['instruction-t1.0-k16'][c];bp=r['summary'][m]['instruction-t1.0-k16']['base']
  exec_table.append(f"| {m} | {c} | {pc(statistics.mean(x['iid']['accuracy'] for x in ev))} | {pc(statistics.mean(x['ood']['accuracy'] for x in ev))} | {pc(bp['compression'])} → {pc(p['compression'])} |")
loop_table=[]
for d in ['digits','strings']:
 for c,data in l['summary'][d].items():
  before=data['0'];after=data['3']
  loop_table.append(f"| {d} | {c} | {pc(before['proposal_compression'])} → {pc(after['proposal_compression'])} | {pc(before['short_accuracy'])} → {pc(after['short_accuracy'])} | {pc(before['family_accuracy'])} → {pc(after['family_accuracy'])} | {pc(after['family_program_accuracy'])} |")
branch_table=[]
for d,stats in l['branch_comparisons'].items():
 for split,value in stats.items():branch_table.append(f"| {d} | {split} | {pp(value['base_source_minus_updated'])} | {' / '.join(pp(x) for x in value['seed_differences'])} | {' to '.join(pp(x) for x in value['t_interval_95'])} |")
grad=[]
for p in (ROOT/'runs').glob('gradient-*/results.json'):
 z=json.loads(p.read_text())
 for row in z['records']:grad.append({**z['args'],**row})
gtable=[]
for c in ['shared','joint']:
 for rnd in range(4):
  rs=[x for x in grad if x['condition']==c and x['round']==rnd];gtable.append(f"| {c} | {rnd} | {statistics.mean(x['cosine'] for x in rs):+.4f} | {sum(x['cosine']<0 for x in rs)}/{len(rs)} |")
text=f'''# Execution learning and improvement capability: extended results

Generated at (UTC): {time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}. This user-authorized RSI extension has completed actual model/data experiments and awaits consolidated review.

## Research question and interpretation

Distinguish execution performance E under a given prompt, abstraction utility P under a finite proposal budget, and actual learning gain G after the proposal source shapes next-round training data. E rising while P falls does not imply falling G or the impossibility of open-ended RSI. See [MECHANISM.md](MECHANISM.md) for counterexamples and limits.

Interpretation is in [CONCLUSIONS.md](CONCLUSIONS.md). This report retains the full design and main tables without selecting favorable models, prompts, rounds, or domains.

## Actual scale

- Three models across two families: Qwen2.5-1.5B, Qwen2.5-3B, SmolLM2-1.7B. The latter two were downloaded with fixed revisions/hashes for this round.
- Initial-setting replication adds twelve 512-step LoRA runs and two frozen execution baselines, reusing six original 1.5B adapters.
- Robustness: 27 jobs, base/flat/macro with three seeds per model, three prompts plus a temperature check, and 16 fresh test families with 64 proposals each. K=4/16/64 use prefixes of the same sampled sequence.
- Closed loop: 24 three-round trajectories, five numeric-domain conditions × three seeds and three string-domain conditions × three seeds. Each round has 128 steps and batch 16; rounds 0–3 are retained.
- Twelve prespecified same-start causal branches and six post hoc degraded-proposer stress branches, each with 128 steps. Six closed-loop and three original-recipe gradient diagnostics do not update parameters. Original macro training is repeated for three seeds with checkpoints 0/16/64/128/256/512. Three length-matched primitive-coverage runs and 27 proposal-length-quota controls are explicitly post hoc.
- Total: {v['raw_proposals']:,} actual proposals and {v['raw_execution_records']:,} example-level execution records. Repeated measurements of one example/model are not equally many independent samples.
- Audited {len(v['checkpoint_sha256'])} adapter hashes; approximately {sum(cost.values()):.2f} allocated GPU-hours, excluding downloads/prior waiting and distinct from kernel-active time.

## Multi-model execution and proposal controls

Execution uses the original macro-call task; proposals use 16 new test families. Primary proposal settings are instruction, T=1, K=16. Values average three seeds; base seeds vary sampling, not base-model training.

| Model | Training format | IID execution | Unseen-composition execution | Net proposal compression: base → trained |
|---|---|---:|---:|---:|
{chr(10).join(exec_table)}

![Proposal budget](figures/proposal-budget.png)

![Prompt robustness](figures/prompt-robustness.png)

Full seed/family differences and family bootstrap results: [robust-results.json](analysis/robust-results.json). Frozen execution baselines have format limitations; increased trained IID accuracy alone does not establish newly acquired internal algorithms. Tokenizers differ, so equal steps/examples need not yield equal supervised tokens; see actual counts in the [audit](analysis/verification.json).

## Three-round closed loop

Stages A/B differ in input representation, task distribution, learning rate, and update amount; see [RECIPE_COMPARISON.md](RECIPE_COMPARISON.md). Absence of degradation in B limits the phenomenon’s scope but identifies no single protective factor.

Each round, models propose 16 candidates from support programs in 12 training families. Support-set greedy selection chooses at most three macros, shaping next-round execution-training operation distributions. The environment supplies execution truth; test families never enter training. Training and fixed evaluation programs are exactly semantically disjoint.

shared: one updated model continues proposing and executing. frozen: the initial base proposes while the executor updates. replay: shared plus initial-proposal replay. joint: shared plus supervision on proposals selected from current support. shuffled: replay targets are reassigned to prompts within equal-token-length buckets. Auxiliary loss weight is 0.2 with four extra examples per step; every condition has 16 execution examples. Auxiliary methods add compute, so total compute is unequal.

| Domain | Condition | Net proposal compression: round 0→3 | Short-program execution: round 0→3 | Unseen-family execution: round 0→3 | Round-3 exact primitive sequence |
|---|---|---:|---:|---:|---:|
{chr(10).join(loop_table)}

![Three-round trajectories](figures/loop-trajectories.png)

Frozen proposal metrics come from the actual frozen proposer. Preservation is structural, not learned by the executor. Optimizers restart each round while adapter parameters carry forward. All rounds are reported without test-based checkpoint selection.

Short string inputs permit chance-correct answers; also inspect exact primitive sequences and the [copy-input baseline](analysis/loop-inference.json). Domains share primitive names and family ASTs but differ in execution semantics; they are not fully independent natural-task categories.

## Causal branches from identical learner starts

From the same shared round-1 adapter, copy two 128-step branches, changing only proposal source: the updated model or initial base with LoRA disabled. Support, selector, executor, training seed, and learner start match; starting hashes are verified pairwise.

The table reports final execution for base-source minus updated-source. Positive values favor retaining the initial proposer. Identical starts make these learning-gain differences too. Three-seed t intervals can be wide.

| Domain | Evaluation | Mean difference (percentage points) | Three seed differences | 95% t interval |
|---|---|---:|---|---|
{chr(10).join(branch_table)}

![Proposal-source intervention](figures/causal-branches.png)

Branches match execution-example counts and optimization steps, but selected program lengths change training tokens/difficulty. This is the total proposal-source effect through curriculum, not pure information quality at equal tokens.

## Gradient diagnostics

For numeric shared/joint runs across three seeds and rounds 0–3, compute LoRA gradient cosines between fixed execution batches and proposal NLL for the frequency-optimal macro from training support. Negative cosine indicates local first-order descent conflict on that batch. This surrogate is not the true gradient of sampled proposal utility P and cannot alone establish long-term forgetting.

| Condition | Round | Mean gradient cosine | Negative batches |
|---|---:|---:|---:|
{chr(10).join(gtable)}

![Gradient diagnostics](figures/gradient-alignment.png)

## Relation to prior work

[Absolute Zero](https://arxiv.org/html/2505.03335v1) studies shared proposing/solving and proposer-training ablations; [Self-play Dynamics](https://arxiv.org/html/2510.27072v1) studies role entropy and frozen proposers; [Skill Self-Play](https://arxiv.org/html/2607.22529v1) studies coevolution of skills, proposing, and solving; [Implicit Inference](https://arxiv.org/html/2309.10105v2) shows prompt recovery from some fine-tuning degradation. Role interference, entropy decline, and the need to train proposers are not original claims here. Retain the [literature review](literature/NEAREST.md) and local paper HTML.

Potential contribution must come from controlled E/P/G separation, same-start proposal-source interventions, recovery interventions, and scope limits. Paper value depends on evidence, not RSI terminology.

## Limitations, failures, and reproduction

- Finite artificial DSL, 252 short macros, three training seeds, small-model LoRA, and three rounds do not represent open-ended discovery or unlimited recursive improvement.
- No general natural-corpus SFT control, real-code benchmark, full-parameter training, or RL. General forgetting/prompt-recovery explanations remain incompletely excluded.
- Grammar constraints match across base/trained models, but constrained utility measures finite-budget usability rather than disappearance of parameter knowledge.
- Initial downloads lacked httpx and switched to the standard library; curl resumed HTTP/2 interruptions. Run failures/refinements are in [amendments](analysis/amendments.md) and root logs.
- [Verification/hashes](analysis/verification.json), [training/proposal reproduction](README.md), [original protocol](PROTOCOL.md), [costs](analysis/cost.json), [full loop statistics](analysis/loop-results.json), and [intervention intervals](analysis/loop-inference.json).

All environments, weights, caches, raw outputs, and figures remain in the project. No paper has been published or submitted.
'''
(ROOT/'REPORT.md').write_text(text);print('Report generated',len(text),'characters')
