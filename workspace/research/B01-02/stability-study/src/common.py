import json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
O=R.parent/'oracle-study'
sys.path.insert(0,str(O/'src'))
from protocol import MODELS,read

def checkpoint(model,condition,seed,step):
    return O/'runs'/f'{model}-{condition}-s{seed}'/'checkpoints'/f'step{step:04d}'/'adapter'

def rows(split):
    return [json.loads(l) for l in (R/'data'/f'{split}.jsonl').read_text().splitlines()]

def write(p,data):
    p.write_text(json.dumps(data,indent=2,ensure_ascii=False))
