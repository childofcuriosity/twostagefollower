import statistics
from common import *
import loop_data as ld
families=load();motifs={};notes=[]
for f in families:
 for c in f['motifs']:
  s=sig(CANDIDATES[c]);assert s not in motifs;motifs[s]=f['id']
 assert not ({sig(tuple(p)) for p in f['support']}&{sig(tuple(p)) for p in f['test']})
# Independent exhaustive segmentation check.
def brute(p,lib):
 if not p:return 0
 options=[1+brute(p[1:],lib)]
 for c in lib:
  op=CANDIDATES[c]
  if p[:len(op)]==op:options.append(1+brute(p[len(op):],lib))
 return min(options)
rng=random.Random(371)
for _ in range(100):
 p=tuple(rng.choices(OPS,k=7));lib=rng.sample(range(252),3);assert cost(p,lib)==brute(p,lib)
verified=[];raw_proposals=0;raw_execution=0;strict_changes=[]
for p in (ROOT/'runs').glob('robust-*/proposals.jsonl'):
 rows=[json.loads(l) for l in p.read_text().splitlines()]
 assert len(rows)==64
 for r in rows:
  assert len(r['proposals'])==64
  for v in r['proposals']:assert v['raw']==','.join(CANDIDATES[v['candidate']])+'\n'
  raw_proposals+=len(r['proposals'])
 verified.append(str(p.relative_to(ROOT)))
for p in (ROOT/'runs').glob('loop-*/round*/execution.jsonl'):
 domain=p.parent.parent.name.split('-')[1];rows=[json.loads(l) for l in p.read_text().splitlines()];assert len(rows)==256
 for r in rows:
  expected=ld.engine(domain).execute(r['x'],r['ops']);expected=list(expected) if domain=='digits' else expected
  assert expected==r['expected'];assert ld.answer(r['raw'],domain)==r['prediction'];assert r['correct']==(r['prediction']==expected)
 raw_execution+=len(rows);verified.append(str(p.relative_to(ROOT)))
for p in (ROOT/'runs').glob('branch-*/execution.jsonl'):
 domain=p.parent.name.split('-')[1];rows=[json.loads(l) for l in p.read_text().splitlines()];assert len(rows)==256
 for r in rows:
  expected=ld.engine(domain).execute(r['x'],r['ops']);expected=list(expected) if domain=='digits' else expected
  assert expected==r['expected'] and ld.answer(r['raw'],domain)==r['prediction'] and r['correct']==(r['prediction']==expected)
 raw_execution+=len(rows);verified.append(str(p.relative_to(ROOT)))
for kind,pattern in [('loop','loop-*/round*/training-data.jsonl'),('branch','branch-*/training-data.jsonl')]:
 for p in (ROOT/'runs').glob(pattern):
  run=p.parent.parent if kind=='loop' else p.parent;domain=run.name.split('-')[1]
  test=json.loads((ROOT/f'data/loop-eval-{domain}.json').read_text());sigs={ld.engine(domain).signature(tuple(r['ops'])) for r in test};rows=[json.loads(l) for l in p.read_text().splitlines()];assert len(rows)==2048
  assert not any(ld.engine(domain).signature(tuple(r['ops'])) in sigs for r in rows)
  logs=[json.loads(l) for l in (p.parent/'train.jsonl').read_text().splitlines()];assert len(logs)==128 and logs[-1]['exec_examples']==2048
  assert (p.parent/'adapter/adapter_model.safetensors').exists()
  verified.append(str(p.relative_to(ROOT)))
for run in (ROOT/'runs').glob('loop-*'):
 if not run.is_dir():continue
 for p in list(run.glob('round*/train-proposals.jsonl'))+list(run.glob('round*/test-proposals.jsonl'))+[run/'initial-replay.jsonl']:
  for l in p.read_text().splitlines():
   r=json.loads(l);assert len(r['proposals'])==16
   for v in r['proposals']:assert v['raw']==','.join(CANDIDATES[v['candidate']])+'\n'
   raw_proposals+=16
for p in (ROOT/'runs').glob('branch-*/train-proposals.jsonl'):
 for l in p.read_text().splitlines():
  r=json.loads(l);assert len(r['proposals'])==16
  for v in r['proposals']:assert v['raw']==','.join(CANDIDATES[v['candidate']])+'\n'
  raw_proposals+=16
world=json.loads((PARENT/'data/worlds.json').read_text())['original']
replica_tokens={}
for p in (ROOT/'replications').glob('*/runs/*/summary.json'):
 meta=json.loads(p.read_text());rows=[json.loads(l) for l in (p.parent/'predictions.jsonl').read_text().splitlines()];assert len(rows)==560;changes=0
 for r in rows:
  expected=list(dsl.execute(r['x'],dsl.expand(r['chain'],world['library'])));assert expected==r['expected'] and r['correct']==(r['prediction']==expected)
  strict=ld.answer(r['raw'],'digits');changes+=bool(r['correct'] and strict!=expected)
 raw_execution+=len(rows);strict_changes.append(dict(run=str(p.parent.relative_to(ROOT)),correct_false_positives_under_loose_parser=changes))
 if 'training' in meta:replica_tokens[str(p.parent.relative_to(ROOT))]=meta['training']['counts']
 verified.append(str(p.relative_to(ROOT)))
timecourse_matches=[]
for p in (ROOT/'runs').glob('timecourse-*/summary.json'):
 meta=json.loads(p.read_text());timecourse_matches.append({'seed':meta['seed'],'matches_original_final_weights':meta['matches_original_final_weights']})
 for q in p.parent.glob('step*/execution.jsonl'):
  rs=[json.loads(l) for l in q.read_text().splitlines()];assert len(rs)==560
  for r in rs:
   expected=list(dsl.execute(r['x'],dsl.expand(r['chain'],world['library'])))
   assert expected==r['expected'] and r['correct']==(r['prediction']==expected)
  raw_execution+=len(rs);verified.append(str(q.relative_to(ROOT)))
 for q in p.parent.glob('step*/proposals.jsonl'):
  for line in q.read_text().splitlines():
   record=json.loads(line);assert len(record['proposals'])==16
   for x in record['proposals']:assert x['raw']==','.join(CANDIDATES[x['candidate']])+'\n'
   raw_proposals+=16
for p in (ROOT/'timecourse').glob('s*/runs/*/predictions.jsonl'):
 rs=[json.loads(l) for l in p.read_text().splitlines()];assert len(rs)==560;raw_execution+=len(rs)
 for r in rs:assert list(dsl.execute(r['x'],dsl.expand(r['chain'],world['library'])))==r['expected'] and r['correct']==(r['prediction']==r['expected'])
matched=[]
for seed in [11,22,33]:
 for rnd in [1,2,3]:
  a=ROOT/f'runs/loop-digits-replay-s{seed}/round{rnd}/summary.json';b=ROOT/f'runs/loop-digits-shuffled-s{seed}/round{rnd}/summary.json'
  if a.exists() and b.exists():
   av=json.loads(a.read_text())['training']['counts'];bv=json.loads(b.read_text())['training']['counts']
   for key in ['aux_input_tokens','aux_target_tokens','aux_examples']:assert av[key]==bv[key],(seed,rnd,key)
   matched.append(dict(seed=seed,round=rnd,auxiliary_target_tokens=av['aux_target_tokens']))
# Post-hoc coverage and length-matched proposal controls.
for pattern,groups,n in [('coverage-*/proposals.jsonl',64,64),('length-*/proposals.jsonl',16,16)]:
 for p in (ROOT/'runs').glob(pattern):
  rs=[json.loads(l) for l in p.read_text().splitlines()];assert len(rs)==groups
  for r in rs:
   assert len(r['proposals'])==n
   for x in r['proposals']:assert x['raw']==','.join(CANDIDATES[x['candidate']])+'\n'
   if n==16:assert sorted(len(CANDIDATES[x['candidate']]) for x in r['proposals'])==[2]*8+[3]*8
   raw_proposals+=n
  verified.append(str(p.relative_to(ROOT)))
cworld=json.loads((ROOT/'coverage/data/worlds.json').read_text())['original']
for p in (ROOT/'coverage/runs').glob('*/summary.json'):
 meta=json.loads(p.read_text());rs=[json.loads(l) for l in (p.parent/'predictions.jsonl').read_text().splitlines()]
 for r in rs:
  expected=list(dsl.execute(r['x'],dsl.expand(r['chain'],cworld['library'])))
  assert expected==r['expected'] and r['correct']==(r['prediction']==expected)
 raw_execution+=len(rs)
 seed=meta['args']['seed'];old=json.loads((PARENT/f'runs/macro-original-s{seed}/summary.json').read_text());assert old['training']['counts']==meta['training']['counts']
 verified.append(str(p.relative_to(ROOT)))
branch_pairs=[]
for domain in ['digits','strings']:
 for seed in [11,22,33]:
  a=json.loads((ROOT/f'runs/branch-{domain}-base-s{seed}/summary.json').read_text());b=json.loads((ROOT/f'runs/branch-{domain}-updated-s{seed}/summary.json').read_text());assert a['source_adapter_sha256']==b['source_adapter_sha256']
  assert a['before']==b['before']
  legacy=json.loads((ROOT/f'runs/branch-{domain}-legacy-s{seed}/summary.json').read_text());assert legacy['source_adapter_sha256']==a['source_adapter_sha256'] and legacy['before']==a['before']
  branch_pairs.append(dict(domain=domain,seed=seed,source_sha256=a['source_adapter_sha256']))
# Registered originals preserved except explicitly superseded loop.py and append-only amendment notes.
registrations=[]
for filename in ['registration.json','loop-registration.json','loop-registration-v2.json','branch-registration.json','gradient-registration.json','analysis-registration.json','coverage-registration.json','length-registration.json','legacy-registration.json','timecourse-registration.json','timecourse-registration-v2.json','original-gradient-registration.json']:
 record=json.loads((ROOT/'analysis'/filename).read_text())
 for name,h in record['hashes'].items():
  if filename=='loop-registration.json' and name in ['src/loop.py','analysis/amendments.md']:continue
  if filename=='timecourse-registration.json' and name=='src/timecourse.py':continue
  assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,(filename,name)
 registrations.append(filename)
checkpoints={}
for p in list((ROOT/'runs').glob('loop-*/round*/adapter/adapter_model.safetensors'))+list((ROOT/'runs').glob('branch-*/adapter/adapter_model.safetensors'))+list((ROOT/'replications').glob('*/runs/*/adapter/adapter_model.safetensors'))+list((ROOT/'coverage/runs').glob('*/adapter/adapter_model.safetensors'))+list((ROOT/'runs').glob('timecourse-*/step*/adapter/adapter_model.safetensors'))+list((ROOT/'timecourse').glob('s*/runs/*/adapter/adapter_model.safetensors')):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 checkpoints[str(p.relative_to(ROOT))]=h.hexdigest()
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.rglob('*') if p.is_file() and p.suffix in ['.py','.md','.json','.jsonl','.csv','.txt'] and 'models' not in p.parts and p.name!='verification.json' and '__pycache__' not in p.parts and not p.is_symlink()}
result=dict(raw_execution_records=raw_execution,raw_proposals=raw_proposals,verified_files=verified,registered_files=registrations,unique_latent_motifs=len(motifs),independent_DP_checks=100,replay_shuffled_token_matches=matched,branch_start_matches=branch_pairs,replica_training_tokens=replica_tokens,replica_parser_audit=strict_changes,checkpoint_sha256=checkpoints,timecourse_final_weight_matches=timecourse_matches,manifest=manifest)
(ROOT/'analysis/verification.json').write_text(json.dumps(result,indent=2));print('Verified',raw_execution,'execution records;',raw_proposals,'proposals;',len(checkpoints),'checkpoints')
