import json,sys,random,hashlib,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];B=R.parent;S=B/'scale-study'
sys.path.insert(0,str(B/'src'));import dsl
ROOTS={'qwen1.5b':B,'qwen3b':B/'rsi-study/replications/qwen3b','qwen7b':S/'qwen7b','qwen32b':S/'qwen32b'}
WORLD=json.loads((B/'data/worlds.json').read_text())['original']
a=list('ABCDEFGHI');random.Random(2026092601).shuffle(a)
ALIASES=['tool'+x for x in a]
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def target(row,lib,condition,names):
 if condition=='alias':return dsl.target(row,lib,'macro',names)
 if condition!='position':return dsl.target(row,lib,condition,names)
 state=tuple(row['x']);lines=[]
 for k,t in enumerate(row['chain'],1):
  lines.append(f'step{k}:')
  for op in lib[t]:state=dsl.step(state,op);lines.append(op+' '+dsl.digits(state))
 return '\n'.join(lines)+'\nAnswer: '+dsl.digits(state)+'\n'
def source(model):return B/'src/run.py' if model in ['qwen1.5b','qwen3b'] else S/'src/train.py'
def code(model):
 # Only parser allow-list and output-root selection change. Training body remains byte-for-byte.
 s=source(model).read_text()
 s=s.replace("choices=['flat','macro','natural','shuffled','frozen']","choices=['flat','macro','natural','shuffled','frozen','position','alias']")
 if model in ['qwen7b','qwen32b']:s=s.replace(' ROOT=ROOT/args.model\n',' # ROOT supplied by isolated wrapper\n')
 return s
