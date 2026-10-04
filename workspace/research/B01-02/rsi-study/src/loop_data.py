from common import *
import secondary

def engine(domain):return dsl if domain=='digits' else secondary

def inp(x):return ' '.join(map(str,x))
def prompt(row,domain):
 rules='rev reverses; rot rotates left; inc adds 1 mod 10 to all; neg negates mod 10; swap swaps first two; ends adds 1 mod 10 to both ends.' if domain=='digits' else 'rev reverses; rot rotates left; inc flips all a/b; neg flips positions 1,3,5,7; swap swaps first two; ends flips first and last.'
 return 'Execute the program from left to right. Show each primitive and its resulting state, then Answer.\nPrimitives: '+rules+'\nInput: '+inp(row['x'])+'\nProgram: '+','.join(row['ops'])+'\nTrace:\n'
def target(row,domain):
 state=row['x'];lines=[]
 for op in row['ops']:state=engine(domain).step(state,op);lines.append(op+' '+inp(state))
 return '\n'.join(lines)+'\nAnswer: '+inp(state)+'\n'
def answer(text,domain):
 pattern=r'^Answer:[ \t]*([0-9](?:[ \t]+[0-9]){3})[ \t]*$' if domain=='digits' else r'^Answer:[ \t]*([ab](?:[ \t]+[ab]){2,7})[ \t]*$'
 matches=re.findall(pattern,text,re.M)
 if not matches:return None
 return list(map(int,matches[-1].split())) if domain=='digits' else ''.join(matches[-1].split())
def random_input(rng,domain,long=False):return [rng.randrange(10) for _ in range(4)] if domain=='digits' else ''.join(rng.choices('ab',k=rng.choice([7,8] if long else [3,4,5,6])))
def build_eval():
 families=load();rng=random.Random(932016)
 for domain in ['digits','strings']:
  rows=[]
  for i in range(64):rows.append(dict(id=i,split='short',family=-1,x=random_input(rng,domain),ops=rng.choices(OPS,k=rng.choice([2,3,4]))))
  for f in families:
   if f['split']!='test':continue
   for j in range(8):rows.append(dict(id=len(rows),split='family',family=f['id'],x=random_input(rng,domain),ops=f['test'][j]))
   for j in range(8,12):rows.append(dict(id=len(rows),split='pressure',family=f['id'],x=random_input(rng,domain,True),ops=f['test'][j]))
  (ROOT/f'data/loop-eval-{domain}.json').write_text(json.dumps(rows,indent=2))
def training_data(libraries,seed,domain,n=2048):
 rng=random.Random(seed);evalrows=json.loads((ROOT/f'data/loop-eval-{domain}.json').read_text());testsignatures={engine(domain).signature(tuple(r['ops'])) for r in evalrows};rows=[]
 for attempt in range(n*1000):
  fid=rng.randrange(12);lib=libraries[str(fid)];ops=[]
  for _ in range(rng.choice([2,3])):ops.extend(CANDIDATES[rng.choice(lib)] if lib and rng.random()<.8 else [rng.choice(OPS)])
  if engine(domain).signature(tuple(ops)) in testsignatures:continue
  row=dict(id=len(rows),family=fid,x=random_input(rng,domain),ops=ops);rows.append(row)
  if len(rows)==n:break
 assert len(rows)==n,(domain,len(rows))
 return rows
if __name__=='__main__':build_eval()
