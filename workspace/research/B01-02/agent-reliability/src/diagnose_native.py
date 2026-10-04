"""Descriptive failure and role-drift audit; no causal labels inferred automatically."""
from pathlib import Path
import collections,json,re
from sandbox import R
from tasks import expected_data
x=json.loads((R/'analysis/results.json').read_text());audit=json.loads((R/'analysis/native-audit.json').read_text());lookup={r['run']:r for r in audit['records']};rows=[]
pattern=re.compile(r'(?im)^\s*(?:Human:|Assistant:|user\s*$|assistant\s*$|<tool_response>)')
for s in x['runs']:
 p=R/s['run'];meta=json.loads((R/'tasks'/s['task']/'task.json').read_text());events=[json.loads(l) for l in (p/'trajectory.jsonl').read_text().splitlines()];drift=[]
 for e in events:
  content=e.get('content',e['raw'] if 'protocol_error' in e else '')
  if pattern.search(content):drift.append({'turn':e['turn'],'input_tokens':e['input_tokens'],'excerpt':content[:1200]})
 row={'run':s['run'],'task':s['task'],'tag':s['tag'],'condition':s['condition'],'complete':s['grade']['complete'],'category':s['category'],'stop_reason':s['stop_reason'],'correct':s['grade']['completed_requirements'],'total':s['grade']['total_requirements'],'tool_errors':s['tool_errors'],'protocol_error_turns':s['protocol_error_turns'],'role_marker_turns':drift,'final_response':s['finish'],'failure_details':lookup.get(s['run'],{}).get('failures',[])}
 if s['family']=='queue':
  state=json.loads((p/'queue-state.json').read_text());delivered={v['ticket_id'] for v in state['receipts']};opened=set(state['opened']);row.update(delivered=len(delivered),opened=len(opened),unopened=len(meta['tickets'])-len(opened),opened_not_delivered=sorted(opened-delivered),delivered_but_incorrect=sum(not c['passed'] and c['id'] in delivered for c in s['grade']['checks']))
 elif s['family']=='data' and not s['grade']['complete']:
  mappings=[];initial=R/'tasks'/s['task']/'initial'
  for spec,check in zip(meta['specs'],s['grade']['checks']):
   if check['passed']:continue
   path=p/'final-workspace'/spec['path'];alt=path.with_name(re.sub(r'_0(\d)\.',r'_\1.',path.name));obs={'required_path':spec['path'],'exists':path.exists()}
   if not path.exists() and alt.exists():obs['unpadded_alternative']=str(alt.relative_to(p/'final-workspace'));path=alt
   if path.exists():
    try:
     value=json.loads(path.read_text());obs['matches_other_requirement_outputs']=[q['path'] for q in meta['specs'] if expected_data(initial,q)==value]
    except Exception as ex:obs['parse_error']=str(ex)
   mappings.append(obs)
  row['data_output_mapping']=mappings
 rows.append(row)
bytag={}
for tag in sorted(set(r['tag'] for r in rows)):
 rs=[r for r in rows if r['tag']==tag];bytag[tag]={'n':len(rs),'role_marker_runs':sum(bool(r['role_marker_turns']) for r in rs),'failed_with_role_markers':sum(bool(r['role_marker_turns']) and not r['complete'] for r in rs),'complete_with_role_markers':sum(bool(r['role_marker_turns']) and r['complete'] for r in rs)}
(R/'analysis/failure-diagnostics.json').write_text(json.dumps({'by_tag':bytag,'runs':rows,'notes':'Role-marker flags describe model-generated apparent dialogue/tool-response markers outside valid calls; they are not external messages or proof of causality. Output equivalence can match multiple requirements by coincidence. All failure assignments are artifact-based, not claims about hidden reasoning.'},indent=2))
print('Diagnosed',len(rows),'runs; failures',sum(not r['complete'] for r in rows))
