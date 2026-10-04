from pathlib import Path
import sys,json,random,torch,time
from transformers import AutoModelForCausalLM,AutoTokenizer,set_seed
from peft import get_peft_model,LoraConfig
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'src'));import dsl
set_seed(11);torch.set_num_threads(4)
t=AutoTokenizer.from_pretrained(R/'model',local_files_only=True);t.pad_token=t.eos_token
m=AutoModelForCausalLM.from_pretrained(R/'model',torch_dtype=torch.bfloat16,attn_implementation='sdpa',local_files_only=True).cuda()
m=get_peft_model(m,LoraConfig(r=16,lora_alpha=32,lora_dropout=0.,target_modules=['q_proj','k_proj','v_proj','o_proj','gate_proj','up_proj','down_proj'],task_type='CAUSAL_LM'));m.train();m.config.use_cache=False
w=json.loads((R/'data/worlds.json').read_text())['original'];rs=[json.loads(l) for l in (R/'data/train.jsonl').read_text().splitlines()];random.Random(11).shuffle(rs);es=[]
for r in rs[:32]:
 a=t.encode(dsl.prompt(r,w['names']),add_special_tokens=False);b=t.encode(dsl.target(r,w['library'],'flat',w['names']),add_special_tokens=False)+[t.eos_token_id];es.append((a+b,[-100]*len(a)+b))
def batch(items):
 n=max(len(x) for x,y in items);ids=torch.full((len(items),n),t.pad_token_id,device='cuda');labels=torch.full_like(ids,-100);mask=torch.zeros_like(ids)
 for i,(x,y) in enumerate(items):ids[i,:len(x)]=torch.tensor(x,device='cuda');labels[i,:len(y)]=torch.tensor(y,device='cuda');mask[i,:len(x)]=1
 return dict(input_ids=ids,labels=labels,attention_mask=mask)
def run(micro):
 m.zero_grad(set_to_none=True);lossvalue=0
 for start in [0,16]:
  pieces=[batch(es[i:i+micro]) for i in range(start,start+16,micro)];nt=[int((b['labels']!=-100).sum()) for b in pieces]
  for b,n in zip(pieces,nt):
   loss=m(**b).loss*n/sum(nt)/2;lossvalue+=float(loss.detach());loss.backward()
 g=torch.cat([p.grad.float().reshape(-1).cpu() for p in m.parameters() if p.requires_grad]);return lossvalue,g
l0,g0=run(16)
m.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False});m.enable_input_require_grads();l1,g1=run(16)
g0=g0.double();g1=g1.double();cos=float(torch.dot(g0,g1)/(torch.linalg.vector_norm(g0)*torch.linalg.vector_norm(g1)));rel=float(torch.linalg.vector_norm(g0-g1)/torch.linalg.vector_norm(g0));result=dict(original_loss=l0,subdivided_loss=l1,gradient_cosine=cos,gradient_relative_l2=rel,passed=cos>.999 and rel<.03,notes='Actual Qwen1.5B BF16/LoRA first 32 examples; microbatch16 accum2 vs same microbatch16 with gradient checkpointing; no optimizer step')
(R/'scale-study/analysis/checkpointing-check.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True);assert result['passed']
