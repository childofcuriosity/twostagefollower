import argparse,json,time,os,sys,hashlib,socket
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM,AutoTokenizer
from peft import PeftModel
R=Path(__file__).resolve().parents[1];P=R.parent
ap=argparse.ArgumentParser();ap.add_argument('--tag',required=True);a=ap.parse_args();a.model='qwen32b'
assert a.tag in ['frozen-with-library']+[f'{c}-s{s}' for s in [11,22,33] for c in ['flat','macro']]
sys.path.insert(0,str(P/'src'));import dsl
torch.set_num_threads(4);root=R/'qwen32b'
world=json.loads((P/'data/worlds.json').read_text())['original'];lib=world['library'];names=world['names']
rows=[json.loads(l) for l in (R/'data/extended-test.jsonl').read_text().splitlines()];out=R/'extended/qwen32b';out.mkdir(parents=True,exist_ok=True)
tok=AutoTokenizer.from_pretrained(root/'model',local_files_only=True);tok.pad_token=tok.eos_token;tok.padding_side='left'
model=AutoModelForCausalLM.from_pretrained(root/'model',torch_dtype=torch.bfloat16,attn_implementation='sdpa',local_files_only=True,low_cpu_mem_usage=True).cuda()
if a.tag!='frozen-with-library':
 condition,seed=a.tag.split('-s');path=root/f'runs/{condition}-original-s{seed}/adapter'
 model=PeftModel.from_pretrained(model,path,adapter_name=a.tag);model.set_adapter(a.tag)
def evaluate(tag,with_library):
 file=out/f'{tag}.jsonl';meta=out/f'{tag}-summary.json'
 if meta.exists():return json.loads(meta.read_text())
 assert not file.exists(),'Refuse partial overwrite'
 model.eval();model.config.use_cache=True;records=[];start=time.time()
 for i in range(0,len(rows),4):
  batch=rows[i:i+4];inputs=tok([dsl.prompt(r,names,lib if with_library else None) for r in batch],return_tensors='pt',padding=True).to('cuda')
  with torch.inference_mode():z=model.generate(**inputs,max_new_tokens=512,do_sample=False,pad_token_id=tok.eos_token_id,eos_token_id=tok.eos_token_id)
  tokens=z[:,inputs.input_ids.shape[1]:]
  for row,raw,ids in zip(batch,tok.batch_decode(tokens,skip_special_tokens=True),tokens):
   expected=list(dsl.execute(row['x'],dsl.expand(row['chain'],lib)));pred=dsl.answer(raw);pred=list(pred) if pred is not None else None
   records.append({**row,'raw':raw,'expected':expected,'prediction':pred,'correct':pred==expected,'generated_tokens':int((ids!=tok.eos_token_id).sum()),'max_new_tokens':512,'with_library':with_library})
  if i%96==0:print('EXTENDED',a.model,tag,i,flush=True)
 file.write_text(''.join(json.dumps(r)+'\n' for r in records));result=dict(model=a.model,tag=tag,with_library=with_library,wall_seconds=time.time()-start,records=len(records),sha256=hashlib.sha256(file.read_bytes()).hexdigest());meta.write_text(json.dumps(result,indent=2));return result
result=evaluate(a.tag,a.tag=='frozen-with-library');print('PASS DONE',json.dumps(result),flush=True)
