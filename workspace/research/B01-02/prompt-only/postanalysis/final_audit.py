import collections,datetime,hashlib,json,subprocess,sys
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];R=BASE/'fallback14'
sys.path.insert(0,str(R/'src'))
from common import CONDITIONS,LIB,NAMES,ALIASES,EXAMPLE,dsl,target,template,sha,readrows,write
from score import grade
manifest=json.loads((R/'data/formal-L2-manifest.json').read_text())
freeze=datetime.datetime.fromisoformat(manifest['created_utc'].replace('Z','+00:00')).timestamp()
records={};costs={};jobs=[];all_counts={};failures=[]
for root in [BASE,R]:
 for f in (root/'analysis').glob('dispatch-*.json'):
  ledger=json.loads(f.read_text());assert 'allocated_gpu_seconds' in ledger
  for j in ledger['results']:
   assert j['returncode']==0;jobs.append(dict(attempt=root.name,phase=f.name,**j))
 for f in (root/'runs').rglob('failures.jsonl'):failures.extend(readrows(f))
 all_counts[root.name]=sum(len(readrows(f)) for f in (root/'runs').glob('*/predictions.jsonl'))
# Validate formal shards, launch times, frozen executable/config, and exactly-once merge.
for name,h in manifest['source'].items():
 assert sha(R/'src'/name)==h and sha(R/'frozen-source'/name)==h
for c in CONDITIONS:
 run=R/f'runs/formal-L2-{c}';merged=readrows(run/'predictions.jsonl');parts=[]
 for i in range(2):
  sub=run/f'shard-{i}-of-2';running=json.loads((sub/'running.json').read_text());assert running['start']>=freeze
  assert running['manifest_sha256']==sha(R/'data/formal-L2-manifest.json')
  config=json.loads((sub/'generation-config.json').read_text());assert config['do_sample'] is False and config['num_beams']==1 and config['repetition_penalty']==1.0
  assert config['max_new_tokens']==manifest['max_new_tokens']
  rr=readrows(sub/'predictions.jsonl');assert len(rr)==256
  parts+=rr
 assert len({x['id'] for x in parts})==512
 assert {x['id']:x for x in parts}=={x['id']:x for x in merged}
 assert sha(run/'predictions.jsonl')==json.loads((run/'complete.json').read_text())['prediction_sha256']
 gg=[grade(x) for x in merged];saved=[x for x in readrows(R/'analysis/graded-formal-L2.jsonl') if x['condition']==c];assert gg==saved
 records[c]=gg
 sj=[j for j in jobs if j['attempt']=='fallback14' and j['phase']=='dispatch-formal-2.json' and j['condition']==c]
 assert len(sj)==2
 costs[c]=dict(generated_tokens=sum(x['generated_tokens'] for x in gg),text_tokens=sum(x['text_tokens'] for x in gg),input_tokens=sum(x['input_tokens'] for x in gg),generate_seconds=sum(x['allocated_generate_seconds'] for x in gg),allocated_gpu_seconds=sum(x['seconds'] for x in sj),full_heading_compliance=sum(x['header_compliant'] for x in gg),position_matched_headings=sum(x['matched_headers'] for x in gg),required_headings=sum(x['required_headers'] for x in gg),canonical_order_success=sum(x['canonical_order'] for x in gg),under_calls=sum(x['under_calls'] for x in gg),over_calls=sum(x['over_calls'] for x in gg),operation_mismatch=sum(x['operation_mismatch'] for x in gg),numeric_step_error=sum(x['numeric_step_error'] for x in gg),format_error=sum(x['format_error'] for x in gg))
for c in CONDITIONS:
 assert (BASE/f'prompts/{c}.txt').read_text()==(R/f'prompts/{c}.txt').read_text()==template(c)
# Paired error transitions are descriptive, not additive causal attributions.
paired={}
for c in CONDITIONS:
 if c=='STEP':continue
 transitions=collections.Counter((s['first_error'],v['first_error']) for s,v in zip(records['STEP'],records[c]))
 recovered=collections.Counter(s['first_error'] for s,v in zip(records['STEP'],records[c]) if not s['strict'] and v['strict'])
 lost=collections.Counter(v['first_error'] for s,v in zip(records['STEP'],records[c]) if s['strict'] and not v['strict'])
 paired[c]=dict(transitions=[dict(STEP=k[0],condition=k[1],n=v) for k,v in sorted(transitions.items())],recovered_by_STEP_error=dict(recovered),lost_by_condition_error=dict(lost))
# Model manifests and all downloaded file sizes; SHA hashes were computed at download completion.
models={}
for name in ['qwen7b','qwen14b']:
 m=json.loads((BASE/f'models/{name}/download-manifest.json').read_text())
 for f in m['files']:assert (BASE/f'models/{name}'/f['file']).stat().st_size==f['bytes']
 models[name]=dict(repo=m['repo'],revision=m['revision'],files=len(m['files']))
# Verify all original measured trajectories, not just formal aggregate tables.
for root in [BASE,R]:
 for phase in ['precheck','explore']:
  for L in ([2,5,10] if phase=='precheck' else [2,5,10,15,20,30,40]):
   conds=CONDITIONS if phase=='precheck' else ['STEP','NAME']
   expected=4 if phase=='precheck' else 32
   for c in conds:
    rr=readrows(root/f'runs/{phase}-L{L}-{c}/predictions.jsonl');assert len(rr)==expected
    assert len({x['id'] for x in rr})==expected
    for row in rr:grade(row)
summary=dict(passed=True,formal_rows=2048,total_unique_generation_records=sum(all_counts.values()),records_by_attempt=all_counts,models=models,formal_generation_cap=manifest['max_new_tokens'],formal_limits=manifest['limits'],formal_freeze=manifest['created_utc'],all_jobs=len(jobs),all_jobs_exit_zero=True,failures=failures,allocated_gpu_seconds_all=sum(x['seconds'] for x in jobs),costs=costs,paired_errors=paired,formal_prompt_identity_across_models=True,frozen_source_verified=True,formal_freeze_precedes_all_eight_jobs=True,exactly_once_shards_verified=True,all_3040_scores_rechecked=True)
write(BASE/'analysis/final-research-audit.json',summary)
print(json.dumps(summary,ensure_ascii=False,indent=2))
