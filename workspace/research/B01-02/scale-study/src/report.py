from pathlib import Path
import json,statistics,time
R=Path(__file__).resolve().parents[1];d=json.loads((R/'analysis/results.json').read_text());e=json.loads((R/'analysis/extended-results.json').read_text());ci=json.loads((R/'analysis/paired-inference.json').read_text())
assert not d['missing'];assert e['records_checked']==13440
fmt=lambda v:f'{100*v:.2f}%'
table=[]
for model in ['qwen1.5b','qwen3b','qwen7b','qwen32b']:
 for c in ['flat','macro']:
  r=next(r for r in d['summary'] if (r['model'],r['condition'],r['split'])==(model,c,'ood'))
  v=r['means'];table.append(f"| {model} | {c} | {fmt(v['accuracy'])} | {fmt(v['strict_trace'])} | {fmt(v['correct_prefix_early_answer'])} | {fmt(v['exact_two_tools_early_answer'])} | {fmt(v['two_output_segments'])} |")
error_table=[]
for row in d['summary']:
 if row['split']=='ood':
  v=row['means'];error_table.append(f"| {row['model']} | {row['condition']} | {fmt(v['wrong_operation'])} | {fmt(v['numeric_step_error'])} | {fmt(v['format_extra_lines'])} | {fmt(v['missing_or_multiple_answer'])} |")
extable=[]
for r in e['summary']:
 extable.append(f"| {r['model']} | {r['condition']} | {r['split']} | {fmt(r['accuracy'])} | {fmt(r['strict_trace'])} | {fmt(r['exact_two_tools_early_answer'])} |")
intervals=[]
for model,c in ci['comparisons'].items():
 x=c['ood']['accuracy'];intervals.append(f"| {model} | {100*x['mean']:+.2f} | {' / '.join(f'{100*v:+.2f}' for v in x['seed_differences'])} | {' to '.join(f'{100*v:+.2f}' for v in x['seed_t95'])} | {' to '.join(f'{100*v:+.2f}' for v in x['program_bootstrap95'])} |")
cal=[];cost=[]
for model in ['qwen7b','qwen32b']:
 z=json.loads((R/f'analysis/{model}-calibration.json').read_text());m=z['microbatch'];p=R/f'{model}/runs/flat-original-s11-probe-m{m}/summary.json';v=json.loads(p.read_text());cal.append(f"| {model} | {m} | {32//m} | {v['training']['peak_memory_bytes']/1024**3:.2f} | {v['training']['seconds']/2:.2f} |")
 for stage in ['completed','checkpoint-tests-completed']:
  for v in json.loads((R/f'analysis/{model}-{stage}.json').read_text()):cost.append(v['wall_seconds'])
 for v in z['probes']:cost.append(v['wall_seconds'])
# Use actual evaluation time, not waiting time, for extended passes.
for model in ['qwen1.5b','qwen3b','qwen7b','qwen32b']:
 for v in json.loads((R/f'extended/{model}/completed.json').read_text()):cost.append(v['wall_seconds'])
primary_cost=sum(cost)
supplement_cost=0
for lane in ['lr','instruct']:
 records=json.loads((R/f'analysis/supplement-{lane}-completed.json').read_text())
 assert all(x['returncode']==0 for x in records)
 supplement_cost+=sum(x['wall_seconds'] for x in records)
cost.append(supplement_cost)
(R/'analysis/cost.json').write_text(json.dumps({'gpu_reserved_hours_approx':sum(cost)/3600,'primary_and_confirmation_process_hours':primary_cost/3600,'supplement_process_hours':supplement_cost/3600,'note':'single-GPU subprocess wall times for new training, calibration, checkpoint evaluation; extended model loading omitted; pre-launch queue waiting and downloads excluded, but early checkpoint subprocesses may include waiting for saved weights; not GPU kernel busy time; includes completed supplement lane records; excludes unmeasured failed-start overhead and separate sharded smoke probe'},indent=2))
text=f'''# Model scale and stopping after two segments: stage-one results

Generated at (UTC): {time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}. Automatic aggregation is complete; scientific interpretation requires the review in CONCLUSIONS.md. Codex executed scripts directly, rather than through EvoScientist chat.

## Design and completed scope

Qwen2.5 Base 1.5/3/7/32B, with three training seeds each for flat and macro. Reuse existing 1.5/3B adapters; add six 512-step LoRA runs each for 7/32B. Use 4,096 training examples, effective batch size 32, and 16,384 example presentations. Inputs, primitive operations, and correct states are identical; only output segment headers differ between step and the corresponding tool name.

Two-call examples account for 90.38% of original training; none contain more than two calls. The original test contains 560 examples: 128 IID, 384 long compositions, and 48 stress examples. This report analyzes every output, without conditioning on macro success and flat failure. Training seeds are repeated training runs; repeated evaluation of one example does not create independent examples.

Registered checkpoints are 0/16/64/128/256/512, with all weights saved. Development evaluation runs during training; fixed checkpoints are tested after training, without test-based checkpoint selection. Model revisions and SHA hashes are in models/*/download-manifest.json.

The independent confirmation set contains 480 examples: 24 programs at each call length 3/4/5/6/8 and four inputs per program, totaling 120 programs. Exact functions are disjoint from old train/dev/test functions. New tests allow 512 generated tokens; old examples allow 256. Frozen baselines on new examples receive full tool definitions, since the base cannot know artificial color mappings without them. Interpret conditions with and without definitions separately.

## Original test: unseen 3–5 calls, means over three seeds

| Model | Label | Answer accuracy | Complete trajectory accuracy | Early answer after correct prefix | Stops after first two correct tools | Exactly two segments |
|---|---|---:|---:|---:|---:|---:|
{chr(10).join(table)}

“Stops after first two correct tools” requires a correct operation/numeric prefix and a voluntary answer matching that intermediate state. This is a directly verifiable subset of early stopping; other operation errors or omissions are not forced into it. Two segments describe output behavior, not process correctness. Original code saved non-EOS token counts without final token IDs. Counts below the limit minus one imply EOS before the cap under the generation configuration; exactly limit-minus-one is ambiguous, and reaching the cap indicates exhaustion. These are inferences, not directly logged stop reasons. EOS does not imply task completion, and intermediate answers must be assessed against the full trajectory. Correct answers with incorrect trajectories fail the complete-trajectory metric.

## Local operation and formatting errors

The following metrics overlap and cannot be summed into mutually exclusive cause shares. Wrong operation means an emitted operation differs from the required order or is extra; simply omitting a suffix does not count here. Numeric errors are checked against the preceding reported state, avoiding repeated attribution of propagated upstream errors as fresh arithmetic mistakes. These are behavioral observations, not causal mechanism evidence.

| Model | Label | Wrong operation | Wrong arithmetic | Extra formatting lines | Missing or multiple answers |
|---|---|---:|---:|---:|---:|
{chr(10).join(error_table)}

## Paired differences and intervals

The table reports macro−flat answer accuracy in percentage points. Seed intervals are t intervals over three training seeds. Program intervals bootstrap complete call-chain clusters conditional on those seeds. The intervals describe different uncertainty.

| Model | Mean difference | Three seed differences | Seed 95% t interval | Program-clustered 95% interval |
|---|---:|---|---|---|
{chr(10).join(intervals)}

## Fresh confirmation and longer call sequences

Frozen means the untuned base with tool definitions. Other conditions are trained models without definitions. These prompt differences prevent direct interpretation as training gains or losses.

| Model | Condition | Length group | Answer accuracy | Complete trajectory accuracy | Stops after first two correct tools |
|---|---|---|---:|---:|---:|
{chr(10).join(extable)}

## Measured resources and implementation checks

| Model | Microbatch | Accumulation steps | Two-step calibration peak GiB | Calibration seconds/optimization step |
|---|---:|---:|---:|---:|
{chr(10).join(cal)}

Approximately {sum(cost)/3600:.2f} GPU-hours; see analysis/cost.json for the accounting definition. This includes supplementary training/evaluation processes but excludes downloads, prelaunch queues, incompletely timed failed starts, and separate cross-GPU smoke checks. Early-checkpoint evaluation processes may include waiting for weights and do not measure pure GPU kernel activity. Data and caches remain in the project directory.

Splitting microbatch 16 into four failed the prespecified 3% relative BF16 gradient tolerance; failed records remain. A 1.5B check retaining microbatch 16 and enabling only gradient checkpointing matched loss/gradients. Actual microbatches are listed above; fallbacks require acknowledging floating-point implementation differences. The primary study uses no quantization.

## Interpretation limits and unfinished research branches

This is within-family scale association, not fully randomized causal identification of parameter count. Pretraining, architecture, and LoRA proportions are not completely controlled. Larger models do not automatically have more stable priors.

Symmetric 1e-4 learning-rate supplements for 3B/32B and three-seed flat/macro 32B-Instruct training, fixed final evaluation, and the frozen Instruct baseline are complete; see [SUPPLEMENT.md](SUPPLEMENT.md). This is still not real-agent interaction validation. Frozen models do not establish reliable initial long-execution capability under this protocol, so prior preservation/destruction remains unidentified. Same-information pre/post-training comparisons are in analysis/matched-context.json.

[CONCLUSIONS.md](CONCLUSIONS.md) reports major findings, LoRA proportions, and protocol deviations. analysis/outcome-diagnostics.json adds complete classifications of equivalent trajectories and chance-correct answers. Fixed curves do not select checkpoints using test scores. Development mastery thresholds were not numerically preregistered; later thresholds are exploratory only.

## Figures

![Scale and two stopping metrics](figures/scale-comparison.png)

![Independent-program length extrapolation](figures/independent-lengths.png)

![Complete fixed-checkpoint curves](figures/learning-curves.png)

Matching SVG/PDF files are provided. All three figure groups were visually checked. Lines connect fixed-checkpoint means and do not establish values at unmeasured intermediate steps.

## Reproduction materials

- [Final example-level audit](analysis/final-case-audit.jsonl), [original-test statistics](analysis/results.json), and [independent-confirmation statistics](analysis/extended-results.json).
- [Paired intervals](analysis/paired-inference.json), [data registration](analysis/extended-data-registration.json), and [registration and amendments](WORK_STATUS.md).
- Raw outputs in each model runs/ and extended/ directory; final and intermediate LoRA adapters retained in full.
'''
(R/'REPORT.md').write_text(text);print('Report draft generated; manual conclusion required',flush=True)
