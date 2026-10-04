from common import *
import statistics,time
r=json.loads((ROOT/'analysis/results.json').read_text());jobs=json.loads((ROOT/'analysis/completed.json').read_text());assert len(jobs)==12 and all(j['returncode']==0 for j in jobs)
rows=[json.loads(l) for l in (ROOT/'analysis/rows.jsonl').read_text().splitlines()]
labels={'base':'Frozen base','flat':'After flat-trace training','macro':'After macro-label training','mismatch':'Macro model + mismatched context','random':'16 uniform random proposals','frequency':'Support-frequency heuristic','exhaustive':'Greedy over all 252 candidates','no-library':'No macro library'}
table='\n'.join(f"| {labels[k]} | {v['test_compression']*100:.2f}% | {v['search_solved_fraction']*100:.2f}% | {v['mean_selected_size']:.2f} | {v['mean_unique_proposed_semantics']:.2f} |" for k,v in r['methods'].items())
ctable='\n'.join(f"| macro − {k.removeprefix('macro-vs-')} | {v['mean_compression_difference']*100:+.2f} | {' / '.join(f'{x*100:+.2f}' for x in v['seed_compression_differences'])} | {' to '.join(f'{x*100:+.2f}' for x in v['family_cluster_bootstrap_95'])} | {v['mean_search_difference']*100:+.2f} |" for k,v in r['comparisons'].items())
gpu=sum(j['wall_seconds'] for j in jobs)/3600
passed=r['prespecified_screen_passed']
verdict='Passes the prespecified screen against random proposals but remains substantially below the frozen base. This does not support better useful-abstraction proposals after one execution-learning stage. Stop expanding this execution-training route and retain it as a counterexample and diagnostic.' if passed else 'Fails the prespecified screen. Current evidence does not support interpreting earlier execution gains as better useful-abstraction discovery. Further compute expansion of this short-program setup is not recommended.'
text=f'''# B01-02 follow-up: do abstraction proposals improve with execution learning?

Completed at (UTC): {time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}. The user authorized continuation; this round is complete and awaits review.

## Judgment

**{verdict}**

These are measurements with existing Qwen2.5-1.5B and flat/macro adapters, not newly trained proposal policies. Negative results do not exclude specially trained innovation strategies; positive results would not establish multi-round improvement. The protocol was fixed before generation, and analysis source separately registered before utility inspection.

## Actual design

- Eight independent families, each with three hidden short-operation patterns semantically distinct from the previous nine macros, 16 support programs, and 128 tests. Support/test functions are exactly disjoint; test functions need not be distinct from one another. Families are equally weighted.
- Models see support programs without hidden boundaries and generate 16 length-2–3 candidates. A finite-token trie constrains 252 valid candidates. Duplicates/identities consume budget without replacement.
- Three runs each for base/flat/macro, plus three macro mismatched-context controls. Training seeds are 11/22/33; base repeats vary sampling only.
- All methods select up to three semantically distinct macros using the same support-greedy rule and definition costs, without test-based selection. Random also has 16 proposals; frequency/full-enumeration references use different compute.
- Twelve model jobs and 1,536 actual proposals, with no new parameter training or reruns of the earlier 30 training jobs.

## Main results

Compression is net description-length reduction on unseen programs, not neural accuracy. Search discovery is external symbolic breadth-first discovery of complete target functions within 3,000 action expansions.

| Method | Test net compression | Search discovery | Mean library size | Distinct semantics per 16 proposals* |
|---|---:|---:|---:|---:|
{table}

*Full enumeration uses 252 candidates, no-library uses zero, and other methods use 16. Deterministic heuristics/no-library repeat in paired analyses across three seeds, not three independent experiments. Macros and primitives each count as one search action, but macros execute more primitives; see family-level raw counts.

| Comparison | Compression difference (points) | Three seed differences | Family-bootstrap 95% interval | Search difference (points) |
|---|---:|---|---|---:|
{ctable}

Prespecified screen: macro exceeds random mean compression by at least two points, improves across all three seeds, and loses no more than two points in search discovery. Decision: **{'Pass' if passed else 'Fail'}**. Intervals cluster eight families conditional on checkpoints; 1,536 proposals are not independent training repetitions.

## Why the overall judgment remains against this route

Macro beats random compression by +7.69 points, but the family-bootstrap interval is approximately −3.11 to +18.13, with substantial family uncertainty. Passing a screen does not mean significant superiority. More importantly, macro is 18.52 points below frozen base, declining for every seed, with interval approximately −26.76 to −10.01. Search discovery is also 6.71 points below base. Better execution did not transfer to better proposing.

Macro beats flat and mismatched context, indicating retained context adaptation rather than superiority to pretraining. Distinct semantics per 16 proposals fall from approximately 10.08 for base to 5.33 for macro and 3.00 for flat. Diversity contraction co-occurs with lower utility but is not identified as its cause, nor does it diagnose loss of all general capabilities. The support-frequency heuristic compresses 57.04%, substantially better but with different candidate-acquisition compute.

## Post hoc sensitivity checks

Two issues were added after primary results without overwriting them; see [amendments](analysis/amendments.md) and [complete 2×2 controls](analysis/sensitivity.json).

- Original semantic deduplication retained the first spelling, while compression requires literal matching. Selecting support gains first and excluding semantic equivalents afterward yields base 38.79%, macro 19.60%, flat 1.53%, random 11.74%, preserving direction. Full enumeration rises to 57.04%, matching the frequency heuristic. Its earlier disadvantage reflected representative selection, not inherently harmful extra candidates.
- With original selection but a 3,000-primitive-execution budget, search rates are base 58.95%, macro 55.96%, random 49.22%, flat 49.48%. Macro remains below base, including when both modifications apply.

Do not add larger models or more similar execution training. Continuing would require training directly for proposal utility, testing unseen families, and controls preserving base proposing. That next-stage design awaits review and was not started here.

## Interpretation limits

1. Earlier models learned execution traces without efficient-abstraction rewards or supervision. This tests transfer of that training; an untrained skill failure does not establish unlearnable innovation.
2. All methods share executor-generated correct support, not autonomously solved successes. The artificial DSL has only 252 macro candidates.
3. Contiguous-primitive compression need not accelerate search because macros increase branching. Report search separately rather than substituting the better metric for a failed one.
4. Budgets match proposal counts and downstream selection, not model/random/frequency compute. Equal action expansions are not equal primitive-execution costs.
5. Tasks differ from the old library but share six primitives. This is not natural-language, real-code, or cross-primitive transfer.
6. Do not tune prompts, temperature, candidate counts, or families on this test. Retain all proposals, duplicates, and negative-utility candidates.

## Audit and reproduction

- [Preregistration](PROTOCOL.md), [mechanism limits](MECHANISM.md), [initial hashes](analysis/registration.json), [evaluation registration](analysis/evaluation-registration.json).
- [Machine-readable results](analysis/results.json), [method/seed/family records](analysis/rows.jsonl), [verification/hashes](analysis/verification.json).
- `runs/*/proposals.jsonl` retains complete prompts, raw generations, candidate indices, and token counts. `data/tasks.json` retains support/tests and hidden patterns; `data/candidates.json` contains the candidate universe.
- Reuse parent `runs/*/adapter` and root `.training-venv`; all new files stay in this subtree. Base/adapter hashes are in parent `analysis/artifact-verification.json`.
- Total device reservation approximately {gpu:.3f} GPU-hours; CPU analysis wall time {r['seconds']:.1f} seconds. Reservation includes loading/waiting, not kernel-active time. Independent jobs use separate GPUs without NCCL training.

From the project root, first `source training-env.sh`. Build data with `python workspace/research/B01-02/followup/src/common.py`. `src/launch.py` dispatches generation and refuses to overwrite existing runs. Run `src/analyze.py`, `src/verify.py`, and `src/report.py` for statistics, verification, and reporting. Use new run directories for reproduction to retain original evidence.
'''
(ROOT/'REPORT.md').write_text(text)
(ROOT/'analysis/cost.json').write_text(json.dumps({'reserved_gpu_hours':gpu,'cpu_analysis_wall_seconds':r['seconds'],'model_jobs':12,'raw_proposals':1536},indent=2))
print('Wrote report:',verdict)
