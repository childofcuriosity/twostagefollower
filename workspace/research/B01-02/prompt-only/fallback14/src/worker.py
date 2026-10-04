from common import *
import argparse,os,time,traceback
import torch
from transformers import AutoModelForCausalLM,AutoTokenizer,GenerationConfig
p=argparse.ArgumentParser();p.add_argument('--phase',required=True);p.add_argument('--lengths',nargs='+',type=int,required=True);p.add_argument('--conditions',nargs='+',default=list(CONDITIONS));p.add_argument('--batch',type=int,default=16);p.add_argument('--shard',type=int,default=0);p.add_argument('--shards',type=int,default=1);a=p.parse_args()
torch.manual_seed(810001);torch.set_num_threads(4)
start=time.time();tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True,padding_side='left')
model=AutoModelForCausalLM.from_pretrained(MODEL,local_files_only=True,torch_dtype=torch.bfloat16,attn_implementation='sdpa').to('cuda').eval()
load_seconds=time.time()-start
eos=model.generation_config.eos_token_id;eos=[eos] if isinstance(eos,int) else eos
pad=tok.pad_token_id
for L in a.lengths:
 rows=readrows(R/f'data/{a.phase}-L{L}.jsonl');manifest=json.loads((R/f'data/{a.phase}-L{L}-manifest.json').read_text());cap=manifest['max_new_tokens'];rows=rows[a.shard::a.shards]
 assert sha(R/f'data/{a.phase}-L{L}.jsonl')==manifest['data_sha256']
 for c in a.conditions:
  out=R/f'runs/{a.phase}-L{L}-{c}';out=out/f'shard-{a.shard}-of-{a.shards}' if a.shards>1 else out;out.mkdir(parents=True,exist_ok=True)
  if (out/'complete.json').exists():continue
  for cc in CONDITIONS:
   assert sha(R/f'prompts/{cc}.txt')==manifest['prompts'][cc]
   assert template(cc)==(R/f'prompts/{cc}.txt').read_text()
  done=readrows(out/'predictions.jsonl') if (out/'predictions.jsonl').exists() else []
  assert [x['id'] for x in done]==[x['id'] for x in rows[:len(done)]]
  begin=time.time();gen_seconds=0;batch=a.batch
  write(out/'running.json',dict(pid=os.getpid(),gpu=os.environ.get('CUDA_VISIBLE_DEVICES'),start=begin,batch=batch,model_load_seconds=load_seconds,manifest_sha256=sha(R/f'data/{a.phase}-L{L}-manifest.json')))
  offset=len(done)
  with (out/'predictions.jsonl').open('a',buffering=1) as f:
   while offset<len(rows):
    chunk=rows[offset:offset+batch]
    texts=[tok.apply_chat_template([dict(role='user',content=prompt(x,c))],tokenize=False,add_generation_prompt=True) for x in chunk]
    enc=tok(texts,return_tensors='pt',padding=True,add_special_tokens=False).to('cuda')
    config=GenerationConfig(do_sample=False,num_beams=1,max_new_tokens=cap,eos_token_id=eos,pad_token_id=pad,bos_token_id=tok.bos_token_id,use_cache=True)
    if not (out/'generation-config.json').exists():write(out/'generation-config.json',config.to_dict())
    try:
     torch.cuda.synchronize();t=time.time()
     with torch.inference_mode():output=model.generate(**enc,generation_config=config)
     torch.cuda.synchronize();elapsed=time.time()-t
    except torch.cuda.OutOfMemoryError:
     with (out/'failures.jsonl').open('a') as ff:ff.write(json.dumps(dict(offset=offset,batch=batch,type='OOM',traceback=traceback.format_exc(),time=time.time()))+'\n')
     del enc;torch.cuda.empty_cache()
     if batch==1:raise
     batch=max(1,batch//2);continue
    gen_seconds+=elapsed
    for row,seq,mask in zip(chunk,output[:,enc.input_ids.shape[1]:].tolist(),enc.attention_mask):
     stop=next((j for j,x in enumerate(seq) if x in eos),None)
     ids=seq[:stop+1] if stop is not None else seq
     raw=tok.decode(ids,skip_special_tokens=True)
     record=dict(row,condition=c,raw=raw,expected=list(dsl.execute(row['x'],dsl.expand(row['chain'],LIB))),input_tokens=int(mask.sum()),output_token_ids=ids,generated_tokens=len(ids),text_tokens=len(ids)-(stop is not None),finish_reason='eos' if stop is not None else 'length',max_new_tokens=cap,batch_size=len(chunk),batch_generate_seconds=elapsed,allocated_generate_seconds=elapsed/len(chunk))
     f.write(json.dumps(record)+'\n')
    offset+=len(chunk);print(json.dumps(dict(phase=a.phase,length=L,condition=c,done=offset,total=len(rows),batch_seconds=elapsed)),flush=True)
    del enc,output
  predictions=readrows(out/'predictions.jsonl');assert len(predictions)==len(rows)
  write(out/'complete.json',dict(n=len(rows),condition=c,length=L,phase=a.phase,model_load_seconds=load_seconds,wall_seconds=time.time()-begin,generate_seconds_all_records=sum(x['allocated_generate_seconds'] for x in predictions),generate_seconds_this_process=gen_seconds,continued_records=len(done),prediction_sha256=sha(out/'predictions.jsonl'),finished=time.time(),max_gpu_memory_bytes=torch.cuda.max_memory_allocated()))
print('ALL_DONE',flush=True)
