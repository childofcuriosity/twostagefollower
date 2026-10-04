import json,hashlib
from protocol import *
from transformers import AutoTokenizer
out={}
for name in MODELS:
 tok=AutoTokenizer.from_pretrained(MODELS[name],local_files_only=True);rows=read('train');checks=[];counts={m:0 for m in MODES}
 for row in rows:
  es=[encode(row,tok,m) for m in MODES];assert es[0]['ids']==es[1]['ids']==es[2]['ids']
  for m,e in zip(MODES,es):
   for token,label,owner in zip(e['ids'],e['labels'],e['owners']):assert (label==token)==supervised(owner,m)
   counts[m]+=sum(x!=-100 for x in e['labels'])
  # Apart from prompt, two oracle supervision sets partition joint supervision.
  assert all((b!=-100)+(c!=-100)==(a!=-100) for a,b,c in zip(*(e['labels'] for e in es)))
 for row in read('test')+read('independent'):
  state=row['x'];calls=[]
  for tool in row['chain']:
   raw,state=body(tool,state);b=parse_body(raw,calls[-1]['body']['state'] if calls else row['x'],tool);calls.append({'tool':tool,'body':b})
  assert grade(row,calls,'done')['complete']
 # Wrong choice receives correct execution of that wrong tool, never corrected.
 wrong=(rows[0]['chain'][0]+1)%len(LIB);raw,st=body(wrong,rows[0]['x']);assert parse_body(raw,rows[0]['x'],wrong)['correct']
 assert parse_header(NAMES[wrong]+':\n')==wrong
 assert not grade({'chain':[(wrong+1)%len(LIB)],'x':rows[0]['x']},[{'tool':wrong,'body':parse_body(raw,rows[0]['x'],wrong)}],'done')['complete']
 sample={m:encode(rows[0],tok,m) for m in MODES}
 out[name]=dict(training_examples=len(rows),supervised_tokens=counts,sample=sample,source_hash=hashlib.sha256(Path(__file__).with_name('protocol.py').read_bytes()).hexdigest())
 print(name,'mask and reference grading pass',flush=True)
(R/'analysis/preflight.json').write_text(json.dumps(out,indent=2))
