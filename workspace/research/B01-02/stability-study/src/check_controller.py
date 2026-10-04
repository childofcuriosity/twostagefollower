"""Exercise actual shared scheduler with learned-role routing and injected errors."""
import re,json,torch,importlib.util
from common import *
spec=importlib.util.spec_from_file_location('stability_checkpoint_runner',R/'src/run.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);Routed=module.Routed
from evaluate import Session,evaluate,AutoTokenizer
from protocol import NAMES,IDX,body
tok=AutoTokenizer.from_pretrained(MODELS['qwen3b'],local_files_only=True);tok.pad_token=tok.eos_token
class Fake:
    device='cpu'
    def __init__(self):self.trace=[]
    def set_adapter(self,name):self.active=name
    def generate(self,input_ids,attention_mask,stopping_criteria,**kw):
        phase=stopping_criteria[0].phase;assert self.active=={'header':'S','body':'E'}[phase];self.trace.append(phase);outputs=[]
        for ids in input_ids:
            text=tok.decode(ids.tolist(),skip_special_tokens=True);chain=re.search(r'^Functions: (.*)$',text,re.M)[1].split();trace=text.split('Trace:\n',1)[1];headers=re.findall(r'^([a-z]+):$',trace,re.M)
            if phase=='header':suffix=chain[len(headers)]+':\n' if len(headers)<len(chain) else 'Done\n'
            else:
                states=re.findall(r'^(?:rev|rot|inc|neg|swap|ends) ([0-9] [0-9] [0-9] [0-9])$',trace,re.M)
                state=list(map(int,(states[-1] if states else re.search(r'^Input: (.*)$',text,re.M)[1]).split()));suffix=body(IDX[headers[-1]],state)[0]
            outputs.append(tok.encode(suffix,add_special_tokens=False))
        n=max(map(len,outputs));return torch.cat([input_ids,torch.tensor([x+[tok.eos_token_id]*(n-len(x)) for x in outputs])],dim=1)
fake=Fake();p=R/'analysis/mock-routed.jsonl';result=evaluate(Routed(fake,'S','E'),tok,rows('independent')[:8],'joint',p,8);assert result['complete']==8
assert set(fake.trace)=={'header','body'}
records=list(map(json.loads,p.read_text().splitlines()));assert all(e['source']=='model' for r in records for e in r['events'])
checks=['phase_adapter_routing','batched_reference_correct','all_tokens_model_owned']
row=rows('independent')[0];s=Session(row,tok,'joint');wrong=(row['chain'][0]+1)%9;s.accept(tok.encode(NAMES[wrong]+':\n',add_special_tokens=False));assert s.calls[-1]['tool']==wrong
s.accept(tok.encode('inc 9 9 9 9\nEndTool\n',add_special_tokens=False));assert s.state==(9,9,9,9);assert '9 9 9 9' in tok.decode(s.ids)
s.accept(tok.encode('Done\n',add_special_tokens=False));assert s.stop=='done' and not s.finish()['grade']['complete'];checks+=['wrong_tool_not_corrected','wrong_state_preserved_in_next_model_context','early_done_allowed_and_scored_wrong']
s=Session(row,tok,'joint');s.accept(tok.encode(NAMES[row['chain'][0]]+':\n',add_special_tokens=False));s.accept(tok.encode('inc 1 2 3 4\n',add_special_tokens=False));assert s.stop and not s.finish()['grade']['complete'];checks+=['missing_EndTool_fails']
write(R/'analysis/controller-check.json',dict(checks=checks,passed=True,mock_only=True));print(checks)
