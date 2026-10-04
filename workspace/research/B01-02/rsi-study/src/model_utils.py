import time,json
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM,set_seed
from peft import PeftModel
from common import *
def load_model(name,adapter=None,trainable=False):
 path=model_path(name);tok=AutoTokenizer.from_pretrained(path,local_files_only=True);tok.pad_token=tok.eos_token;tok.padding_side='left'
 model=AutoModelForCausalLM.from_pretrained(path,torch_dtype=torch.bfloat16,attn_implementation='sdpa',local_files_only=True).cuda()
 if adapter:model=PeftModel.from_pretrained(model,adapter,is_trainable=trainable)
 return model,tok

def propose(model,tok,f,style='instruction',temperature=1.,n=64,seed=11):
 set_seed(seed);model.eval();model.config.use_cache=True
 texts=[','.join(p)+'\n' for p in CANDIDATES];trie={}
 for txt in texts:
  node=trie
  for t in tok.encode(txt,add_special_tokens=False)+[tok.eos_token_id]:node=node.setdefault(t,{})
 prompt=proposal_prompt(f,style);out=[];start=time.time()
 for offset in range(0,n,32):
  ins=tok([prompt]*min(32,n-offset),padding=True,return_tensors='pt').to('cuda');width=ins.input_ids.shape[1]
  def allowed(batch,ids):
   node=trie
   for t in ids[width:].tolist():
    if t==tok.eos_token_id:return [tok.eos_token_id]
    node=node[t]
   return list(node)
  with torch.inference_mode():z=model.generate(**ins,max_new_tokens=32,do_sample=True,temperature=temperature,top_k=0,top_p=1.,prefix_allowed_tokens_fn=allowed,pad_token_id=tok.eos_token_id,eos_token_id=tok.eos_token_id)
  tokens=z[:,width:];raw=tok.batch_decode(tokens,skip_special_tokens=True)
  for j,(txt,ids) in enumerate(zip(raw,tokens)):
   assert txt in texts,(repr(txt),tok.name_or_path)
   out.append(dict(attempt=offset+j,raw=txt,candidate=texts.index(txt),generated_tokens=int((ids!=tok.eos_token_id).sum())))
 return dict(family=f['id'],split=f['split'],style=style,temperature=temperature,seed=seed,prompt=prompt,proposals=out,seconds=time.time()-start)
