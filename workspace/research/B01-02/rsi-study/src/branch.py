import argparse,time
from common import *
from model_utils import load_model
from loop import evaluate,collect,train_round
import loop_data as ld
from transformers import set_seed
import torch
ap=argparse.ArgumentParser();ap.add_argument('--seed',type=int,required=True);ap.add_argument('--domain',required=True);ap.add_argument('--source',choices=['updated','base'],required=True);a=ap.parse_args()
out=ROOT/'runs'/f'branch-{a.domain}-{a.source}-s{a.seed}';out.mkdir(exist_ok=False);start=time.time();set_seed(a.seed);torch.set_num_threads(4)
origin=ROOT/'runs'/f'loop-{a.domain}-shared-s{a.seed}'/'round1'
if a.domain=='strings':
 import common
 common.sig=lru_cache(None)(ld.secondary.signature);common.IDENTITY=common.sig(())
model,tok=load_model('qwen1.5b',origin/'adapter',True)
train=[f for f in load() if f['split']=='train']
records,libraries=collect(model,tok,train,a.seed*100000+2000,out/'train-proposals.jsonl',a.source=='base')
rows=ld.training_data(libraries,a.seed*100000+2000,a.domain);(out/'training-data.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows));(out/'libraries.json').write_text(json.dumps(libraries))
training=train_round(model,tok,rows,[],a.domain,a.seed+200,out)
execution=evaluate(model,tok,a.domain,out/'execution.jsonl')
origin_sha=hashlib.sha256((origin/'adapter/adapter_model.safetensors').read_bytes()).hexdigest()
summary=dict(args=vars(a),source_adapter=str(origin/'adapter'),source_adapter_sha256=origin_sha,training=training,execution=execution,before=json.loads((origin/'summary.json').read_text())['execution'],wall_seconds=time.time()-start)
(out/'summary.json').write_text(json.dumps(summary,indent=2))
