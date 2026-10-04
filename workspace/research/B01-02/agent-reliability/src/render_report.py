from pathlib import Path
import collections,json,statistics
R=Path(__file__).resolve().parents[1]
x=json.loads((R/'analysis/results.json').read_text());a=json.loads((R/'analysis/native-audit.json').read_text());m=json.loads((R/'analysis/mechanism-audit.json').read_text());assert len(x['runs'])==a['count']
rows=x['runs'];G=x['groups'];N=len(rows);failed=sum(not s['grade']['complete'] for s in rows)
def score(tag):return f"{G[tag]['complete']}/{G[tag]['n']}"
def block(prefix):return ' | '.join(score(prefix+c) for c in ['plan','reminder','identity','todo'])
def group_runs(tag):return [s for s in rows if s['tag']==tag]
def one(tag,task):
 ss=[s for s in rows if s['tag']==tag and s['task']==task];assert len(ss)==1;return ss[0]
policies=[('controlled-v2-main-full','Full history'),('controlled-v2-main-trim','Clear old history only'),('controlled-v2-main-compact','Clear + progress summary'),('controlled-v3-main-sanitize','Filter pseudo-role text only')]
tasks=[f'queue-controlled-n24-s{20267001+i}' for i in range(3)]
lines=['# Agent reliability: repairs, replication, and mechanism controls','',f'This study retains **{N} model trajectories**, including {failed} that failed full acceptance. These include development failures, backtests, independent validation, and repeats. Model processes occupied a total of **{x["gpu_reserved_hours"]:.2f} GPU-hours** (including loading and preparation while processes hold GPUs; excluding the earlier agent-study total of 2.80 GPU-hours). No paid external inference APIs were called, and model weights were unchanged.','',
'## Conclusions supported so far','',
'1. The execution interface was a substantial obstacle. On the original 24 tasks, the same frozen 32B model improved from 9/24 actual completions with the earlier custom protocol to 23/24 with the native tool interface; adding an unrelated example gave 21/24. This is an engineering comparison of combined interface, termination-semantics, and budget repairs, not a single-component effect.',
'2. A unique advantage from identity notes did not replicate consistently. On 36 independent tasks, empty notes scored 36/36, generic reminders 34/36, identity notes 36/36, and to-do lists 35/36. This replication has a ceiling effect; it neither proves identity notes useless nor turns a small-sample advantage into a firm conclusion.',
'3. A repairable long-interaction failure was found. Across three new 24-ticket tasks with fixed clock, error paths, and input schema, full history completed only 1/3 tasks. Clearing old history alone, clearing it while retaining a progress summary, and filtering only model-generated pseudo-role text each completed 3/3. Every condition can stop voluntarily, without hidden-answer feedback or a hard gate preventing termination.',
'4. A failure that declared completion after delivering only 5/24 items reproduced verbatim in a new process. Model outputs and tool returns matched before intervention. Preserving all genuine tool history while filtering only pseudo-role text also repaired it. Additional identity restatement or progress summaries were therefore not necessary for completion in these cases.','',
'The positive findings are reproducible execution repairs and mechanism cases. Three controlled tasks do not provide a broad success-rate estimate or establish RSI, weight-level self-improvement, or research novelty.','',
'## Model, tools, and acceptance checks','',
'Frozen Qwen2.5-32B-Instruct, revision `5ede1c97bbab6ce5cda5812749b4c0bdf79b18dd`; BF16, SDPA, and greedy generation, using the native tools chat_template. Ordinary tasks use list_files/read_file/write_file/run_python; sequential tickets add next_ticket/submit_ticket. Python runs in a chroot sandbox within this directory, without network access or subprocess creation. Execution uses local experiment scripts, not the EvoScientist chat runner, with no SFT or Agentic RL.',
'File tasks check specified configurations and all unauthorized changes. Data tasks check actual CSV computations and preservation of inputs. Code tasks use hidden fresh inputs to check function behavior and unchanged inputs. Sequential tickets reveal inputs one at a time; submission receipts acknowledge file delivery only, opening the next item even if the result is wrong. All actual results are independently graded after termination. See `analysis/queue-receipt-validation.json` for a check that deliberately submits an incorrect output and confirms acceptance.',
'Long checklists can be batch-processed in one action, so 12 requirements alone do not establish long-horizon interaction. Sequential tickets require new tool inputs and are used to test long interactions. Controlled main experiments share limits of 128 rounds, 24000 generated tokens, 30000 context tokens, 4096 generated tokens per turn, and 2400 seconds. Early stopping, protocol failure, context/output budget exhaustion, and incorrect deliveries are recorded separately.','',
'## All main comparisons','',
'Experiments below use different fixed samples, so changes across rows are not single-factor effects. The four columns count tasks passing all requirements within each row.','',
'| Experiment | Empty notes/baseline | Generic reminder | Identity notes | To-do list |','|---|---:|---:|---:|---:|',
'| Native interface, 12 new long checklists | '+block('long-')+' |',
'| Explicit note field, 12 independent long checklists | '+block('notes-main-')+' |',
'| Explicit note field, fixed 36-task replication | '+block('notes-replication-')+' |',
'| Native sequential tickets, 3 tasks each with 12/24 items | '+block('queue-main-')+' |',
'| Explicit notes + shared execution instructions, 6 new sequential-ticket tasks | '+block('queue-notes-main-')+' |',
'| Handoff summary, 3 old + 3 new 24-item tasks | '+block('compact-main-')+' |','',
'Both native-interface development configurations scored 6/6; both independent short-task sets scored 12/12. Explicit-note development results, baseline5/6 and identity6/6, are also retained. Early natural-language status requests were often not followed: only 7/24 action rounds in the native long-checklist identity condition contained nonempty prose. Later notes were recorded through a shared note parameter on all tools, but adherence must still be checked from content rather than condition names.','',
'## 24-ticket experiment with fixed execution conditions','',
'The table reports **correct deliveries/24**, not self-reported completion. The two full-history failures delivered only 5 and 23 items; they were not arithmetic errors among 24 delivered items.','',
'| Input seed | Full history | Clear old history only | Clear + progress summary | Filter pseudo-role text only |','|---|---:|---:|---:|---:|']
for t in tasks:lines.append('| '+t.rsplit('s',1)[-1]+' | '+' | '.join(f"{one(tag,t)['grade']['completed_requirements']}/24" for tag,_ in policies)+' |')
lines+=['','Paired tests of full history versus each repair have only 3 tasks, with two-sided sign-test p=0.5. No statistically established general advantage is claimed. The successful full-history case is retained alongside both failures. Filtering was proposed after observing one failure and then applied to all 3 tasks, making it an exploratory mechanism ablation.','',
'| Policy | Mean generated tokens | Mean cumulative input tokens | Mean generation rounds | Full passes |','|---|---:|---:|---:|---:|']
for tag,label in policies:
 g=G[tag];lines.append(f"| {label} | {g['mean_generated_tokens']:.0f} | {g['mean_input_tokens']:.0f} | {g['mean_turns']:.1f} | {score(tag)} |")
lines+=['','These are per-attempt costs. Full history includes failures, so fewer generated tokens cannot directly be read as higher efficiency.','',
'## A verifiable failure sequence','',
'Seed20267001: the first 6 rounds match exactly before intervention. In full history, model-generated Human/pseudo-tool_response text appears at round 10 (logs are zero-indexed), then accumulates. Round 19 reaches the 4096-token cap. In the next round, the model infers that all 24 items are processed because the first items follow the same procedure, although genuine receipts cover only 5. Independent repetition matches all visible model outputs, tool returns, and final file states.',
'Filtering adds no tool calls, writes no missing outputs, supplies no answers for remaining tasks, and does not intercept termination. When an assistant message containing genuine tool calls is inserted into history, it removes pseudo-role markers and subsequent prose while retaining genuine calls, genuine returns, and raw logs. It achieves 24/24 on all three samples. This regex filter is a diagnostic ablation, not a general production-dialogue policy: legitimate quotations can contain similar markers.',
'Deleting old interactions for completed items alone also achieves 3/3; additional progress summaries were not necessary in these data. More precise length-matched deletion, alternative decoding, and cross-model checks remain undone, so all improvements cannot be uniquely attributed to one semantic mechanism.','',
'## Failures encountered and repairs','',
'- Custom JSON wrapping rejected multiple calls, and same-batch finish preceded observation of tool results. Native tool messages replaced it, allowing the model to terminate naturally only after receiving actual returns.',
'- Native interfaces still showed inconsistent generated code, incorrect mapping arguments, and missing validation. All failures were retained and independent long-checklist replication was run; faulty implementation was not uniformly classified as unwillingness to continue.',
'- Long histories accumulated invented role/tool-return text and exhausted context. Handoff-summary, clearing-only, and filtering-only controls were added.',
'- The model printed the current time, causing paired trajectories to diverge before summary intervention; host error paths also varied by worker. Common clocks/RNG were fixed and error paths standardized before shared-interface comparisons on new inputs. Earlier cross-version pairs serve only as engineering backtests.',
'- Initial summary calibration under fixed execution conditions scored 3/4. One task delivered 4 items with only 1 correct because the JSON root structure was lost or guessed incorrectly. The actual array schema was added to persistent interface instructions shared by every condition; second-version calibration scored 4/4. The failed version was retained, and scheduled main-task inputs/answers were unchanged.','',
'## Evidence and limitations','',
f'- `analysis/native-audit.json`：{a["count"]} archived trajectory results rechecked, actions replayed, and file states verified. Early cached audits check files and tool-error states; new controlled experiments additionally compare full tool-return text.',
'- `analysis/mechanism-audit.json`: pre-intervention agreement in nine repair pairs and deterministic repetition of the original failure.',
'- `analysis/failure-diagnostics.json`: missing/incorrect outputs, delivered/undelivered items, pseudo-role text, and final responses for every failure.',
'- `analysis/results.json`: all successes, failures, tokens, rounds, model-process costs, and paired statistics.',
'- `runs/`: raw generations, tool calls, messages, final files, and submission receipts for every run. `src/` and REGISTRATION files preserve implementation and preregistered design.',
'- `analysis/environment.json`: environment and model/template fingerprints; all environments and artifacts are in the current project directory.','',
'The earlier SFT flat/macro length-generalization study differs from this frozen-model agent study. Current results test inference-time interface/prompt transfer only and are not combined into one RSI mechanism. Only one model family and greedy decoding are tested. The main controlled sequential experiment has only 3 tasks: synthetic workflows with explicit inputs and visible receipts, rather than open-ended software projects or research tasks. Baseline interface, escaping/format, context, and behavioral effects must be distinguished. Low scores under the old interface alone do not establish a need to change models or train.','',
'See [LITERATURE.md](LITERATURE.md) for related context-management work and this limited novelty check. A more specific follow-up question is when mixing genuine tool records with invented execution narratives in history causes false completion, and how to prevent that accumulation while preserving necessary interface information. Name restatement remains an ablation, not an established main conclusion.','',
'![Results and controlled progress](figures/reliability.png)','']
(R/'REPORT.md').write_text('\n'.join(lines))
summary=f'''# Review entry point

Execution repairs and controlled verification are complete, with {N} retained trajectories and {x['gpu_reserved_hours']:.2f} GPU-hours of model-process occupancy. No fine-tuning or paid external inference was used.

- Same 32B model, original 24 tasks: old protocol9/24, native interface23/24.
- Independent 36-task replication: empty notes36/36, identity36/36; no consistent unique benefit from name/identity notes.
- Three new 24-ticket tasks: full history5/24,24/24,23/24; clearing history alone, clearing + summary, and filtering invented pseudo-role text alone each score24/24,24/24,24/24.
- The failure completing only 5 items reproduces verbatim in a new process. Paired prefixes match before repair, with genuine tool records and all failures retained. There is no answer feedback or hard termination gate.

These are small-scale mechanism cases and usable repairs, not an established novelty claim, proof of RSI, or proof of a unique identity-restatement benefit. Further work should focus on false completion after invented execution narratives/pseudo-tool observations enter history, with cross-model and real-task verification.

See [REPORT.md](REPORT.md) for full methods, costs, counterexamples, novelty checks, and limitations, and [COMPLETION_AUDIT.md](COMPLETION_AUDIT.md) for the audit.
'''
(R/'CONCLUSIONS.md').write_text(summary)
print('Wrote report and review entry for',N,'runs')
