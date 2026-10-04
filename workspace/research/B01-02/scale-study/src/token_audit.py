from pathlib import Path
import sys,json,argparse
from transformers import AutoTokenizer
R=Path(__file__).resolve().parents[1];P=R.parent;sys.path.insert(0,str(P/'src'));import dsl
ap=argparse.ArgumentParser();ap.add_argument('--model',choices=['qwen7b','qwen32b'],required=True);a=ap.parse_args()
t=AutoTokenizer.from_pretrained(R/'models'/a.model,local_files_only=True);old=AutoTokenizer.from_pretrained(P/'model',local_files_only=True)
rs=[json.loads(l) for l in (P/'data/train.jsonl').read_text().splitlines()];w=json.loads((P/'data/worlds.json').read_text())['original'];totals={'input':0,'flat_target':0,'macro_target':0};same=True
for row in rs:
 p=dsl.prompt(row,w['names']);x=dsl.target(row,w['library'],'flat',w['names']);y=dsl.target(row,w['library'],'macro',w['names'])
 ids=t.encode(p,add_special_tokens=False);tx=t.encode(x,add_special_tokens=False);ty=t.encode(y,add_special_tokens=False);assert len(tx)==len(ty)
 same &= ids==old.encode(p,add_special_tokens=False) and tx==old.encode(x,add_special_tokens=False) and ty==old.encode(y,add_special_tokens=False)
 totals['input']+=len(ids);totals['flat_target']+=len(tx)+1;totals['macro_target']+=len(ty)+1
result={'model':a.model,'rows':len(rs),'flat_macro_target_tokens_equal_each_row':True,'training_token_ids_identical_to_original_qwen1.5b':same,'one_pass_tokens':totals}
(R/f'analysis/{a.model}-token-audit.json').write_text(json.dumps(result,indent=2));print(result)
