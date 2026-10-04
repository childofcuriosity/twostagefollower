import hashlib,json,random,re,sys
from pathlib import Path

R=Path(__file__).resolve().parents[1]
B=R.parent
MODEL=R/'models/qwen05b'
sys.path.insert(0,str(B/'src'))
import dsl

CONDITIONS=('flat','position','alias','macro')
SEEDS=(11,22,33,*range(100,117))
letters=list('ABCDEFGHI');random.Random(2026092601).shuffle(letters)
ALIASES=['tool'+x for x in letters]
WORLD=json.loads((B/'data/worlds.json').read_text())['original']

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,data):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def target(row,lib,condition,names):
 if condition=='alias':return dsl.target(row,lib,'macro',names)
 if condition!='position':return dsl.target(row,lib,condition,names)
 state=tuple(row['x']);lines=[]
 for i,t in enumerate(row['chain'],1):
  lines.append(f'step{i}:')
  for op in lib[t]:
   state=dsl.step(state,op);lines.append(op+' '+dsl.digits(state))
 return '\n'.join(lines)+'\nAnswer: '+dsl.digits(state)+'\n'

def snapshot():
 src=(B/'src/run.py').read_text()
 return src.replace("choices=['flat','macro','natural','shuffled','frozen']","choices=['flat','macro','natural','shuffled','frozen','position','alias']")
