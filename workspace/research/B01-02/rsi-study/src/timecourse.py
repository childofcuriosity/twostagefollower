"""Replay original macro training with read-only probes; keep every checkpoint."""
import argparse,sys,os,time
from common import *
from model_utils import propose
import torch
from transformers import AutoTokenizer
ap=argparse.ArgumentParser();ap.add_argument('--seed',type=int,required=True);a=ap.parse_args()
r=ROOT/'timecourse'/f's{a.seed}';r.mkdir(parents=True,exist_ok=False)
for name,path in [('model',PARENT/'model'),('data',PARENT/'data')]:(r/name).symlink_to(os.path.relpath(path,r),target_is_directory=True)
(r/'runs').mkdir();out=ROOT/'runs'/f'timecourse-s{a.seed}';out.mkdir(exist_ok=False);start=time.time()
import run
run.ROOT=r
world=json.loads((PARENT/'data/worlds.json').read_text())['original'];test=[json.loads(l) for l in (PARENT/'data/test.jsonl').read_text().splitlines()]
tok=AutoTokenizer.from_pretrained(PARENT/'model',local_files_only=True);tok.pad_token=tok.eos_token;tok.padding_side='left';families=[f for f in load() if f['split']=='test'];captured={};step=0
base_get=run.get_peft_model;base_step=torch.optim.AdamW.step

def probe(n):
 model=captured['model'];model.config.use_cache=True;stage=out/f'step{n:04d}';stage.mkdir();model.save_pretrained(stage/'adapter')
 metrics=run.evaluate(model,tok,test,world,stage/'execution.jsonl')
 records=[];scores=[]
 for f in families:
  rec=propose(model,tok,f,n=16,seed=a.seed*10000+f['id']);records.append(rec);lib=select(f['support'],[x['candidate'] for x in rec['proposals']]);scores.append(dict(family=f['id'],compression=utility(f['test'],lib),selected=lib))
 (stage/'proposals.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in records));(stage/'summary.json').write_text(json.dumps(dict(step=n,execution=metrics,proposal=scores),indent=2));model.train();model.config.use_cache=False;print('PROBE COMPLETE',a.seed,n,flush=True)
def get_model(*args,**kwargs):
 model=base_get(*args,**kwargs);captured['model']=model;probe(0);return model
def optimizer_step(self,*args,**kwargs):
 global step
 value=base_step(self,*args,**kwargs);step+=1
 if step in [16,64,128,256,512]:probe(step)
 return value
run.get_peft_model=get_model;torch.optim.AdamW.step=optimizer_step
sys.argv=['run.py','--condition','macro','--seed',str(a.seed),'--steps','512'];run.main()
old=PARENT/f'runs/macro-original-s{a.seed}/adapter/adapter_model.safetensors';new=out/'step0512/adapter/adapter_model.safetensors'
summary=dict(seed=a.seed,wall_seconds=time.time()-start,steps=[0,16,64,128,256,512],matches_original_final_weights=hashlib.sha256(old.read_bytes()).hexdigest()==hashlib.sha256(new.read_bytes()).hexdigest(),note='All stochastic dropout is zero; optimizer and shuffle state preserved, generation seeds affect only probes. Check final weight hash explicitly.')
(out/'summary.json').write_text(json.dumps(summary,indent=2));print(summary,flush=True)
