import argparse,json,time
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM,set_seed
from peft import PeftModel
from common import *
ap=argparse.ArgumentParser();ap.add_argument('--condition',choices=['base','flat','macro','mismatch'],required=True);ap.add_argument('--seed',type=int,required=True);a=ap.parse_args()
out=ROOT/'runs'/f'{a.condition}-s{a.seed}';out.mkdir(exist_ok=False)
start=time.time();set_seed(a.seed);torch.set_num_threads(4)
tok=AutoTokenizer.from_pretrained(PARENT/'model',local_files_only=True);tok.pad_token=tok.eos_token;tok.padding_side='left'
model=AutoModelForCausalLM.from_pretrained(PARENT/'model',torch_dtype=torch.bfloat16,attn_implementation='sdpa',local_files_only=True).cuda()
if a.condition!='base':
 c='macro' if a.condition=='mismatch' else a.condition
 model=PeftModel.from_pretrained(model,PARENT/f'runs/{c}-original-s{a.seed}/adapter')
model.eval();tasks=load();trie={};texts=[','.join(p)+'\n' for p in CANDIDATES]
for text in texts:
 node=trie
 for token in tok.encode(text,add_special_tokens=False)+[tok.eos_token_id]:node=node.setdefault(token,{})
records=[];counts={'input_tokens':0,'generated_tokens':0}
with (out/'proposals.jsonl').open('w',buffering=1) as log:
 for f in tasks:
  source=tasks[(f['id']+1)%len(tasks)] if a.condition=='mismatch' else f
  history='\n'.join(','.join(p) for p in source['support'])
  prompt='Choose one reusable subprogram of exactly two or three operations from rev,rot,inc,neg,swap,ends. It should compress the following successful programs by replacing repeated contiguous operations. Return only comma-separated operations.\nPrograms:\n'+history+'\nReusable program:\n'
  ins=tok([prompt]*16,return_tensors='pt',padding=True).to('cuda');width=ins.input_ids.shape[1]
  def allowed(batch_id,ids):
   node=trie
   for token in ids[width:].tolist():
    if token==tok.eos_token_id:return [tok.eos_token_id]
    node=node[token]
   return list(node)
  with torch.inference_mode():z=model.generate(**ins,max_new_tokens=32,do_sample=True,temperature=1.,top_k=0,top_p=1.,prefix_allowed_tokens_fn=allowed,pad_token_id=tok.pad_token_id,eos_token_id=tok.eos_token_id)
  tails=z[:,width:];raw=tok.batch_decode(tails,skip_special_tokens=True)
  for j,(txt,ids) in enumerate(zip(raw,tails)):
   assert txt in texts,repr(txt)
   r={'family':f['id'],'context_family':source['id'],'attempt':j,'prompt':prompt,'raw':txt,'candidate':texts.index(txt),'generated_tokens':int((ids!=tok.eos_token_id).sum())}
   log.write(json.dumps(r)+'\n');records.append(r)
  counts['input_tokens']+=int(ins.attention_mask.sum());counts['generated_tokens']+=sum(r['generated_tokens'] for r in records[-16:])
  print('completed family',f['id'],flush=True)
summary={'args':vars(a),'wall_seconds':time.time()-start,'counts':counts,'proposals':len(records),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'gpu':torch.cuda.get_device_name()}
(out/'summary.json').write_text(json.dumps(summary,indent=2));print(summary,flush=True)
