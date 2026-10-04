import hashlib,json,random,re
from pathlib import Path
import frozen_dsl as dsl
R=Path(__file__).resolve().parents[1]
B=R.parent.parent
MODEL=R.parent/'models/qwen14b'
WORLD=json.loads((B/'data/worlds.json').read_text())['original']
LIB=WORLD['library']; NAMES=WORLD['names']
letters=list('ABCDEFGHI');random.Random(2026092601).shuffle(letters)
ALIASES=['tool'+x for x in letters]
CONDITIONS=('STEP','POSITION','ALIAS','NAME')
EXAMPLE=dict(id='example',chain=[0,1],x=[9,0,4,7],split='example',depth=2)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def readrows(p):return [json.loads(s) for s in Path(p).read_text().splitlines()]
def saverows(p,rows):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(''.join(json.dumps(x)+'\n' for x in rows))
def names(c):return ALIASES if c=='ALIAS' else NAMES
def labels(row,c):return ['step' if c=='STEP' else f'step{k}' if c=='POSITION' else names(c)[t] for k,t in enumerate(row['chain'],1)]
def target(row,c):
 state=tuple(row['x']);lines=[]
 for t,h in zip(row['chain'],labels(row,c)):
  lines.append(h+':')
  for op in LIB[t]:
   state=dsl.step(state,op);lines.append(op+' '+dsl.digits(state))
 return '\n'.join(lines)+'\nAnswer: '+dsl.digits(state)+'\n'
RULES={
 'STEP':'Before each tool call, write the heading step: on its own line.',
 'POSITION':'Before each tool call, write the heading step1:, step2:, and so on, using its 1-based position in the plan, on its own line.',
 'ALIAS':'Before each tool call, write the current tool name followed by a colon on its own line.',
 'NAME':'Before each tool call, write the current tool name followed by a colon on its own line.'}
def task(row,c):return 'Input: '+dsl.digits(row['x'])+'\nFunctions: '+' '.join(names(c)[t] for t in row['chain'])+'\nTrace:\n'
def template(c):
 return ('Execute the given tool calls from left to right on a state of four digits. Each tool applies its listed primitive operations in order. Carry the resulting state into the next operation and tool.\n'
 'Primitive definitions for state a b c d:\n'
 'rev: d c b a\nrot: b c d a\ninc: (a+1) mod 10, (b+1) mod 10, (c+1) mod 10, (d+1) mod 10\n'
 'neg: (-a) mod 10, (-b) mod 10, (-c) mod 10, (-d) mod 10 (0 maps to 0)\n'
 'swap: b a c d\nends: (a+1) mod 10, b, c, (d+1) mod 10\n'
 'Tool definitions:\n'+'\n'.join(f'{names(c)[i]}: '+', '.join(ops) for i,ops in enumerate(LIB))+'\n'
 'Output requirements:\n'+RULES[c]+'\n'
 'Under each heading, output every primitive operation of that tool and the state AFTER that operation, one line per operation, in the format: operation digit digit digit digit.\n'
 'After all calls, output exactly one final line: Answer: digit digit digit digit\n'
 'Use single spaces between digits. Output only the trace and final Answer, with no explanation, code fences, or extra lines.\n'
 'Format example:\n'+task(EXAMPLE,c)+target(EXAMPLE,c)+'\nNow execute this plan:\n{task}')
def prompt(row,c):return template(c).replace('{task}',task(row,c))
def key(row):return (tuple(row['chain']),tuple(row['x']))
def generate(phase,L,n):
 p=R/f'data/{phase}-L{L}.jsonl'
 if p.exists():
  rows=readrows(p);assert len(rows)==n;return rows
 used={key(EXAMPLE)}
 for path in (R/'data').glob('*.jsonl'):used.update(key(x) for x in readrows(path))
 seed={'precheck':610000,'explore':620000,'formal':630000}[phase]+L
 rng=random.Random(seed);rows=[]
 while len(rows)<n:
  row=dict(id=f'{phase}-L{L}-{len(rows):04d}',split=phase,depth=L,chain=[rng.randrange(9) for _ in range(L)],x=[rng.randrange(10) for _ in range(4)])
  if key(row) in used:continue
  used.add(key(row));rows.append(row)
 saverows(p,rows);return rows
