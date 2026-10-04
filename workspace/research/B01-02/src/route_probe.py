"""Post-hoc failure diagnosis. External routing; never a replacement OOD score."""
import argparse,json,time,os
from pathlib import Path
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM,set_seed
from peft import PeftModel
from dsl import prompt,answer,execute,expand
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--condition',choices=['flat','macro','frozen'],required=True);ap.add_argument('--seed',type=int,default=11);args=ap.parse_args()
set_seed(args.seed);torch.set_num_threads(4);t0=time.time()
world=json.loads((ROOT/'data/worlds.json').read_text())['original'];seen=set();rows=[]
for r in [json.loads(s) for s in (ROOT/'data/test.jsonl').read_text().splitlines()]:
 if r['split']=='ood' and tuple(r['chain']) not in seen:seen.add(tuple(r['chain']));rows.append(r)
tok=AutoTokenizer.from_pretrained(ROOT/'model',local_files_only=True);tok.pad_token=tok.eos_token;tok.padding_side='left'
model=AutoModelForCausalLM.from_pretrained(ROOT/'model',torch_dtype=torch.bfloat16,attn_implementation='sdpa',local_files_only=True).cuda()
if args.condition!='frozen':model=PeftModel.from_pretrained(model,ROOT/f'runs/{args.condition}-original-s{args.seed}/adapter')
model.eval();states=[tuple(r['x']) for r in rows];calls=[[] for r in rows]
for j in range(5):
 indices=[i for i,r in enumerate(rows) if len(r['chain'])>j and states[i] is not None]
 for offset in range(0,len(indices),32):
  ids=indices[offset:offset+32]
  queries=[{**rows[i],'x':states[i],'chain':[rows[i]['chain'][j]]} for i in ids]
  ins=tok([prompt(q,world['names']) for q in queries],return_tensors='pt',padding=True).to('cuda')
  with torch.inference_mode():z=model.generate(**ins,max_new_tokens=96,do_sample=False,pad_token_id=tok.pad_token_id,eos_token_id=tok.eos_token_id)
  texts=tok.batch_decode(z[:,ins.input_ids.shape[1]:],skip_special_tokens=True)
  for i,q,txt in zip(ids,queries,texts):
   pred=answer(txt);calls[i].append({'position':j,'input':q['x'],'macro_index':q['chain'][0],'raw':txt,'prediction':pred});states[i]=pred
results=[]
for r,state,history in zip(rows,states,calls):
 expected=execute(r['x'],expand(r['chain'],world['library']))
 results.append({**r,'calls':history,'prediction':state,'expected':expected,'correct':state==expected})
out=ROOT/'analysis/routing-probe';out.mkdir(exist_ok=True)
name=f'{args.condition}-s{args.seed}'
(out/f'{name}.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in results))
summary={'condition':args.condition,'seed':args.seed,'n_unique_programs':len(results),'correct':sum(r['correct'] for r in results),'accuracy':sum(r['correct'] for r in results)/len(results),'calls':sum(len(r['calls']) for r in results),'wall_seconds':time.time()-t0,'interpretation':'External Python loop routes each macro. Intermediate states come only from model outputs, not oracle. No function definitions supplied. Different inference scaffold and cost; do not substitute for autonomous OOD result.'}
(out/f'{name}-summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))
