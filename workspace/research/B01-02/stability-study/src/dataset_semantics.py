"""Distinguish unseen tool sequences from unseen terminal affine functions."""
import collections,hashlib,json
from common import R,write
from protocol import read,LIB
import dsl

def signature(chain):return dsl.signature(dsl.expand(chain,LIB))

training={signature(row['chain']) for row in read('train')}
prior={signature(row['chain']) for split in ['train','dev','test','independent'] for row in read(split)}
programs=[];summary=[]
for label,path in [('old',R/'data/independent.jsonl'),('fresh',R/'fresh-confirmation/data/independent.jsonl')]:
    rows=list(map(json.loads,path.read_text().splitlines()));chains=sorted({tuple(row['chain']) for row in rows})
    for chain in chains:
        s=signature(chain)
        programs.append(dict(dataset=label,chain=list(chain),length=len(chain),
                             signature_sha256=hashlib.sha256(json.dumps(s).encode()).hexdigest(),
                             equivalent_to_training_function=s in training,
                             equivalent_to_any_prior_function=s in prior,
                             has_adjacent_repeat=any(a==b for a,b in zip(chain,chain[1:]))))
    for length in ['all',3,4,5,6,8]:
        selected=[p for p in programs if p['dataset']==label and (length=='all' or p['length']==length)]
        summary.append(dict(dataset=label,length=length,programs=len(selected),
                            unique_terminal_functions=len({p['signature_sha256'] for p in selected}),
                            training_function_overlap=sum(p['equivalent_to_training_function'] for p in selected),
                            any_prior_function_overlap=sum(p['equivalent_to_any_prior_function'] for p in selected),
                            adjacent_repeat_programs=sum(p['has_adjacent_repeat'] for p in selected)))
write(R/'analysis/dataset-semantics.json',dict(programs=programs,summary=summary,note=(
    'Original extended set was selected for terminal-function novelty; fresh confirmation registration '
    'excludes exact tool sequences, not equivalent terminal functions. The affine signature is exact for this DSL. '
    'All 400 frozen fresh rows remain in primary evaluation; no outcome-based filtering. Old any-prior overlap '
    'includes the old set itself and must not be interpreted as training overlap.')))
old=next(x for x in summary if x['dataset']=='old' and x['length']=='all')
new=next(x for x in summary if x['dataset']=='fresh' and x['length']=='all')
lines=['# Dataset scope of the confirmation set',
       'The earlier 480-example generator deduplicates final affine functions and excludes functions from earlier training/development/test sets. The new confirmation set deduplicates tool-name sequences as registered. These are different conditions; new tool sequences are not automatically new final functions.',
       f'The new confirmation set has 100 distinct tool sequences and 400 examples, corresponding to {new["unique_terminal_functions"]} distinct final functions. Of these sequences, {new["training_function_overlap"]} have final functions equivalent to training-set functions, and {new["any_prior_function_overlap"]} have final functions equivalent to functions in any earlier input set at this stage, including the old independent set.',
       'This does not mean the long tool sequences or full operation trajectories appeared in training. Strict scoring requires every specified operation and intermediate state; reaching the same final state alone is insufficient. The limitation concerns claims of transfer to new functions.',
       'The primary analysis retains all 400 preregistered frozen examples and reports the two batches separately. Data are not reselected based on output scores. Program-level labels and counts by length are in the parent analysis/dataset-semantics.json.',
       'This scope check occurred after some new-confirmation jobs had completed, without changing data, methods, or scoring.']
(R/'fresh-confirmation/DATASET_SCOPE.md').write_text('\n\n'.join(lines)+'\n')
print('Old profile:',old);print('Fresh profile:',new)
