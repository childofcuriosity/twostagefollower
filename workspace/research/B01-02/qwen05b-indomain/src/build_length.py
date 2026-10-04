"""Freeze an in-domain extension after the previous STEP tier is scored."""
from common import R, B, MODEL, WORLD, CONDITIONS, ALIASES, sha, write, target, dsl
import argparse
import collections
import json
import random
from transformers import AutoTokenizer

p = argparse.ArgumentParser()
p.add_argument('--max-length', type=int, required=True, choices=range(4,9))
a = p.parse_args()
L = a.max_length
root = R/f'data/L{L}'
root.mkdir(parents=True, exist_ok=False)
rng = random.Random(900+L)
weights = [len(WORLD['library'])**d for d in range(1,L+1)]
def chain():
    k = rng.randrange(sum(weights))
    d = next(d for d,w in enumerate(weights,1) if (k:=k-w) < 0)
    return tuple(rng.randrange(len(WORLD['library'])) for _ in range(d))
seen = set()
uid = L*1_000_000
def row(c, split):
    global uid
    while True:
        x = tuple(rng.randrange(10) for _ in range(4))
        key = (tuple(c), x)
        if key not in seen:
            seen.add(key)
            break
    uid += 1
    return {'id': uid, 'split': split, 'chain': list(c), 'x': x, 'depth': len(c)}

train = [row(chain(), 'train') for _ in range(4096)]
previous = [json.loads(line) for line in (R/f'data/L{L-1}/test.jsonl').read_text().splitlines()]
seen.update((tuple(r['chain']), tuple(r['x'])) for r in previous)
new = [row(tuple(rng.randrange(len(WORLD['library'])) for _ in range(L)), 'iid')
       for _ in range(128)]
test = previous + new
assert len(test) == 128*(L-1)
assert set(len(x['chain']) for x in train) == set(range(1,L+1))
assert len({r['id'] for r in test}) == len(test)
for name, rows in [('train', train), ('test', test)]:
    (root/f'{name}.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
for name in ('dev.jsonl','library.json','worlds.json'):
    (root/name).symlink_to((B/'data'/name).resolve())

tok = AutoTokenizer.from_pretrained(MODEL, local_files_only=True)
limits = {}
for condition in CONDITIONS:
    names = ALIASES if condition == 'alias' else WORLD['names']
    training = [len(tok(dsl.prompt(r,names),add_special_tokens=False).input_ids)
                +len(tok(target(r,WORLD['library'],condition,names),add_special_tokens=False).input_ids)+1
                for r in train]
    targets = [len(tok(target(r,WORLD['library'],condition,names),add_special_tokens=False).input_ids)+1
               for r in test]
    limits[condition] = {'max_train_sequence':max(training),
                         'max_test_target_tokens':max(targets),
                         'target_tokens_per_epoch':sum(
                             len(tok(target(r,WORLD['library'],condition,names),add_special_tokens=False).input_ids)+1
                             for r in train)}
max_train = max(x['max_train_sequence'] for x in limits.values())
max_test = max(x['max_test_target_tokens'] for x in limits.values())
train_cap = 256 if max_train <= 256 else 512
generation_cap = 256 if max_test <= 256 else 512
assert max_train <= train_cap and max_test <= generation_cap
adjustments = []
if train_cap != 256: adjustments.append('train sequence assertion 256 -> 512 for longer targets')
if generation_cap != 256: adjustments.append('greedy generation max_new_tokens 256 -> 512 for longer targets')
write(root/'manifest.json', {'length':L,'sampler':'uniform over every chain of 1..L tools; four uniform digits; unique chain+digits',
    'data_seed':900+L,'train_rows':len(train),'test_rows':len(test),
    'test_source':f'previous L{L-1} in-domain test plus 128 frozen length-{L} iid rows',
    'train_depth_counts':dict(collections.Counter(str(len(r['chain'])) for r in train)),
    'test_depth_counts':dict(collections.Counter(str(len(r['chain'])) for r in test)),
    'limits':limits,'training_sequence_cap':train_cap,'generation_cap':generation_cap,
    'compatibility_adjustments':adjustments,
    'sha256':{name:sha(root/f'{name}.jsonl') for name in ('train','test')},
    'source_sha256':sha(B/'src/run.py'),'worlds_sha256':sha(B/'data/worlds.json')})
print(json.dumps(json.loads((root/'manifest.json').read_text()),indent=2))
