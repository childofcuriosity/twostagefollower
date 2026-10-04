import argparse,json,time,os,subprocess,sys,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R.parent
ap=argparse.ArgumentParser();ap.add_argument('--model',choices=['qwen1.5b','qwen3b','qwen7b','qwen32b'],required=True);a=ap.parse_args()
if a.model in ['qwen7b','qwen32b']:
 marker=R/f'analysis/{a.model}-completed.json'
 while not marker.exists():time.sleep(60)
 records=json.loads(marker.read_text());assert len(records)==6 and all(r['returncode']==0 for r in records)
import torch
from transformers import AutoModelForCausalLM,AutoTokenizer
from peft import PeftModel
sys.path.insert(0,str(P/'src'));import dsl
torch.set_num_threads(4)
roots={'qwen1.5b':P,'qwen3b':P/'rsi-study/replications/qwen3b','qwen7b':R/'qwen7b','qwen32b':R/'qwen32b'};root=roots[a.model]
world=json.loads((P/'data/worlds.json').read_text())['original'];lib=world['library'];names=world['names']
rows=[json.loads(l) for l in (R/'data/extended-test.jsonl').read_text().splitlines()];out=R/'extended'/a.model;out.mkdir(parents=True,exist_ok=True)
tok=AutoTokenizer.from_pretrained(root/'model',local_files_only=True);tok.pad_token=tok.eos_token;tok.padding_side='left'
model=AutoModelForCausalLM.from_pretrained(root/'model',torch_dtype=torch.bfloat16,attn_implementation='sdpa',local_files_only=True,low_cpu_mem_usage=True).cuda()
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
results=[evaluate('frozen-with-library',True)]
for seed in [11,22,33]:
 for condition in ['flat','macro']:
  tag=f'{condition}-s{seed}';path=root/f'runs/{condition}-original-s{seed}/adapter'
  if not isinstance(model,PeftModel):model=PeftModel.from_pretrained(model,path,adapter_name=tag)
  else:model.load_adapter(path,adapter_name=tag)
  model.set_adapter(tag);results.append(evaluate(tag,False))
(out/'completed.json').write_text(json.dumps(results,indent=2));print('EXTENDED DONE',a.model,flush=True)
