"""Freeze the first length extension using the old chain-uniform sampler."""
from common import R, B, MODEL, WORLD, CONDITIONS, ALIASES, sha, write, target, dsl
import itertools
import json
import random
from transformers import AutoTokenizer

L = 3
root = R/'data/L3'
root.mkdir(parents=True, exist_ok=False)
rng = random.Random(900+L)
chains = [(i,) for i in range(len(WORLD['library']))]
chains += list(itertools.product(range(len(WORLD['library'])), repeat=2))
chains += list(itertools.product(range(len(WORLD['library'])), repeat=3))
seen = set()
uid = 3_000_000
def row(chain, split):
    global uid
    while True:
        x = tuple(rng.randrange(10) for _ in range(4))
        key = (tuple(chain), x)
        if key not in seen:
            seen.add(key)
            break
    uid += 1
    return {'id': uid, 'split': split, 'chain': list(chain), 'x': x, 'depth': len(chain)}

train = [row(rng.choice(chains), 'train') for _ in range(4096)]
old_iid = [json.loads(line) for line in (B/'data/test.jsonl').read_text().splitlines()
           if json.loads(line)['split'] == 'iid']
assert len(old_iid) == 128
seen.update((tuple(r['chain']), tuple(r['x'])) for r in old_iid)
new_iid = [row(tuple(rng.randrange(len(WORLD['library'])) for _ in range(3)), 'iid')
           for _ in range(128)]
test = old_iid + new_iid
assert set(len(x['chain']) for x in train) == {1,2,3}
assert len({r['id'] for r in test}) == len(test)
for name, rows in [('train', train), ('test', test)]:
    (root/f'{name}.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
(root/'dev.jsonl').symlink_to((B/'data/dev.jsonl').resolve())
(root/'library.json').symlink_to((B/'data/library.json').resolve())
(root/'worlds.json').symlink_to((B/'data/worlds.json').resolve())

tok = AutoTokenizer.from_pretrained(MODEL, local_files_only=True)
limits = {}
for condition in CONDITIONS:
    names = ALIASES if condition == 'alias' else WORLD['names']
    training = [len(tok(dsl.prompt(r,names), add_special_tokens=False).input_ids)
                +len(tok(target(r,WORLD['library'],condition,names), add_special_tokens=False).input_ids)+1
                for r in train]
    targets = [len(tok(target(r,WORLD['library'],condition,names), add_special_tokens=False).input_ids)+1
               for r in test]
    limits[condition] = {'max_train_sequence': max(training),
                         'max_test_target_tokens': max(targets),
                         'target_tokens_per_epoch': sum(
                             len(tok(target(r,WORLD['library'],condition,names),add_special_tokens=False).input_ids)+1
                             for r in train)}
assert max(x['max_train_sequence'] for x in limits.values()) <= 256
assert max(x['max_test_target_tokens'] for x in limits.values()) <= 256
write(root/'manifest.json', {'length': L, 'sampler': 'rng.choice over all 1/2/3 tool chains; four uniform digits; unique chain+digits',
    'data_seed': 900+L, 'train_rows':len(train), 'test_rows':len(test),
    'test_source': 'original 128 iid rows plus 128 frozen length-3 iid rows',
    'train_depth_counts':{str(d):sum(len(r['chain'])==d for r in train) for d in range(1,4)},
    'test_depth_counts':{str(d):sum(len(r['chain'])==d for r in test) for d in range(1,4)},
    'limits':limits,'compatibility_adjustments':[],
    'sha256':{name:sha(root/f'{name}.jsonl') for name in ('train','test')},
    'source_sha256':sha(B/'src/run.py'),'worlds_sha256':sha(B/'data/worlds.json')})
print(json.dumps(json.loads((root/'manifest.json').read_text()),indent=2))
