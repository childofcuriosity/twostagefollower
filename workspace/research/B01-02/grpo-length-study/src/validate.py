from common import *
from engine import advantages,pack,loss_terms
import torch
cfg=json.loads((R/'config/precheck-v1.json').read_text())
checked=0
for c in CONDITIONS:
 for row in readrows(R/'data/precheck.jsonl'):
  text=target(row,c);g=score(row,text,c,100,'eos');assert g['reward']==1 and g['header_compliant']==1
  changed=HEADER.sub('anything:',text) if False else '\n'.join('anything:' if HEADER.fullmatch(s) else s for s in text.splitlines())
  gg=score(row,changed,c,100,'eos');assert gg['reward']==1 and gg['header_compliant']==0
  lines=text.splitlines();idx=next(i for i,s in enumerate(lines) if OP.fullmatch(s));parts=lines[idx].split();parts[-1]=str((int(parts[-1])+1)%10);lines[idx]=' '.join(parts)
  assert score(row,'\n'.join(lines),c,100,'eos')['reward']==0
  assert score(row,text+'explanation',c,100,'eos')['reward']==0
  checked+=1
legacy_count=0
for root in [B/'prompt-only',OLD]:
 previous={(x['id'],x['condition']):x['strict'] for path in (root/'analysis').glob('graded-*.jsonl') for x in readrows(path)}
 for p in (root/'runs').glob('*/predictions.jsonl'):
  for row in readrows(p):
   if row['condition'] not in CONDITIONS:continue
   g=score(row,row['raw'],row['condition'],row['generated_tokens'],row['finish_reason'],cap=row['max_new_tokens']);assert g['reward']==previous[(row['id'],row['condition'])];legacy_count+=1
r=[0]*8+[1]*8+[0]*4+[1]*4;a,stats=advantages(r,8,1e-4);assert torch.equal(a[:16],torch.zeros(16));assert abs(float(a[16:].mean()))<1e-7
rows=[dict(prompt_ids=[1,2,3],output_ids=[4,9]),dict(prompt_ids=[1,2],output_ids=[3,4,9])]
ids,attention,mask=pack(rows,pad=9,device='cpu');assert mask.sum().item()==5
assert mask[0].tolist()==[0.,0.,1.,1.] and mask[1].tolist()==[0.,1.,1.,1.]
lp=torch.zeros_like(mask,requires_grad=True);ref=torch.zeros_like(mask);adv=torch.tensor([1.,-1.]);loss,_=loss_terms(lp,ref,mask,adv,cfg);loss.backward()
assert torch.equal(lp.grad[mask==0],torch.zeros_like(lp.grad[mask==0]))
expected=-adv[:,None]*mask/mask.sum(1,keepdim=True)/2;assert torch.allclose(lp.grad,expected)
assert lp.grad[0,-1]<0 and lp.grad[1,-1]>0 # Real EOS token participates.
write(R/'analysis/implementation-tests.json',dict(passed=True,precheck_correct_traces=checked,mutations_per_trace=3,historical_outputs_reward_checked=legacy_count,uniform_groups_zero_advantage=True,prompt_and_padding_zero_gradient=True,eos_has_policy_gradient=True,per_completion_aggregation_verified=True,legacy_sha256=sha(B/'scale-study/src/audit.py')))
print('PASS',checked,'correct traces and mutations;',legacy_count,'historical outputs; advantage/mask/EOS/aggregation checks')
