from pathlib import Path
import collections,json,math,statistics
from sandbox import R

def wilson(k,n):
 if not n:return None
 z=1.96;p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
 return [c-h,c+h]
def paired(a,b):
 assert set(a)==set(b)
 win=sum(b[t] and not a[t] for t in a);lose=sum(a[t] and not b[t] for t in a);m=win+lose
 return {'n':len(a),'b_wins':win,'a_wins':lose,'delta':(win-lose)/len(a),'exact_two_sided_sign_p':min(1,2*sum(math.comb(m,k) for k in range(min(win,lose)+1))/2**m) if m else 1,'note':'Exploratory task-paired comparison; instances share three generators. No claim of independent real-world task sampling.'}
rows=[];groups={}
for p in sorted((R/'runs').glob('*/*/summary.json')):
 s=json.loads(p.read_text());s['run']=str(p.parent.relative_to(R));s['tag']=p.parent.parent.name;s['worker_tag']=s['tag'];s['tag']=('controlled-v3-main-'+s['context_policy']) if s['tag'].startswith('controlled-v3-main-') else ('controlled-v2-main-'+s['context_policy']) if s['tag'].startswith('controlled-v2-main-') else (('controlled-main-'+s['context_policy']) if s['tag'].startswith('controlled-main-') else s['tag']);events=[json.loads(l) for l in (p.parent/'trajectory.jsonl').read_text().splitlines()]
 s['protocol_error_turns']=sum('protocol_error' in e for e in events);s['tool_calls']=sum(len(e.get('tool_calls',[])) for e in events);s['length_capped_turns']=sum(e['generation_stop']=='length_limit' for e in events);s['action_turns']=sum(bool(e.get('tool_calls')) for e in events)
 s['narrated_action_turns']=sum(bool(e.get('tool_calls')) and bool(e.get('content','').strip()) for e in events)
 notes=[c['function']['arguments'].get('note') for e in events for c in e.get('tool_calls',[])];s['note_calls']=sum(x is not None for x in notes);s['nonempty_note_calls']=sum(bool(x) for x in notes);s['note_words']=sum(len(x.split()) for x in notes if x)
 rows.append(s)
for tag in sorted(set(s['tag'] for s in rows)):
 xs=[s for s in rows if s['tag']==tag];k=sum(s['grade']['complete'] for s in xs);groups[tag]={'n':len(xs),'complete':k,'rate':k/len(xs),'wilson95':wilson(k,len(xs)),'categories':dict(collections.Counter(s['category'] for s in xs)),'mean_generated_tokens':statistics.mean(s['generated_tokens'] for s in xs),'mean_input_tokens':statistics.mean(s['input_tokens'] for s in xs),'mean_turns':statistics.mean(s['turns'] for s in xs),'mean_tool_calls':statistics.mean(s['tool_calls'] for s in xs),'protocol_error_turns':sum(s['protocol_error_turns'] for s in xs),'tool_errors':sum(s['tool_errors'] for s in xs),'narrated_action_turns':sum(s['narrated_action_turns'] for s in xs),'action_turns':sum(s['action_turns'] for s in xs),'nonempty_note_calls':sum(s['nonempty_note_calls'] for s in xs),'note_calls':sum(s['note_calls'] for s in xs),'mean_note_words':statistics.mean(s['note_words'] for s in xs),'by_family':{f:{'n':sum(s['family']==f for s in xs),'complete':sum(s['family']==f and s['grade']['complete'] for s in xs)} for f in set(s['family'] for s in xs)}}
comparisons={}
for prefix in ['long-','queue-main-','notes-main-','queue-notes-main-','notes-replication-','compact-main-']:
 base={s['task']:s['grade']['complete'] for s in rows if s['tag']==prefix+'plan'}
 for c in ['reminder','identity','todo']:
  other={s['task']:s['grade']['complete'] for s in rows if s['tag']==prefix+c}
  if base and set(base)==set(other):comparisons[prefix+c+' vs plan']=paired(base,other)
for c in ['plan','reminder','identity','todo']:
 full={s['task']:s['grade']['complete'] for s in rows if s['tag']=='queue-notes-main-'+c and s['n_requirements']==24}
 compact={s['task']:s['grade']['complete'] for s in rows if s['tag']=='compact-main-'+c and s['task'] in full}
 if len(full)==3 and set(full)==set(compact):comparisons['compact vs full-history '+c]=paired(full,compact)
for prefix in ['controlled-main-','controlled-v2-main-']:
 for policy in ['compact','trim']:
  full={s['task']:s['grade']['complete'] for s in rows if s['tag']==prefix+'full'}
  variant={s['task']:s['grade']['complete'] for s in rows if s['tag']==prefix+policy}
  if len(full)==3 and set(full)==set(variant):comparisons[prefix+policy+' vs full']=paired(full,variant)
full={s['task']:s['grade']['complete'] for s in rows if s['tag']=='controlled-v2-main-full'}
sanitized={s['task']:s['grade']['complete'] for s in rows if s['tag']=='controlled-v3-main-sanitize'}
if len(full)==3 and set(full)==set(sanitized):comparisons['controlled sanitize vs full']=paired(full,sanitized)
old={}
for p in (R.parent/'agent-study/runs').glob('main-*/*/summary.json'):
 s=json.loads(p.read_text())
 if s['condition']=='plan':old[s['task']]=s['grade']['complete']
for mode in ['zero','fewshot']:
 new={s['task']:s['grade']['complete'] for s in rows if s['tag'].startswith('regression-'+mode)}
 if old and set(old)==set(new):comparisons['native-'+mode+' vs archived-custom-plan']=paired(old,new)
cost=[]
for p in sorted((R/'analysis').glob('*-completed.json')):
 x=json.loads(p.read_text())
 if isinstance(x,dict) and 'jobs_requested' in x:
  cost.append({'tag':p.name.removesuffix('-completed.json'),'gpu_reserved_seconds':x['seconds'],'jobs_requested':x['jobs_requested'],'jobs_completed':x['jobs_completed'],'peak_memory_bytes':x['peak_memory_bytes']})
result={'groups':groups,'comparisons':comparisons,'gpu_reserved_hours':sum(x['gpu_reserved_seconds'] for x in cost)/3600,'process_costs':cost,'runs':rows}
(R/'analysis/results.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:v for k,v in result.items() if k not in ['runs','process_costs']},indent=2))
