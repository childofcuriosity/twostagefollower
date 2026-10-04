"""Post-hoc stress intervention using the demonstrably degraded original macro proposer."""
import argparse,time,gc
from common import *
from model_utils import load_model
from loop import evaluate,collect,train_round
import loop_data as ld
from transformers import set_seed
import torch
ap=argparse.ArgumentParser();ap.add_argument('--seed',type=int,required=True);ap.add_argument('--domain',required=True);a=ap.parse_args();a.source='legacy'
out=ROOT/'runs'/f'branch-{a.domain}-legacy-s{a.seed}';out.mkdir(exist_ok=False);start=time.time();torch.set_num_threads(4);set_seed(a.seed)
origin=ROOT/'runs'/f'loop-{a.domain}-shared-s{a.seed}'/'round1'
if a.domain=='strings':
 import common
 common.sig=lru_cache(None)(ld.secondary.signature);common.IDENTITY=common.sig(())
# Teacher is the original numeric-domain macro adapter even in string stress test;
# only operation-sequence proposals transfer, and this distinction is recorded.
teacher,tok=load_model('qwen1.5b',PARENT/f'runs/macro-original-s{a.seed}/adapter')
records,libraries=collect(teacher,tok,[f for f in load() if f['split']=='train'],a.seed*100000+2000,out/'train-proposals.jsonl')
del teacher;gc.collect();torch.cuda.empty_cache()
model,tok=load_model('qwen1.5b',origin/'adapter',True)
rows=ld.training_data(libraries,a.seed*100000+2000,a.domain);(out/'training-data.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows));(out/'libraries.json').write_text(json.dumps(libraries))
training=train_round(model,tok,rows,[],a.domain,a.seed+200,out);execution=evaluate(model,tok,a.domain,out/'execution.jsonl')
summary=dict(args=vars(a),posthoc=True,source_adapter=str(origin/'adapter'),source_adapter_sha256=hashlib.sha256((origin/'adapter/adapter_model.safetensors').read_bytes()).hexdigest(),proposer_adapter=str(PARENT/f'runs/macro-original-s{a.seed}/adapter'),training=training,execution=execution,before=json.loads((origin/'summary.json').read_text())['execution'],wall_seconds=time.time()-start)
(out/'summary.json').write_text(json.dumps(summary,indent=2))
