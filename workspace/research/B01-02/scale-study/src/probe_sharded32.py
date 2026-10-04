from pathlib import Path
import json,time,sys,socket
import torch
from transformers import AutoModelForCausalLM,AutoTokenizer
from peft import PeftModel
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'src'));import dsl
torch.set_num_threads(4)
root=R/'qwen32b';world=json.loads((root/'data/worlds.json').read_text())['original']
tok=AutoTokenizer.from_pretrained(root/'model',local_files_only=True);tok.pad_token=tok.eos_token;tok.padding_side='left'
model=AutoModelForCausalLM.from_pretrained(root/'model',local_files_only=True,torch_dtype=torch.bfloat16,attn_implementation='sdpa',low_cpu_mem_usage=True,device_map='balanced',max_memory={i:28*1024**3 for i in range(4)})
mapping={k:str(v) for k,v in model.hf_device_map.items()};assert not {'cpu','disk'}.intersection(mapping.values())
model=PeftModel.from_pretrained(model,root/'runs/flat-original-s11/checkpoints/step0000/adapter');model.eval();model.config.use_cache=True
reference=list(map(json.loads,(root/'runs/flat-original-s11/step0000-dev.jsonl').read_text().splitlines()))
selected=reference[:4]+reference[128:132];records=[];start=time.time()
for i in [0,4]:
 batch=selected[i:i+4];ins=tok([dsl.prompt(x,world['names']) for x in batch],return_tensors='pt',padding=True).to('cuda:0')
 with torch.inference_mode():z=model.generate(**ins,max_new_tokens=256,do_sample=False,pad_token_id=tok.eos_token_id,eos_token_id=tok.eos_token_id)
 tokens=z[:,ins.input_ids.shape[1]:]
 for row,txt,ids in zip(batch,tok.batch_decode(tokens,skip_special_tokens=True),tokens):records.append(dict(id=row['id'],raw=txt,reference_raw=row['raw'],exact_match=txt==row['raw'],generated_tokens=int((ids!=tok.eos_token_id).sum())))
 print('PROBE BATCH',i,flush=True)
for i in range(4):torch.cuda.synchronize(i)
elapsed=time.time()-start
result=dict(hostname=socket.gethostname(),gpu=torch.cuda.get_device_name(),device_map=mapping,seconds=elapsed,records=records,exact_matches=sum(x['exact_match'] for x in records),tokens_per_second=sum(x['generated_tokens'] for x in records)/elapsed,peak_memory_bytes=[torch.cuda.max_memory_allocated(i) for i in range(4)],passed=all(x['exact_match'] for x in records),scope='Eight dev outputs, same batch4, BF16, max256 and greedy decoder. Smoke comparison only, not global bitwise equivalence.')
(R/'analysis/sharded32-probe.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ['records','device_map']}),flush=True)
