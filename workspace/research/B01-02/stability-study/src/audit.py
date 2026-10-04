"""Independent operation grading and token provenance for complete registered matrix."""
import hashlib,json
from common import *
from audit_results import audit
from protocol import prompt
from transformers import AutoTokenizer

def main():
    jobs=json.loads((R/'analysis/jobs.json').read_text());total=new=events=0;files={};reused=0
    for model in ['qwen3b','qwen32b']:
        tok=AutoTokenizer.from_pretrained(MODELS[model],local_files_only=True)
        for job in [j for j in jobs if j['model']==model]:
            p=R/'runs'/job['id']/'complete.json';assert p.exists(),p
            d=json.loads(p.read_text());assert d['job']==job
            if job['kind']=='control':
                c=json.loads((p.parent/'control-check.json').read_text());assert c['exact']==c['n']==40;continue
            for e in d['summary']:
                src=Path(e['source']);data=src.read_bytes();files[str(src)]=hashlib.sha256(data).hexdigest();records=list(map(json.loads,data.splitlines()));expected=rows(e['split'])
                assert len(records)==len(expected)==e['n'];assert [r['id'] for r in records]==[r['id'] for r in expected]
                for r,ref in zip(records,expected):
                    assert (r['x'],r['chain'])==(ref['x'],ref['chain']);audit(r)
                    if job['kind']=='curve':assert r['mode']==e['mode']
                    if job['kind']=='compose':assert r['mode']=='joint' and all(x['source']=='model' for x in r['events'])
                    ids=tok.encode(prompt(r),add_special_tokens=False)
                    for event in r['events']:
                        assert len(ids)==event['prefix_tokens'];assert hashlib.sha256(json.dumps(ids).encode()).hexdigest()==event['prefix_sha256'];assert tok.decode(event['token_ids'],clean_up_tokenization_spaces=False)==event['text'];ids+=event['token_ids'];events+=1
                assert sum(r['grade']['complete'] for r in records)==e['complete']
                total+=len(records)
                if e['reuse']:reused+=len(records)
                else:new+=len(records)
    assert (total,new,reused)==(109824,102624,7200)
    freeze=json.loads((R/'analysis/formal-source-freeze.json').read_text())
    for p,h in freeze.items():
        if Path(p).name in ['run.py','common.py','dispatch.py','evaluate.py','protocol.py'] or Path(p).suffix=='.jsonl':assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
    write(R/'analysis/completion-audit.json',dict(complete=True,covered=total,new=new,reused=reused,events=events,files=files,control_records=80,all_composition_tokens_model_generated=True))
    print('FULL MATRIX AUDIT PASSED',total,new,reused,events)
if __name__=='__main__':main()
