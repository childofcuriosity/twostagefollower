from common import *
import argparse,math,time
from transformers import AutoTokenizer,AutoConfig
p=argparse.ArgumentParser();p.add_argument('--phase',required=True,choices=['precheck','explore','formal']);p.add_argument('--lengths',nargs='+',type=int,required=True);a=p.parse_args()
tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True);cfg=AutoConfig.from_pretrained(MODEL,local_files_only=True)
for c in CONDITIONS:
 path=R/f'prompts/{c}.txt';content=template(c)
 if path.exists():assert path.read_text()==content
 else:path.write_text(content)
for L in a.lengths:
 rows=generate(a.phase,L,{'precheck':4,'explore':32,'formal':512}[a.phase]);limits={}
 for c in CONDITIONS:
  nt=[len(tok(target(x,c),add_special_tokens=False).input_ids)+1 for x in rows]
  ni=[len(tok.apply_chat_template([dict(role='user',content=prompt(x,c))],tokenize=True,add_generation_prompt=True)) for x in rows]
  limits[c]=dict(max_target=max(nt),max_input=max(ni),mean_target=sum(nt)/len(nt))
 cap=math.ceil((1.25*max(v['max_target'] for v in limits.values())+64)/256)*256
 assert max(v['max_input'] for v in limits.values())+cap<=cfg.max_position_embeddings
 manifest=dict(phase=a.phase,length=L,n=len(rows),seed={'precheck':610000,'explore':620000,'formal':630000}[a.phase]+L,limits=limits,max_new_tokens=cap,context=cfg.max_position_embeddings,data_sha256=sha(R/f'data/{a.phase}-L{L}.jsonl'),model=json.loads((MODEL/'download-manifest.json').read_text()),prompts={c:sha(R/f'prompts/{c}.txt') for c in CONDITIONS},source={f.name:sha(f) for f in (R/'src').glob('*.py')},decode=dict(do_sample=False,num_beams=1,dtype='bfloat16',attention='sdpa',use_cache=True,chat='single user, official template, add_generation_prompt=True'),created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
 path=R/f'data/{a.phase}-L{L}-manifest.json'
 if path.exists():
  old=json.loads(path.read_text());assert old['data_sha256']==manifest['data_sha256'] and old['max_new_tokens']==cap
 else:write(path,manifest)
 print(a.phase,L,len(rows),cap,flush=True)
