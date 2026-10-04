"""Independent variable-length binary-string environment. No numeric DSL calls."""
import random,re,json,itertools,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'secondary'

def step(x,op):
 if op=='rev':return x[::-1]
 if op=='rot':return x[1:]+x[:1]
 if op=='inc':return ''.join('b' if c=='a' else 'a' for c in x)
 if op=='neg':return ''.join(('b' if c=='a' else 'a') if i%2==0 else c for i,c in enumerate(x))
 if op=='swap':return x[1]+x[0]+x[2:] if len(x)>1 else x
 if op=='ends':return step(x[:1],'inc')+x[1:-1]+step(x[-1:],'inc') if len(x)>1 else step(x,'inc')
 raise ValueError(op)
def execute(x,ops):
 for op in ops:x=step(x,op)
 return x
def expand(chain,lib):return tuple(o for i in chain for o in lib[i])
def signature(ops):
 # Each length has an affine map over GF(2), identified by zero and basis images.
 return tuple(execute('a'*n,ops)+''.join(execute('a'*j+'b'+'a'*(n-j-1),ops) for j in range(n)) for n in range(3,9))
def prompt(row,names,library=None):
 p='Execute functions left to right on a string of a and b. Show primitive steps and final Answer.\nPrimitives: rev reverses; rot rotates left; inc swaps every a and b; neg swaps a and b at positions 1,3,5,7; swap exchanges first two; ends swaps a and b at both ends.\n'
 if library is not None:p+='Library: '+'; '.join(names[i]+'='+','.join(x) for i,x in enumerate(library))+'\n'
 return p+'Input: '+' '.join(row['x'])+'\nFunctions: '+' '.join(names[i] for i in row['chain'])+'\nTrace:\n'
def target(row,library,condition,names):
 x=row['x'];out=[]
 for i in row['chain']:
  out.append((names[i] if condition=='macro' else 'step')+':')
  for op in library[i]:x=step(x,op);out.append(op+' '+' '.join(x))
 return '\n'.join(out)+'\nAnswer: '+' '.join(x)+'\n'
def answer(text):
 m=re.findall(r'^Answer:[ \t]*([ab](?:[ \t]+[ab]){2,7})[ \t]*$',text,re.M)
 return ''.join(m[-1].split()) if m else None

def build():
 from transformers import AutoTokenizer
 world=json.loads((ROOT.parent/'data/worlds.json').read_text())['original'];lib=world['library'];names=world['names']
 assert len({signature(x) for x in lib})==len(lib)
 (ROOT/'data/worlds.json').write_text(json.dumps({'original':world},indent=2));rng=random.Random(1800);uid=0;used=set()
 chains=[(i,) for i in range(len(lib))]+list(itertools.product(range(len(lib)),repeat=2))
 def row(c,split,pressure=False):
  nonlocal uid
  while True:
   n=rng.choice([7,8] if pressure else [3,4,5,6]);x=''.join(rng.choices('ab',k=n));key=(tuple(c),x)
   if key not in used:used.add(key);break
  uid+=1;return {'id':uid,'x':x,'chain':list(c),'depth':len(c),'split':split}
 train=[row(rng.choice(chains),'train') for _ in range(4096)];iid=[row(rng.choice(chains),'iid') for _ in range(128)];dev=[row(rng.choice(chains),'dev') for _ in range(128)]
 trkeys={signature(expand(c,lib)) for c in chains};seen=set(trkeys);test=iid
 for depth in [3,4,5]:
  count=0
  while count<36:
   c=tuple(rng.randrange(len(lib)) for _ in range(depth));sig=signature(expand(c,lib))
   if sig in seen:continue
   seen.add(sig)
   test.extend(row(c,'ood' if count<32 else 'pressure',count>=32) for _ in range(4));count+=1
 for name,rs in [('train',train),('dev',dev),('test',test)]:
  (ROOT/f'data/{name}.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rs))
 tok=AutoTokenizer.from_pretrained(ROOT/'model',local_files_only=True);length=lambda s:len(tok(s,add_special_tokens=False).input_ids)
 for r in train:assert length(target(r,lib,'macro',names))==length(target(r,lib,'flat',names))
 # Independent exhaustive finite-domain checks against affine reconstruction.
 for ops in lib:
  for n in range(3,9):
   zero=execute('a'*n,ops);basis=[execute('a'*j+'b'+'a'*(n-j-1),ops) for j in range(n)]
   for chars in itertools.product('ab',repeat=n):
    x=''.join(chars);prediction=''
    for k in range(n):
     bit=int(zero[k]=='b')
     for j,c in enumerate(x):
      if c=='b':bit^=(basis[j][k]!=zero[k])
     prediction+='b' if bit else 'a'
    assert prediction==execute(x,ops)
 audit={'train':len(train),'test':len(test),'ood_programs':96,'ood_examples':384,'iid':128,'pressure':48,'train_lengths':[3,4,5,6],'pressure_lengths':[7,8],'token_match':True,'semantic_overlap':0,'verification':'Exhaustive affine reconstruction for every macro over all a/b strings of length 3..8','scope':'Same self-proposed macro structures reinterpreted under independent string primitives; separately trained, not zero-shot cross-domain transfer.'}
 (ROOT/'data/audit.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit,indent=2))

def evaluate(model,tok,rows,world,out,with_library=False,fewshot=False):
 import torch
 model.eval();tok.padding_side='left';results=[];start=time.time();lib=world['library'];names=world['names']
 for ix in range(0,len(rows),32):
  batch=rows[ix:ix+32];ins=tok([prompt(r,names) for r in batch],padding=True,return_tensors='pt').to('cuda')
  with torch.inference_mode():z=model.generate(**ins,max_new_tokens=256,do_sample=False,pad_token_id=tok.pad_token_id,eos_token_id=tok.eos_token_id)
  tokens=z[:,ins.input_ids.shape[1]:];texts=tok.batch_decode(tokens,skip_special_tokens=True)
  for r,txt,ids in zip(batch,texts,tokens):
   ops=expand(r['chain'],lib);expected=execute(r['x'],ops);pred=answer(txt)
   traces=re.findall(r'^(rev|rot|inc|neg|swap|ends)[ \t]+([ab](?:[ \t]+[ab]){2,7})[ \t]*$',txt,re.M)
   state=r['x'];valid=bool(traces)
   for op,values in traces:state=step(state,op);valid=valid and state==''.join(values.split())
   results.append({**r,'raw':txt,'expected':expected,'prediction':pred,'correct':pred==expected,'primitive_sequence_correct':[o for o,v in traces]==list(ops),'execution_steps_correct':valid,'generated_tokens':int((ids!=tok.pad_token_id).sum())})
 out.write_text(''.join(json.dumps(r)+'\n' for r in results))
 groups={}
 for split in sorted({r['split'] for r in results}):
  rs=[r for r in results if r['split']==split];groups[split]={'n':len(rs),'accuracy':sum(r['correct'] for r in rs)/len(rs),'program_accuracy':sum(r['primitive_sequence_correct'] for r in rs)/len(rs),'valid_execution':sum(r['execution_steps_correct'] for r in rs)/len(rs)}
 return {'groups':groups,'elapsed_seconds':time.time()-start,'generated_tokens':sum(r['generated_tokens'] for r in results)}
if __name__=='__main__':build()
