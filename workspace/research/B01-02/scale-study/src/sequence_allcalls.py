"""Whole-trajectory A=name sequence, B=all emitted calls correctly expanded."""
import json,collections,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=R/'analysis/subtask-factorization-segments.jsonl';rows=[json.loads(l) for l in p.read_text().splitlines()]
out=[]
for family,model,L in sorted({(r['family'],r['model'],r['length']) for r in rows}):
 rs=[r for r in rows if (r['family'],r['model'],r['length'])==(family,model,L)];n=len(rs)
 a=sum(r['name_sequence_ok'] for r in rs);b=sum(r['all_named_expansions_ok'] for r in rs);ab=sum(r['name_sequence_ok'] and r['all_named_expansions_ok'] for r in rs);actual=sum(r['strict'] for r in rs)
 assert ab==actual,(family,model,L,ab,actual)
 seeds=[]
 for seed in [11,22,33]:
  ss=[r for r in rs if r['seed']==seed];pa=sum(r['name_sequence_ok'] for r in ss)/len(ss);pb=sum(r['all_named_expansions_ok'] for r in ss)/len(ss)
  seeds.append({'seed':seed,'A':pa,'B':pb,'product':pa*pb,'actual':sum(r['strict'] for r in ss)/len(ss)})
 out.append(dict(family=family,model=model,length=L,n=n,A_correct=a,B_correct=b,both_correct=ab,A=a/n,B=b/n,pooled_product=a*b/n**2,seed_matched_product=sum(s['product'] for s in seeds)/3,actual=actual/n,B_given_A=ab/a if a else None,B_given_not_A=(b-ab)/(n-a) if n>a else None,empty=sum(not r['segments'] for r in rs),seeds=seeds))
obj={'definition':'Per trajectory A: full emitted name list equals requested name list. B: at least one emitted macro and EVERY emitted macro completely/correctly expands its actual legal name, including local numeric transitions. Missing calls fail A but are not imaginary B errors. Unknown label fails B. No oracle or new inference. All A&B matched strict success in every group. Product shown per training seed then averaged; pooled product also retained. Same-data descriptive independence check, not held-out prediction or proof of independence. B has variable emitted-call exposure and is not all-required-calls oracle ability.','source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'summary':out}
(R/'analysis/sequence-allcalls.json').write_text(json.dumps(obj,indent=2))
lines=['# Two whole-task components: complete name order and all emitted calls\n',obj['definition']]
for family in ['main','independent']:
 lines+=['\n## '+family]
 for model in ['qwen1.5b','qwen3b','qwen7b','qwen32b']:
  lines+=['\n### '+model,'|Calls|A: complete order correct|B: all emitted calls expanded correctly|A×B within seed|Actual whole task|','|---|---:|---:|---:|---:|']
  for z in out:
   if z['family']==family and z['model']==model:lines.append('| '+str(z['length'])+' | '+' | '.join(f'{z[k]*100:.2f}%' for k in ['A','B','seed_matched_product','actual'])+' |')
(R/'SEQUENCE_ALLCALLS.md').write_text('\n'.join(lines));print('\n'.join(lines))
