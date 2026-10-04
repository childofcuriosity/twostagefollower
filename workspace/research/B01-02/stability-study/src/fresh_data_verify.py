"""Reproduce the frozen confirmation inputs without reading model predictions."""
import json,random,hashlib
from common import R
from protocol import read

forbidden={tuple(row['chain']) for split in ['train','dev','test','independent'] for row in read(split)}
rng=random.Random(2026092501);chosen=set();data=[]
for length in [3,4,5,6,8]:
    for i in range(20):
        while True:
            chain=tuple(rng.randrange(9) for _ in range(length))
            if chain not in forbidden and chain not in chosen:break
        chosen.add(chain);inputs=set()
        for j in range(4):
            while True:
                x=tuple(rng.randrange(10) for _ in range(4))
                if x not in inputs:break
            inputs.add(x);data.append(dict(id=f'context-confirm-L{length}-p{i:02d}-x{j}',split='length'+str(length),x=list(x),chain=list(chain),depth=length))
root=R/'fresh-confirmation';path=root/'data/independent.jsonl'
assert list(map(json.loads,path.read_text().splitlines()))==data
assert hashlib.sha256(path.read_bytes()).hexdigest()==json.loads((root/'analysis/dataset-manifest.json').read_text())['sha256']
print('Fresh dataset exact reproduction passed:',len(data),len(chosen))
