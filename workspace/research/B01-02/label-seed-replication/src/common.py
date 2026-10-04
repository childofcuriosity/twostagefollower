import hashlib,json,random,re,sys
from pathlib import Path

R=Path(__file__).resolve().parents[1]
B=R.parent
S=B/'scale-study'
L=B/'label-controls'
sys.path.insert(0,str(B/'src'))
import dsl

ROOTS={'qwen1.5b':B,'qwen3b':B/'rsi-study/replications/qwen3b','qwen7b':S/'qwen7b'}
WORLD=json.loads((B/'data/worlds.json').read_text())['original']
letters=list('ABCDEFGHI');random.Random(2026092601).shuffle(letters)
ALIASES=['tool'+x for x in letters]
CONDITIONS=['flat','position','alias','macro']
SEEDS=list(range(100,117))

def write(path,value):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def source(model):return B/'src/run.py' if model in ('qwen1.5b','qwen3b') else S/'src/train.py'

def target(row,library,condition,names):
 if condition=='alias':return dsl.target(row,library,'macro',names)
 if condition!='position':return dsl.target(row,library,condition,names)
 state=tuple(row['x']);lines=[]
 for position,tool in enumerate(row['chain'],1):
  lines.append(f'step{position}:')
  for op in library[tool]:
   state=dsl.step(state,op);lines.append(op+' '+dsl.digits(state))
 return '\n'.join(lines)+'\nAnswer: '+dsl.digits(state)+'\n'

def driver(model):
 s=source(model).read_text()
 s=s.replace("choices=['flat','macro','natural','shuffled','frozen']","choices=['flat','macro','natural','shuffled','frozen','position','alias']")
 if model=='qwen7b':s=s.replace(' ROOT=ROOT/args.model\n',' # isolated output root supplied by wrapper\n')
 return s
