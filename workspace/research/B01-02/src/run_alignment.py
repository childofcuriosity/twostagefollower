"""Post-hoc paired alignment control. Keeps original experiment untouched."""
import argparse,sys,random,json
from pathlib import Path
from transformers import AutoTokenizer
import run as runner
import dsl
ap=argparse.ArgumentParser(add_help=False);ap.add_argument('--alignment',choices=['stable','call'],required=True);args,rest=ap.parse_known_args()
tok=AutoTokenizer.from_pretrained(runner.ROOT/'model',local_files_only=True)
size=lambda x:len(tok(x,add_special_tokens=False).input_ids)
world=json.loads((runner.ROOT/'data/worlds.json').read_text())['original']
POOL=[x for x in ['cat','dog','bird','fish','sun','moon','rain','snow','wind','fire','book','tree'] if size('\n'+x+':')==size('\nstep:')]
assert len(POOL)>=6

def tags(row):
 return random.Random(120000+row['id']).sample(POOL,len(row['chain']))
def tagged_prompt(row,names=dsl.NAMES,library=None):
 p=dsl.prompt(row,names,library)
 return p.replace('\nTrace:\n','\nCall tags: '+' '.join(tags(row))+'\nTrace:\n')
def tagged_target(row,library,condition,names=dsl.NAMES):
 base=dsl.target(row,library,'macro',names)
 if args.alignment=='stable':return base
 out=[];j=0;ts=tags(row)
 for line in base.splitlines():
  if line.endswith(':') and line[:-1] in names:
   out.append(ts[j]+':');j+=1
  else:out.append(line)
 assert j==len(row['chain'])
 return '\n'.join(out)+'\n'
# Same prompt, same expanded program and states, same active target tokens.
for row in runner.read('train'):
 assert size(tagged_target(row,world['library'],'macro',world['names']))==size(dsl.target(row,world['library'],'macro',world['names']))
runner.prompt=tagged_prompt;runner.target=tagged_target
sys.argv=[sys.argv[0]]+rest+['--tag=-tagged-'+args.alignment]
runner.main()
