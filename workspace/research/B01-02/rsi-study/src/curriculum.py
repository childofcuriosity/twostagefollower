from common import *
import loop_data as ld
import statistics,collections
rows=[]
families_by_id={f['id']:f for f in load()}
paths=list((ROOT/'runs').glob('loop-*/round*/training-data.jsonl'))+list((ROOT/'runs').glob('branch-*/training-data.jsonl'))
for p in paths:
 run=p.parent.parent if p.parent.name.startswith('round') else p.parent;parts=run.name.split('-');domain=parts[1];data=[json.loads(l) for l in p.read_text().splitlines()];lib=json.loads((p.parent/'libraries.json').read_text());counts=collections.Counter(op for r in data for op in r['ops'])
 rows.append(dict(run=run.name,round=int(p.parent.name[5:]) if p.parent.name.startswith('round') else None,domain=domain,examples=len(data),mean_primitive_length=statistics.mean(len(r['ops']) for r in data),primitive_counts=dict(counts),unique_programs=len({tuple(r['ops']) for r in data}),unique_semantics=len({ld.engine(domain).signature(tuple(r['ops'])) for r in data}),fraction_empty_libraries=statistics.mean(not v for v in lib.values()),mean_library_size=statistics.mean(len(v) for v in lib.values()),source_heldout_compression=statistics.mean(utility(families_by_id[int(fid)]['test'],v) for fid,v in lib.items()),source_support_compression=statistics.mean(utility(families_by_id[int(fid)]['support'],v) for fid,v in lib.items()),contains_ends_fraction=statistics.mean('ends' in r['ops'] for r in data)))
(ROOT/'analysis/curriculum-rows.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
families=load();domain=[]
for split in ['train','dev','test']:
 fs=[f for f in families if f['split']==split];domain.append(dict(split=split,families=len(fs),motif_count=sum(len(f['motifs']) for f in fs),motifs_containing_ends=sum('ends' in CANDIDATES[c] for f in fs for c in f['motifs']),programs_containing_ends_fraction=statistics.mean('ends' in p for f in fs for p in f['test'])))
(ROOT/'analysis/curriculum-summary.json').write_text(json.dumps({'training_runs':len(rows),'task_distribution':domain,'interpretation':'Descriptive post-hoc curriculum statistics; lengths and token costs are mediators of changing the proposal source, not controlled separately.'},indent=2));print('curriculum stages',len(rows));print(domain)
