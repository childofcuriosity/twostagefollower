from pathlib import Path
import collections,json
R=Path(__file__).resolve().parents[1];v=json.loads((R/'analysis/verification.json').read_text());replays={(x['task'],x['condition']):x for x in json.loads((R/'analysis/replay.json').read_text())};rows=[]
for case in v['cases']:
 p=R/case['source'];events=[json.loads(x) for x in (p/'trajectory.jsonl').read_text().splitlines()];errors=collections.Counter();truncated=0
 for event in events:
  err=event.get('tool_result',{}).get('error','')
  if err:errors[err.split(':',1)[0]]+=1
  truncated+=event['generation_stop']=='length_limit'
 details=[]
 if not case['grade']['complete']:
  for item in case['failure_details']:
   info=dict(item);path=p/'final-workspace'/item['path']
   if path.exists() and path.suffix=='.py':
    try:compile(path.read_text(),str(path),'exec');info['python_syntax_valid']=True
    except SyntaxError as ex:info['python_syntax_valid']=False;info['syntax_error']=str(ex)
   details.append(info)
 replay=replays[(case['task'],case['condition'])]
 rows.append(dict(task=case['task'],condition=case['condition'],category=case['category'],complete=case['grade']['complete'],parser_or_tool_exception_counts=dict(errors),generation_limit_turns=truncated,failure_details=details,first_complete_turn=replay['first_complete_turn'],completed_then_regressed=replay['first_complete_turn'] is not None and not case['grade']['complete'],post_completion_action_count=len(replay['post_completion_actions']),blocked_claim_review='No missing external inputs in fixture; claim concerns recoverable internal execution/protocol issue, not a verified need for user information.' if case['category']=='claimed_blocked' else None))
(R/'analysis/failure-diagnostics.json').write_text(json.dumps(rows,indent=2))
print('Reviewed',len(rows),'cases;',sum(x['completed_then_regressed'] for x in rows),'completed then regressed;',sum(bool(x['parser_or_tool_exception_counts']) for x in rows),'with parser/tool exceptions')
for x in rows:
 if x['completed_then_regressed']:print('REGRESSION',x['task'],x['condition'])
