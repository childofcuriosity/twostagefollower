import argparse,time,torch
from transformers import set_seed
from common import *
from model_utils import load_model
ap=argparse.ArgumentParser();ap.add_argument('--model',required=True);ap.add_argument('--condition',required=True);ap.add_argument('--seed',type=int,required=True);a=ap.parse_args()
out=ROOT/'runs'/f'length-{a.model}-{a.condition}-s{a.seed}';out.mkdir(exist_ok=False);start=time.time();torch.set_num_threads(4)
adapter=None
if a.condition!='base':adapter=(PARENT if a.model=='qwen1.5b' else ROOT/'replications'/a.model)/f'runs/{a.condition}-original-s{a.seed}/adapter'
model,tok=load_model(a.model,adapter);model.eval();records=[]
for f in [f for f in load() if f['split']=='test']:
 proposals=[];prompt=proposal_prompt(f)
 for length in [2,3]:
  set_seed(a.seed*10000+f['id']+length*1000000);texts=[','.join(p)+'\n' for p in CANDIDATES if len(p)==length];indices=[c for c,p in enumerate(CANDIDATES) if len(p)==length];trie={}
  for txt in texts:
   node=trie
   for t in tok.encode(txt,add_special_tokens=False)+[tok.eos_token_id]:node=node.setdefault(t,{})
  ins=tok([prompt]*8,return_tensors='pt',padding=True).to('cuda');width=ins.input_ids.shape[1]
  def allowed(b,ids):
   node=trie
   for token in ids[width:].tolist():
    if token==tok.eos_token_id:return [tok.eos_token_id]
    node=node[token]
   return list(node)
  with torch.inference_mode():z=model.generate(**ins,max_new_tokens=32,do_sample=True,temperature=1.,top_k=0,top_p=1.,prefix_allowed_tokens_fn=allowed,pad_token_id=tok.eos_token_id,eos_token_id=tok.eos_token_id)
  for raw in tok.batch_decode(z[:,width:],skip_special_tokens=True):
   assert raw in texts;proposals.append(dict(length=length,raw=raw,candidate=indices[texts.index(raw)]))
 selected=select(f['support'],[p['candidate'] for p in proposals]);records.append(dict(family=f['id'],prompt=prompt,proposals=proposals,selected=selected,compression=utility(f['test'],selected)))
(out/'proposals.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in records));(out/'summary.json').write_text(json.dumps(dict(args=vars(a),wall_seconds=time.time()-start,raw_proposals=256),indent=2))
