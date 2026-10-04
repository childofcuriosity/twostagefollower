"""Count registered inputs and exact/program overlap; no model predictions used."""
import collections,json
from protocol import R,read

sets={s:read(s) for s in ['train','test','independent']}
summary={s:dict(n=len(rs),lengths=dict(collections.Counter(len(r['chain']) for r in rs)),splits=dict(collections.Counter(r['split'] for r in rs)),programs=len({tuple(r['chain']) for r in rs}),unique_inputs=len({(tuple(r['x']),tuple(r['chain'])) for r in rs})) for s,rs in sets.items()}
tr={(tuple(r['x']),tuple(r['chain'])) for r in sets['train']};programs={tuple(r['chain']) for r in sets['train']}
for s in ['test','independent']:
    summary[s]['exact_overlap_train']=sum((tuple(r['x']),tuple(r['chain'])) in tr for r in sets[s])
    summary[s]['program_overlap_train_by_split']={sp:sum(tuple(r['chain']) in programs for r in sets[s] if r['split']==sp) for sp in sorted({r['split'] for r in sets[s]})}
summary['independent']['exact_overlap_test']=len({(tuple(r['x']),tuple(r['chain'])) for r in sets['independent']}&{(tuple(r['x']),tuple(r['chain'])) for r in sets['test']})
assert all(summary[s]['exact_overlap_train']==0 for s in ['test','independent'])
assert summary['independent']['exact_overlap_test']==0
(R/'analysis/data-audit.json').write_text(json.dumps(summary,indent=2));print('Data coverage and no exact train/test overlap verified')
