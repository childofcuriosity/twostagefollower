import argparse,time
from common import *
from model_utils import load_model
from loop import encode,batchify
import torch
ap=argparse.ArgumentParser();ap.add_argument('--seed',type=int,required=True);a=ap.parse_args();a.condition='original'
out=ROOT/'runs'/f'gradient-original-s{a.seed}';out.mkdir(exist_ok=False);start=time.time();waited=0.;torch.set_num_threads(4);records=[]
families=[f for f in load() if f['split']=='train'];world=json.loads((PARENT/'data/worlds.json').read_text())['original'];data=[json.loads(l) for l in (PARENT/'data/train.jsonl').read_text().splitlines()];random.Random(941).shuffle(data)
for st in [0,16,64,128,256,512]:
 origin=ROOT/'runs'/f'timecourse-s{a.seed}'/f'step{st:04d}'
 while not (origin/'summary.json').exists():
  before=time.time();time.sleep(60);waited+=time.time()-before
 model,tok=load_model('qwen1.5b',origin/'adapter',True);model.eval();model.config.use_cache=False;parameters=[p for p in model.parameters() if p.requires_grad]
 for b in range(3):
  eb=batchify(tok,[encode(tok,dsl.prompt(r,world['names']),dsl.target(r,world['library'],'macro',world['names'])) for r in data[b*4:(b+1)*4]])
  pe=[];targets=[]
  for f in families[b*4:(b+1)*4]:
   best=max((c for c in range(252) if sig(CANDIDATES[c])!=IDENTITY),key=lambda c:utility(f['support'],[c]));pe.append(encode(tok,proposal_prompt(f),','.join(CANDIDATES[best])+'\n'));targets.append(dict(family=f['id'],candidate=best))
  pb=batchify(tok,pe);le=model(**eb).loss;ge=torch.autograd.grad(le,parameters);lp=model(**pb).loss;gp=torch.autograd.grad(lp,parameters)
  dot=sum((x.float()*y.float()).sum() for x,y in zip(ge,gp));ne=sum(x.float().square().sum() for x in ge);np_=sum(y.float().square().sum() for y in gp)
  records.append(dict(step=st,batch=b,execution_loss=float(le),proposal_surrogate_loss=float(lp),dot=float(dot),execution_grad_norm=float(ne.sqrt()),proposal_grad_norm=float(np_.sqrt()),cosine=float(dot/(ne*np_).sqrt().clamp_min(1e-20)),targets=targets))
  del eb,pb,le,lp,ge,gp
 del model;torch.cuda.empty_cache()
(out/'results.json').write_text(json.dumps(dict(args=vars(a),records=records,wall_seconds=time.time()-start,checkpoint_wait_seconds=waited,active_wall_seconds=time.time()-start-waited,interpretation='Original-recipe execution gradient vs support-only valid best-macro NLL. Local surrogate diagnostic, not actual sampled-utility gradient.'),indent=2))
