from pathlib import Path
import hashlib,json,re
from sandbox import R

def events(path):return [json.loads(l) for l in (path/'trajectory.jsonl').read_text().splitlines()]
def equal_turn(a,b):return a['raw']==b['raw'] and a.get('tool_results',[])==b.get('tool_results',[]) and a.get('protocol_error')==b.get('protocol_error') and a['input_tokens']==b['input_tokens'] and a['generated_tokens']==b['generated_tokens'] and a['last_token_id']==b['last_token_id'] and a['generation_stop']==b['generation_stop']
def digest(root):return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
runs=[]
for p in (R/'runs').glob('controlled-v[23]-main-*/*/summary.json'):
 s=json.loads(p.read_text());runs.append((p.parent,s))
full={s['task']:(p,s) for p,s in runs if p.parent.name.startswith('controlled-v2-') and s['context_policy']=='full'}
checks=[]
for p,s in runs:
 if s['context_policy'] not in ['compact','trim','sanitize']:continue
 base,bs=full[s['task']];a=events(base);b=events(p)
 if s['context_policy']=='sanitize':
  changed=[e['turn'] for e in b if e.get('history_content',e.get('content',''))!=e.get('content','')]
  prefix=(changed[0]+1) if changed else min(len(a),len(b));intervention={'first_filtered_history_turn':changed[0] if changed else None}
 else:
  comp=json.loads((p/'compactions.json').read_text());prefix=comp[0]['before_turn'] if comp else min(len(a),len(b));intervention={'first_handoff_before_turn':comp[0]['before_turn'] if comp else None}
 ok=len(a)>=prefix and len(b)>=prefix and all(equal_turn(a[i],b[i]) for i in range(prefix))
 checks.append({'task':s['task'],'policy':s['context_policy'],'unchanged_prefix_turns':prefix,'pre_intervention_identical':ok,'full_delivered':bs['grade'].get('delivered'),'variant_delivered':s['grade'].get('delivered'),'full_correct':bs['grade']['completed_requirements'],'variant_correct':s['grade']['completed_requirements'],'full_stop':bs['stop_reason'],'variant_stop':s['stop_reason'],**intervention})
 assert ok,checks[-1]
repeat=[]
for p,s in runs:
 if p.parent.name.startswith('controlled-v3-') and s['context_policy']=='full':
  base,bs=full[s['task']];a=events(base);b=events(p);ok=len(a)==len(b) and all(equal_turn(x,y) for x,y in zip(a,b)) and digest(base/'final-workspace')==digest(p/'final-workspace') and bs['grade']==s['grade']
  repeat.append({'task':s['task'],'all_model_outputs_and_tool_results_identical':ok,'turns':len(a),'correct':s['grade']['completed_requirements']});assert ok,repeat[-1]
case=[]
for task,(p,s) in full.items():
 es=events(p);case.append({'task':task,'correct':s['grade']['completed_requirements'],'delivered':s['grade'].get('delivered'),'total':s['n_requirements'],'stop':s['stop_reason'],'role_marker_turns':[e['turn'] for e in es if re.search(r'(?im)^\s*(Human:|Assistant:|user\s*$|assistant\s*$|<tool_response>)',e.get('content',''))],'generation_cap_turns':[e['turn'] for e in es if e['generation_stop']=='length_limit'],'protocol_error_turns':[e['turn'] for e in es if 'protocol_error' in e],'final_response':s['finish'],'source':str(p.relative_to(R))})
assert len(checks)==9 and len(repeat)==1,(len(checks),len(repeat))
(R/'analysis/mechanism-audit.json').write_text(json.dumps({'paired_prefix_checks':checks,'deterministic_rerun':repeat,'full_history_cases':case,'scope':'Three fixed synthetic workflows. Role filtering is exploratory, selected after observing one full-history failure, then applied to all three cases. No broad or unique-identity claim.'},indent=2));print('PASS paired prefixes and exact deterministic failure rerun')
