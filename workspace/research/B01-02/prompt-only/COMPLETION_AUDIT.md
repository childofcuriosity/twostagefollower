# Completion audit

2026-09-28. Every item in COMPLETION_REQUIREMENTS.md has been checked. The bounded goal for this round is complete; this is not a prior commitment to method effectiveness.

| Requirement | Authoritative evidence and verification | Result |
|---|---|---|
| Original model, no adapters, earlier training unchanged | models/qwen7b and qwen14b/download-manifest.json; worker.py loads original directories directly with AutoModelForCausalLM, without training or PEFT; original DSL/scorer SHA unchanged; writes limited to prompt-only and top-level handoff documents | Pass |
| Start with 7B and use only the authorized fallback | All 448 7B exploration outputs across seven lengths retained; L2 STEP 3/32 and L5 0/32; analysis/precheck-diagnosis.json and fallback-decision.json; full procedure repeated with 14B | Pass |
| Four prompts and shared demonstration | Literal normalized comparison in analysis/method-audit.json; identical templates across models; ALIAS mapping matches the earlier formal manifest; actual chat system prefix in analysis/rendered-precheck-STEP.txt | Pass |
| Exploration and length selection | 32 examples per length in STEP/NAME, 448 outputs per model; fallback14/analysis/length-selection.json reads STEP only; only L2 qualifies; no supplementary-test trigger | Pass; one length under the rule |
| Fresh examples and exactly-once shard generation | fallback14/analysis/completion-audit.json verifies disjoint underlying pairs among 12 prechecks, 224 exploration examples, 512 formal examples, and the demonstration; final-research-audit.json verifies shared examples across conditions and eight disjoint 256-example shards with no additions/deletions during merging | Pass; 2,048 formal outputs |
| Formal freeze | fallback14/data/formal-L2-manifest.json written at 00:36:17 UTC before all eight running.json.start values; source and frozen-source hashes match file by file; all workers hold the same manifest hash | Pass |
| Decoding and capacity | Per-shard generation-config.json: do_sample=false, num_beams=1, repetition_penalty=1; shared 256-token limit; maximum correct target 78 and input 493 within context 32768; token IDs, decoded text, and EOS verified per example | Pass |
| Strict scoring and paired statistics | Original scorer agrees with independent trajectory comparison; 3040 outputs rescored; formal raw/graded records match; scores-formal-L2.json contains group differences, 10,000-sample paired bootstrap intervals, and discordant counts; repeated greedy inference is not treated as seeds | Pass |
| Errors, headers, and termination | analysis/formal-errors-reviewed.json and example-level files; header compliance separate; all-stop-reasons.json records 2048 formal EOS endings, three capped 7B and ten capped 14B exploration outputs, and all-EOS prechecks | Pass, with explicit analysis corrections |
| Error-classification corrections preserved | Initial labels conflated extra primitives with calls and empty Trace: headers with call segments; postanalysis/error_review.py corrects 99 auxiliary labels without changing originals, scores, or outputs; seven targeted cases pass in error-review-validation.json | Pass; no result-driven inference changes |
| Costs | final-research-audit.json sums GPU-synchronized batch generate time and outer dispatch durations; formal allocation 0.198 GPU-hours, total 1.046; report distinguishes parallel wall time, allocation, and kernel activity | Pass |
| Resources and exceptions | All 60 jobs return code 0; no failed records; eight local GPUs only, two simultaneous shards per formal condition; each stage under one hour; final nvidia-smi shows 0 MiB and 0% on all GPUs, with no worker/dispatch/pipeline/download processes | Pass |
| Final delivery and limits | Top-level REPORT.md answers the primary comparison, informative lengths/errors, and costs; 7B_EXPLORATION.md retained; prompts, configurations, raw data/outputs, original and reviewed scores retained; no independent cross-model confirmation, real tasks, or external publication launched | Pass |

## Audit entry points

- Main procedure: `fallback14/src/report.py` (generation-stage audit; rerunning rebuilds the initial automatic report, while the top-level formal report is separate).
- Research review: `postanalysis/final_audit.py`, producing `analysis/final-research-audit.json`.
- Auxiliary error review: `postanalysis/error_review.py`, producing `analysis/formal-errors-reviewed.json` and `graded-formal-errors-reviewed.jsonl`.
- Targeted primitive-operation and correct/incorrect trajectory checks: `analysis/implementation-validation.json`, `fallback14/analysis/implementation-validation.json`, and `analysis/error-review-validation.json`.

Supported conclusion: 14B L2 NAME−STEP is −0.78 points, with a 95% interval crossing zero. ALIAS has an auxiliary positive result, limited by simultaneous input/output renaming. This round establishes no effective length for prompt-only repetition of original names, and does not rule out benefits across all prompts and tasks.
