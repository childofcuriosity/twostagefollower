from common import *
from score import grade
import itertools
count=0
for c in CONDITIONS:
 for t in range(9):
  for x in ([0,0,0,0],[9,9,9,9],[9,0,4,7],[1,2,3,4]):
   row=dict(id=f'test-{c}-{t}-{x}',condition=c,chain=[t,t],x=x,split='validation',depth=2)
   row.update(raw=target(row,c),expected=list(dsl.execute(x,dsl.expand(row['chain'],LIB))),finish_reason='eos',generated_tokens=100,text_tokens=99,input_tokens=100,max_new_tokens=256,allocated_generate_seconds=1.)
   g=grade(row);assert g['strict']==1 and g['header_compliant']==1 and g['first_error']=='none'
   bad=dict(row,raw=row['raw'].replace('Answer:','Final:'));assert not grade(bad)['strict']
   lines=row['raw'].splitlines();parts=lines[1].split();parts[1]=str((int(parts[1])+1)%10);lines[1]=' '.join(parts)
   bad=dict(row,raw='\n'.join(lines));assert grade(bad)['first_error']=='numeric' and not grade(bad)['strict']
   bad=dict(row,raw=row['raw'].replace(labels(row,c)[0]+':','unrelated:',1));gg=grade(bad);assert gg['strict']==1 and not gg['header_compliant']
   count+=1
# Exhaustive primitive range and reference checks, all four digits.
for x in itertools.product(range(10),repeat=4):
 a,b,c,d=x
 expected={'rev':(d,c,b,a),'rot':(b,c,d,a),'inc':tuple((v+1)%10 for v in x),'neg':tuple((-v)%10 for v in x),'swap':(b,a,c,d),'ends':((a+1)%10,b,c,(d+1)%10)}
 for op,y in expected.items():assert dsl.step(x,op)==y
write(R/'analysis/implementation-validation.json',dict(correct_trace_cases=count,mutations_per_case=3,primitive_checks=60000,passed=True,score_sha256=sha(R/'src/score.py')))
print('PASS',count,'correct traces + mutations; 60000 primitive checks')
