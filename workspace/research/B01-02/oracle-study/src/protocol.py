"""Shared text protocol; source attribution and grading independent of generation."""
import json,re,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R.parent
sys.path.insert(0,str(P/'src'));import dsl
WORLD=json.loads((P/'data/worlds.json').read_text())['original'];LIB=WORLD['library'];NAMES=WORLD['names'];IDX={n:i for i,n in enumerate(NAMES)}
MODELS={'qwen1.5b':P/'model','qwen3b':P/'rsi-study/models/qwen3b','qwen7b':P/'scale-study/models/qwen7b','qwen32b':P/'scale-study/models/qwen32b'}
MODES=['joint','order_oracle','operation_oracle']
def read(split):
 p=P/'scale-study/qwen32b/data'/f'{split}.jsonl'
 if split=='independent':p=P/'scale-study/extended/qwen32b/macro-s11.jsonl'
 return [{k:v for k,v in json.loads(l).items() if k in ['id','split','x','chain','depth']} for l in p.read_text().splitlines()]
def prompt(row):
 s=dsl.prompt(row,NAMES)
 return s.replace('Show the primitive steps and final Answer.','For each tool, write its name followed by a colon and newline, then the primitive steps. Finish each tool with EndTool on its own line. After all tools, write Done on its own line. Do not write an Answer line.')
def body(tool,state):
 lines=[]
 for op in LIB[tool]:state=dsl.step(state,op);lines.append(op+' '+dsl.digits(state)+'\n')
 return ''.join(lines)+'EndTool\n',state

def fragments(row):
 result=[('prompt',prompt(row))];state=tuple(row['x'])
 for tool in row['chain']:
  result.append(('header',NAMES[tool]+':\n'));b,state=body(tool,state);result.append(('body',b))
 result.append(('finish','Done\n'));return result

def supervised(kind,mode):return kind!='prompt' and (mode=='joint' or (mode=='order_oracle' and kind=='body') or (mode=='operation_oracle' and kind in ['header','finish','eos']))
def encode(row,tok,mode):
 fs=fragments(row);text=''.join(t for _,t in fs);ranges=[];cursor=0
 for kind,t in fs:ranges.append((cursor,cursor+len(t),kind));cursor+=len(t)
 enc=tok(text,add_special_tokens=False,return_offsets_mapping=True);labels=[];owners=[];j=0
 for token,(a,b) in zip(enc['input_ids'],enc['offset_mapping']):
  while a>=ranges[j][1]:j+=1
  assert b<=ranges[j][1],('Token crosses source boundary',tok.decode([token]),(a,b),ranges[j])
  owner=ranges[j][2];owners.append(owner);labels.append(token if supervised(owner,mode) else -100)
 ids=enc['input_ids']+[tok.eos_token_id];owners.append('eos');labels.append(tok.eos_token_id if mode!='order_oracle' else -100)
 assert tok.decode(ids[:-1],clean_up_tokenization_spaces=False)==text
 assert any(x!=-100 for x in labels)
 return dict(ids=ids,labels=labels,owners=owners,text=text)

def parse_header(text):
 if text=='Done\n':return None
 m=re.fullmatch(r'([a-z]+):\n',text)
 if not m or m[1] not in IDX:raise ValueError('Invalid header')
 return IDX[m[1]]
def parse_body(text,start,tool):
 if not text.endswith('EndTool\n'):raise ValueError('Missing EndTool')
 lines=text[:-len('EndTool\n')].splitlines();state=tuple(start);ops=[];numeric=True
 for line in lines:
  m=re.fullmatch(r'(rev|rot|inc|neg|swap|ends) ([0-9]) ([0-9]) ([0-9]) ([0-9])',line)
  if not m:raise ValueError('Invalid primitive line')
  op=m[1];new=tuple(map(int,m.groups()[1:]));numeric &= new==dsl.step(state,op);ops.append(op);state=new
 return dict(state=state,ops=ops,numeric_ok=bool(numeric),ops_ok=ops==LIB[tool],correct=bool(numeric and ops==LIB[tool]))
def grade(row,calls,stop):
 names=[c['tool'] for c in calls];seq=names==row['chain'] and stop in ['done','oracle_done'];allb=bool(calls) and all(c.get('body',{}).get('correct',False) for c in calls)
 final=calls[-1].get('body',{}).get('state') if calls else row['x'];expected=dsl.execute(row['x'],dsl.expand(row['chain'],LIB))
 return dict(sequence_correct=seq,all_expansions_correct=allb,complete=bool(seq and allb and final is not None and tuple(final)==expected),expected=list(expected),final_state=final,requested=len(row['chain']),emitted=len(calls),local_correct=sum(c.get('body',{}).get('correct',False) for c in calls))
