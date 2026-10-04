"""Post-hoc, explicitly designed primitive-coverage intervention."""
import argparse,subprocess,os,sys,time
from common import *
from model_utils import load_model,propose
ap=argparse.ArgumentParser();ap.add_argument('--seed',type=int,required=True);a=ap.parse_args();root=ROOT/'coverage';start=time.time()
# Common data prepared once by launcher before workers begin.
import run
run.ROOT=root;sys.argv=['run.py','--condition','macro','--seed',str(a.seed),'--steps','512'];run.main()
import torch,gc
gc.collect();torch.cuda.empty_cache()
out=ROOT/'runs'/f'coverage-s{a.seed}';out.mkdir(exist_ok=False)
model,tok=load_model('qwen1.5b',root/f'runs/macro-original-s{a.seed}/adapter')
with (out/'proposals.jsonl').open('w',buffering=1) as log:
 for f in [f for f in load() if f['split']=='test']:
  for style,temp in [('instruction',1.),('concise',1.),('fewshot',1.),('instruction',1.5)]:log.write(json.dumps(propose(model,tok,f,style,temp,64,a.seed*10000+f['id']))+'\n')
(out/'summary.json').write_text(json.dumps(dict(seed=a.seed,wall_seconds=time.time()-start,raw_proposals=4096),indent=2))
