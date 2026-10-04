from common import *
import collections,datetime
from transformers import AutoTokenizer
selection=json.loads((R/'analysis/length-selection.json').read_text());lengths=selection['lengths']
tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True)
eos=json.loads((MODEL/'generation_config.json').read_text())['eos_token_id']
if isinstance(eos,int):eos=[eos]
seen={key(EXAMPLE):'example'};splits=collections.Counter()
for f in sorted((R/'data').glob('*.jsonl')):
 for x in readrows(f):
  k=key(x);assert k not in seen,(f,k,seen.get(k));seen[k]=f.name;splits[x['split']]+=1
checks=[];scores=[]
for L in lengths:
 manifest=json.loads((R/f'data/formal-L{L}-manifest.json').read_text());assert manifest['data_sha256']==sha(R/f'data/formal-L{L}.jsonl')
 rows=readrows(R/f'data/formal-L{L}.jsonl');assert len(rows)==512
 graded=readrows(R/f'analysis/graded-formal-L{L}.jsonl');assert len(graded)==2048
 for c in CONDITIONS:
  run=R/f'runs/formal-L{L}-{c}';rr=readrows(run/'predictions.jsonl');assert len(rr)==512
  assert [x['id'] for x in rr]==[x['id'] for x in rows]
  assert (run/'complete.json').exists()
  assert sha(R/f'prompts/{c}.txt')==manifest['prompts'][c]
  for x,y in zip(rr,rows):
   assert key(x)==key(y)
   ids=x['output_token_ids'];assert len(ids)==x['generated_tokens']
   assert tok.decode(ids,skip_special_tokens=True)==x['raw']
   assert x['max_new_tokens']==manifest['max_new_tokens']
   assert x['input_tokens']+manifest['max_new_tokens']<=manifest['context']
   if x['finish_reason']=='eos':assert ids[-1] in eos and all(i not in eos for i in ids[:-1])
   else:assert len(ids)==x['max_new_tokens'] and not any(i in eos for i in ids)
  checks.append(dict(length=L,condition=c,n=len(rr),predictions_sha256=sha(run/'predictions.jsonl')))
 scores.append(json.loads((R/f'analysis/scores-formal-L{L}.json').read_text()))
# Confirm all registered initial exploration lengths and selection rule using only STEP.
rates=selection['step_rates'];assert all(str(L) in rates for L in [2,5,10,15,20,30,40])
eligible=sorted(int(L) for L,r in rates.items() if .2<=r<=.9)
expected=sorted(set([eligible[0],eligible[-1]])) if eligible else [min(map(int,rates),key=lambda L:(abs(rates[str(L)]-.5),L))]
assert lengths==expected
sources={}
for L in lengths:
 manifest=json.loads((R/f'data/formal-L{L}-manifest.json').read_text())
 for name,h in manifest['source'].items():
  assert sha(R/'src'/name)==h,(name,'changed after formal freeze')
 sources[L]=manifest['source']
audit=dict(passed=True,formal_rows=2048*len(lengths),selected_lengths=lengths,disjoint_data_counts=dict(splits),raw_checks=checks,source_hashes=sources,verified_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
write(R/'analysis/completion-audit.json',audit)
lines=['# Repeating tool identities with prompting alone: formal results','',f'Model: {json.loads((MODEL/"download-manifest.json").read_text())["repo"]} Original weights, without adapters or training. The primary comparison is NAME−STEP. Success requires the complete operation sequence, every intermediate state, and the final Answer to be correct.','', '## Length selection and exploration','', 'Formal lengths selected using STEP alone:'+', '.join(map(str,lengths))+'。'+('No tested length lies in the 20%–90% range. Following registration, select the tested length closest to 50%; floor/ceiling limitations apply.' if selection['fallback'] else 'Select the shortest and longest lengths within the 20%–90% range.'),'', '| Call length | STEP | NAME |','|---:|---:|---:|']
for L in sorted(map(int,rates)):
 s=json.loads((R/f'analysis/scores-explore-L{L}.json').read_text())['results'];lines.append(f'| {L} | {s["STEP"]["correct"]}/32 ({s["STEP"]["rate"]:.2%}) | {s["NAME"]["correct"]}/32 ({s["NAME"]["rate"]:.2%}) |')
lines+=['','## Four formal conditions','', '| L | Header | Strict success | Paired difference from STEP, 95% interval (percentage points) | All headers compliant | Output tokens/example | Input tokens/example | Generate time (seconds) |','|---:|---|---:|---|---:|---:|---:|---:|']
for score in scores:
 L=score['length']
 for c in CONDITIONS:
  s=score['results'][c];p=score['paired_vs_STEP'].get(c)
  diff='—' if p is None else f'{100*p["difference"]:+.2f} [{100*p["ci95"][0]:+.2f}, {100*p["ci95"][1]:+.2f}]'
  lines.append(f'| {L} | {c} | {s["correct"]}/512 ({s["rate"]:.2%}) | {diff} | {s["header_compliance"]:.2%} | {s["mean_output_tokens"]:.2f} | {s["mean_input_tokens"]:.2f} | {s["generate_seconds"]:.2f} |')
lines+=['','Each example receives one greedy generation per condition, with the same underlying examples across all four conditions. The 95% intervals use 10,000 paired example-level bootstrap samples (seed 740001) and describe sampling uncertainty conditional on the fixed model, prompts, and example distribution. Repeated inference is not treated as training seeds. Auxiliary comparisons are not claimed as multiplicity-adjusted confirmatory findings.','', '## Primary comparison and costs','']
for score in scores:
 L=score['length'];s=score['results']['STEP'];n=score['results']['NAME'];p=score['paired_vs_STEP']['NAME']
 dt=n['mean_output_tokens']-s['mean_output_tokens'];ds=n['generate_seconds']-s['generate_seconds']
 lines.append(f'- L{L}：NAME−STEP {100*p["difference"]:+.2f} percentage points; NAME-only successes: {p["better"]}; STEP-only successes: {p["worse"]}. Output: {dt:+.2f} tokens/example ({dt/s["mean_output_tokens"]:+.2%}); total batch generate time: {ds:+.2f} seconds ({ds/s["generate_seconds"]:+.2%}）。')
lines+=['','## First errors and termination reasons','', '| L | Condition | First-error counts | Termination reasons |','|---:|---|---|---|']
for score in scores:
 for c in CONDITIONS:
  s=score['results'][c];lines.append(f'| {score["length"]} | {c} | {json.dumps(s["first_errors"],ensure_ascii=False)} | {json.dumps(s["finish_reasons"])} |')
lines+=['','First-error labels: numeric = arithmetic or final-number error; tool_or_order = incorrect primitive expansion or order; omitted_call/extra_call = premature Answer, missing/extra primitive operations, or identifiable deletion/insertion of complete calls; format = formatting error; none = no strict trajectory error. Omission/addition labels classify observable outputs, not internal causes. Header counts are reported separately and can overlap. Header noncompliance does not automatically fail the primary metric.','', '## Scope and evidence','', 'This experiment tests a synthetic execution task with nine supplied tools and four-digit states. With no training-length range, in-domain/out-of-domain terminology does not apply. ALIAS changes names in both inputs and outputs, so it is not an output-header-only intervention. Label forms, tokenization, prompts, and demonstration choices lack independent replication. Effects cannot be attributed uniquely to identity information or generalized to real agents.','', 'Output-token counts include generated EOS tokens (text_tokens are stored separately). Generate time is GPU-synchronized batch wall time, not independent per-example latency. Concurrent GPU workloads and sequence lengths affect costs. The dispatch ledger also records allocated GPU time for loading, saving, and other work.','', 'Evidence: top-level REGISTRATION.md; four templates in prompts/; frozen configurations and examples in data/; raw text, token IDs, termination reasons, and completeness markers in runs/; analysis/scores-*, graded-*, length-selection.json, and completion-audit.json; and logs/. Cross-model validation and real-task transfer remain future work. Results have not been externally published.','']
(R/'REPORT.md').write_text('\n'.join(lines))
print(json.dumps(audit,ensure_ascii=False)[:1500])
