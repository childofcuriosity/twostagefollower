"""Descriptive gradient alignment against proposal NLL, not actual utility gradient."""
import argparse,time
from common import *
from model_utils import load_model
from loop import encode,batchify
import loop_data as ld
import torch
ap=argparse.ArgumentParser();ap.add_argument('--condition',required=True);ap.add_argument('--seed',type=int,required=True);a=ap.parse_args()
out=ROOT/'runs'/f'gradient-{a.condition}-s{a.seed}';out.mkdir(exist_ok=False);start=time.time();torch.set_num_threads(4);records=[]
families=[f for f in load() if f['split']=='train']
for rnd in range(4):
 origin=ROOT/'runs'/f'loop-digits-{a.condition}-s{a.seed}'/f'round{rnd}'
 model,tok=load_model('qwen1.5b',origin/'adapter',True);model.eval();model.config.use_cache=False
 parameters=[p for p in model.parameters() if p.requires_grad]
 dataorigin=origin if rnd else origin.parent/'round1'
 erows=[json.loads(l) for l in (dataorigin/'training-data.jsonl').read_text().splitlines()]
 random.Random(417).shuffle(erows)
 for b in range(3):
  eb=batchify(tok,[encode(tok,ld.prompt(r,'digits'),ld.target(r,'digits')) for r in erows[b*4:(b+1)*4]])
  pe=[];targets=[]
  for f in families[b*4:(b+1)*4]:
   best=max(range(252),key=lambda c:utility(f['support'],[c]));target=','.join(CANDIDATES[best])+'\n';pe.append(encode(tok,proposal_prompt(f),target));targets.append(dict(family=f['id'],candidate=best))
  pb=batchify(tok,pe);le=model(**eb).loss;ge=torch.autograd.grad(le,parameters);lp=model(**pb).loss;gp=torch.autograd.grad(lp,parameters)
  dot=sum((x.float()*y.float()).sum() for x,y in zip(ge,gp));ne=sum(x.float().square().sum() for x in ge);np_=sum(y.float().square().sum() for y in gp)
  records.append(dict(round=rnd,batch=b,execution_loss=float(le),proposal_surrogate_loss=float(lp),dot=float(dot),execution_grad_norm=float(ne.sqrt()),proposal_grad_norm=float(np_.sqrt()),cosine=float(dot/(ne*np_).sqrt().clamp_min(1e-20)),targets=targets))
  del eb,pb,le,lp,ge,gp
 del model;torch.cuda.empty_cache()
(out/'results.json').write_text(json.dumps(dict(args=vars(a),records=records,wall_seconds=time.time()-start,interpretation='Gradients of teacher-forced proposal NLL using support-only frequency optimum. Not gradients of sampled proposal utility and not a causal explanation by itself.'),indent=2))
print('gradient complete',a.condition,a.seed,flush=True)
