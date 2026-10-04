from common import *
import statistics
coverage=json.loads((ROOT/'analysis/coverage-results.json').read_text());length=json.loads((ROOT/'analysis/length-results.json').read_text());curve=json.loads((ROOT/'analysis/timecourse-results.json').read_text());inf=json.loads((ROOT/'analysis/loop-inference.json').read_text())
def pc(x):return f'{x*100:.2f}%'
def pp(x):return f'{x*100:+.2f}'
c=coverage['coverage']['instruction-t1.0-k16'];table=[]
for m,d in length['summary'].items():table.append(f"| {m} | {pc(d['base']['mean'])} | {pc(d['flat']['mean'])} | {pc(d['macro']['mean'])} |")
times=[]
for step,r in curve['summary'].items():times.append(f"| {step} | {pc(r['iid_accuracy'])} | {pc(r['ood_accuracy'])} | {pc(r['proposal_compression'])} |")
branches=[]
gradient_rows=[]
gradient_summary={}
for step in [0,16,64,128,256,512]:
 rs=[r for p in (ROOT/'runs').glob('gradient-original-*/results.json') for r in json.loads(p.read_text())['records'] if r['step']==step]
 assert len(rs)==9
 g=dict(mean_cosine=statistics.mean(r['cosine'] for r in rs),negative_batches=sum(r['cosine']<0 for r in rs),batches=len(rs),proposal_surrogate_nll=statistics.mean(r['proposal_surrogate_loss'] for r in rs))
 gradient_summary[step]=g
 gradient_rows.append(f"| {step} | {g['mean_cosine']:+.4f} | {g['negative_batches']}/9 | {g['proposal_surrogate_nll']:.4f} |")
(ROOT/'analysis/original-gradient-summary.json').write_text(json.dumps(gradient_summary,indent=2))
for domain,d in inf['posthoc_legacy_comparisons'].items():
 for source,stats in d.items():
  for split,x in stats.items():branches.append(f"| {domain} | {source} | {split} | {pp(x['mean'])} | {' / '.join(pp(v) for v in x['seed_differences'])} | {' to '.join(pp(v) for v in x['t_interval_95'])} |")
text=f'''# Supplementary controls and training timeline

These experiments were registered and run after some primary results were known. They are not original preregistered results. Original findings and failures are retained.

## Does missing primitive coverage explain degradation?

The original nine macros omit ends, whereas 31/48 hidden patterns in fresh test families contain ends and 83.11% of test programs use it. This is a substantive confound. A fixed manual coverage intervention replaces brown=inc, inc, inc with ends, inc, inc while preserving other call chains, inputs, and steps. Actual cumulative input and supervised tokens match original macro training exactly for all three seeds.

Primary proposal setting: base {pc(c['base'])}, original macro {pc(c['original_macro'])}, restored coverage {pc(c['compression'])}. The fraction of proposals containing ends recovers to {pc(c['contains_ends'])}; restored coverage minus original macro: {pp(c['coverage_minus_original_macro']['mean'])} percentage points, family-bootstrap interval {' to '.join(pp(x) for x in c['coverage_minus_original_macro']['family_bootstrap_95'])}. This mean improvement cannot be claimed as significant recovery, and performance remains well below base. Missing one primitive is therefore insufficient as an explanation, while broader training-distribution narrowness remains possible.

## Candidate stopping-length control

The primary experiment permits lengths 2–3; trained 3B models prefer shorter outputs. The added grammar quota fixes eight length-2 and eight length-3 proposals per family, preserving prompts, T=1, and selection.

| Model | Base | Flat | Macro |
|---|---:|---:|---:|
{chr(10).join(table)}

Complete seed differences and intervals are in [length-results.json](analysis/length-results.json). This is a new decoding condition, not a replacement estimate for the original sampling distribution.

## Complete original-recipe training timeline

Repeat original macro training for three seeds with unchanged optimizer and data order, inserting read-only evaluations at fixed steps without test-based early stopping.

| Optimization step | IID execution | Unseen-composition execution | Fresh-family net proposal compression |
|---|---:|---:|---:|
{chr(10).join(times)}

Final-weight hash agreement with original training by seed: {json.dumps(curve['final_weight_matches'],ensure_ascii=False)}. Agreement is required to interpret checkpoints as observations from the same deterministic training trajectory.

![Training timeline](figures/training-timecourse.png)

The timeline uses a different proposal-sampling random path from primary robustness jobs. Its final 10.37% net compression and primary-table 9.06% therefore use different proposal samples, despite identical execution tasks and final weights. Proposal utility falls from 40.26% to 20.78% by step 16 and approximately 9.48% by step 64, rather than declining only at the end.

## Original-recipe gradient diagnostics

These probes directly use original-recipe checkpoints and execution data, separately from closed-loop diagnostics in the main report. Each checkpoint uses three fixed minibatches per seed across three seeds. Initialization checkpoints are identical; nine batches do not represent nine independent models.

| Step | Mean gradient cosine | Negative-cosine batches | Proposal surrogate NLL |
|---|---:|---:|---:|
{chr(10).join(gradient_rows)}

Local gradient conflicts occur at several post-update points, motivating further study of objective interference. At step 16, however, proposal surrogate NLL improves over initialization while sampled utility has already fallen substantially. NLL is therefore not a sufficient utility proxy. Gradient cosine omits the full AdamW-preconditioned update direction and does not establish long-term causal degradation. The loop recipe also exhibits negative cosines without sustained proposal decline; detecting a negative cosine is not itself an RSI bottleneck.

## Degraded-proposer stress intervention

Because closed-loop proposers do not necessarily degrade, an additional intervention uses the demonstrably degraded first-round numeric macro adapter as an external proposer. Learners still start at the same shared round-1 checkpoint, with unchanged support, selector, executor, and 128-step training. Both execution domains receive primitive-sequence proposals from this same source. This tests the total effect of deliberately introducing a degraded proposer, **not spontaneous degradation within a natural loop**.

Positive values favor base/updated sources over legacy. Identical starts make these next-round learning-gain differences.

| Domain | Comparison | Evaluation | Difference (percentage points) | Three seed differences | 95% t interval |
|---|---|---|---:|---|---|
{chr(10).join(branches)}

Actual macro libraries, training lengths, semantic coverage, and support/held-out program compression by source are in [curriculum-rows.jsonl](analysis/curriculum-rows.jsonl). Proposal sources alter curriculum lengths and training-token counts. These comparisons estimate total effects at equal examples/steps, not pure proposal-quality effects at equal tokens. Abstraction compression P is a candidate proxy; only observed subsequent learning changes G connect it to improvement capability. The two cannot substitute for each other.
'''
(ROOT/'SUPPLEMENT.md').write_text(text)
report=ROOT/'REPORT.md';s=report.read_text();s+='\n\n## Supplementary controls and timeline\n\nSee [SUPPLEMENT.md](SUPPLEMENT.md) for primitive coverage, candidate-length quotas, original-training checkpoint curves, and post hoc degraded-proposer stress branches. These are separate from preregistered experiments.\n';report.write_text(s);print('Supplement generated')
