"""Behavioral tests of local operation inputs and uncorrected failure paths."""
import json,re,torch
from common import R,MODELS,rows,write
from context_run import C,Routed,scoped_evaluate,generation_context
from context_audit import audit_context
from evaluate import Session,AutoTokenizer
from protocol import NAMES,IDX,body,prompt

tok=AutoTokenizer.from_pretrained(MODELS['qwen3b'],local_files_only=True);tok.pad_token=tok.eos_token
for directory in ['runs','analysis','logs']:(C/directory).mkdir(parents=True,exist_ok=True)


class Fake:
    device='cpu'
    def set_adapter(self,name):self.active=name
    def generate(self,input_ids,attention_mask,stopping_criteria,**kwargs):
        phase=stopping_criteria[0].phase;assert self.active=={'header':'S','body':'E'}[phase];outputs=[]
        for ids in input_ids:
            text=tok.decode(ids.tolist(),skip_special_tokens=True)
            chain=re.search(r'^Functions: (.*)$',text,re.M)[1].split()
            trace=text.split('Trace:\n',1)[1];headers=re.findall(r'^([a-z]+):$',trace,re.M)
            if phase=='header':suffix=chain[len(headers)]+':\n' if len(headers)<len(chain) else 'Done\n'
            else:
                assert len(chain)==len(headers)==1
                state=list(map(int,re.search(r'^Input: (.*)$',text,re.M)[1].split()))
                suffix=body(IDX[headers[-1]],state)[0]
            outputs.append(tok.encode(suffix,add_special_tokens=False))
        n=max(map(len,outputs))
        return torch.cat([input_ids,torch.tensor([x+[tok.eos_token_id]*(n-len(x)) for x in outputs])],dim=1)


p=C/'analysis/mock.jsonl'
result=scoped_evaluate(Routed(Fake(),'S','E'),tok,rows('independent')[-8:],p,'local',8)
assert result['complete']==8
for row in map(json.loads,p.read_text().splitlines()):audit_context(row,tok)
checks=['local_body_full_header_routing','eight_tool_batched_execution','global_and_local_token_provenance']
row=rows('independent')[0];s=Session(row,tok,'joint');wrong=(row['chain'][0]+1)%9
s.accept(tok.encode(NAMES[wrong]+':\n',add_special_tokens=False))
context=tok.decode(generation_context(s,'local'));assert f'Functions: {NAMES[wrong]}\n' in context
s.accept(tok.encode('inc 9 9 9 9\nEndTool\n',add_special_tokens=False))
s.accept(tok.encode(NAMES[wrong]+':\n',add_special_tokens=False))
assert 'Input: 9 9 9 9\n' in tok.decode(generation_context(s,'local'))
copied=generation_context(s,'full');s.ids.append(123);assert copied!=s.ids;s.ids.pop()
checks+=['wrong_selected_tool_preserved','wrong_state_preserved','context_snapshot_not_mutated']
s.accept(tok.encode('EndTool\n',add_special_tokens=False));s.accept(tok.encode('Done\n',add_special_tokens=False))
assert not s.finish()['grade']['complete'];checks+=['early_done_not_prevented']
write(C/'analysis/controller-check.json',dict(passed=True,checks=checks,mock_only=True));print(checks)
