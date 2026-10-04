"""Closed, total affine DSL. No eval/exec of generated model text."""
import re
OPS=('rev','rot','inc','neg','swap','ends')
WORDS={'rev':'reverse','rot':'rotate left','inc':'add one modulo ten','neg':'negate modulo ten','swap':'swap first two','ends':'increment both ends modulo ten'}
NAMES=['red','blue','green','gold','pink','black','white','gray','brown','orange','silver','purple','yellow','violet','amber','coral','ivory','lime','navy','olive','cat','dog','bird','fish','sun','moon','rain','snow','wind','fire']
def step(x,op):
 x=tuple(x)
 if op=='rev':return x[::-1]
 if op=='rot':return x[1:]+x[:1]
 if op=='inc':return tuple((a+1)%10 for a in x)
 if op=='neg':return tuple((-a)%10 for a in x)
 if op=='swap':return (x[1],x[0],x[2],x[3])
 if op=='ends':return ((x[0]+1)%10,x[1],x[2],(x[3]+1)%10)
 raise ValueError(op)
def execute(x,ops):
 for op in ops:x=step(x,op)
 return tuple(x)
def signature(ops):
 # All six primitives are affine on Z_10^4. Images of zero and basis
 # exactly determine the affine map; not a sampled equivalence heuristic.
 z=execute((0,0,0,0),ops)
 return (z,)+tuple(tuple((a-b)%10 for a,b in zip(execute(tuple(int(i==j) for i in range(4)),ops),z)) for j in range(4))
def parse(text):
 line=text.strip().split('\n')[0].strip(' []`\"\' .')
 parts=[p.strip(' \"\'') for p in re.split(r'[,; ]+',line) if p]
 return tuple(parts) if 1<=len(parts)<=8 and all(p in OPS for p in parts) else None
def digits(x):return ' '.join(map(str,x))
def expand(chain,library):return tuple(op for i in chain for op in library[i])
def prompt(row,names=NAMES,library=None):
 header='Execute functions from left to right on four digits. Show the primitive steps and final Answer.\n'
 header+='Primitives: rev reverses; rot rotates left; inc adds 1 mod 10 to all; neg negates mod 10; swap swaps first two; ends adds 1 mod 10 to first and last.\n'
 if library is not None:
  header+='Library: '+ '; '.join(f'{names[i]}='+','.join(ops) for i,ops in enumerate(library))+'\n'
 return header+'Input: '+digits(row['x'])+'\nFunctions: '+ ' '.join(names[i] for i in row['chain'])+'\nTrace:\n'
def target(row,library,condition,names=NAMES):
 x=tuple(row['x']);lines=[]
 import random
 rng=random.Random(row['id'])
 for i in row['chain']:
  if condition=='macro':label=names[i]
  elif condition=='flat':label='step'
  elif condition=='shuffled':label=rng.choice(names[:len(library)])
  elif condition=='natural':label=' then '.join(WORDS[o] for o in library[i])
  else:raise ValueError(condition)
  lines.append(label+':')
  for op in library[i]:
   x=step(x,op);lines.append(op+' '+digits(x))
 return '\n'.join(lines)+'\nAnswer: '+digits(x)+'\n'
def answer(text):
 matches=re.findall(r'Answer:\s*([0-9])\s+([0-9])\s+([0-9])\s+([0-9])',text)
 return tuple(map(int,matches[-1])) if matches else None
if __name__=='__main__':
 import itertools,random,json
 assert step((1,2,3,4),'rev')==(4,3,2,1)
 assert step((9,2,3,9),'ends')==(0,2,3,0)
 assert step((1,2,3,4),'neg')==(9,8,7,6)
 assert execute((1,2,3,4),('rot',)*4)==(1,2,3,4)
 assert signature(('rev','rev'))==signature(())
 assert signature(('inc','neg'))!=signature(('neg','inc'))
 assert parse('__import__("os")') is None
 rng=random.Random(14)
 for _ in range(100):
  ops=tuple(rng.choices(OPS,k=5));s=signature(ops)
  for _ in range(100):
   x=tuple(rng.randrange(10) for _ in range(4))
   predicted=tuple((s[0][j]+sum(s[i+1][j]*x[i] for i in range(4)))%10 for j in range(4))
   assert execute(x,ops)==predicted
 print(json.dumps({'hand_tests':'pass','affine_signature_checks':10000,'unsafe_parse':'rejected'}))
