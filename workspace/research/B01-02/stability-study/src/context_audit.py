"""Reconstruct both the global trace and actual generation inputs independently."""
import hashlib,json
from common import R,MODELS,rows,write,Path
from protocol import prompt,NAMES,parse_header,parse_body
from audit_results import audit
from transformers import AutoTokenizer

C=R/'context-intervention'


def digest(ids):
    return hashlib.sha256(json.dumps(ids).encode()).hexdigest()


def audit_context(row,tok):
    audit(row)
    ids=tok.encode(prompt(row),add_special_tokens=False);state=tuple(row['x']);tool=None
    for e in row['events']:
        assert e['source']=='model'
        assert (e['prefix_tokens'],e['prefix_sha256'])==(len(ids),digest(ids))
        assert tok.decode(e['token_ids'],clean_up_tokenization_spaces=False)==e['text']
        actual=e['generation_context']
        if e['phase']=='body' and row['operation_context']=='local':
            assert tool is not None
            expected=tok.encode(prompt({'x':list(state),'chain':[tool]})+NAMES[tool]+':\n',add_special_tokens=False)
            assert actual['scope']=='local'
        else:
            expected=ids.copy();assert actual['scope']=='full'
        assert actual['token_ids']==expected and actual['sha256']==digest(expected)
        ids+=e['token_ids']
        try:
            if e['phase']=='header':tool=parse_header(e['text'])
            else:state=tuple(parse_body(e['text'],state,tool)['state'])
        except ValueError:
            assert e is row['events'][-1]
    return len(row['events'])


def main():
    jobs=json.loads((C/'analysis/jobs.json').read_text());n=events=0;hashes={}
    for model in ['qwen3b','qwen32b']:
        tok=AutoTokenizer.from_pretrained(MODELS[model],local_files_only=True)
        for job in [j for j in jobs if j['model']==model]:
            root=C/'runs'/job['id'];d=json.loads((root/'complete.json').read_text());assert d['job']==job
            if job['kind']=='control':
                check=json.loads((root/'control-check.json').read_text());assert check['n']==check['exact']==40
                for line in (root/'full-context.jsonl').read_text().splitlines():audit_context(json.loads(line),tok)
                continue
            assert len(d['summary'])==2
            for source in d['summary']:
                assert source['route']==job['route']
                path=Path(source['source']);raw=path.read_bytes();hashes[str(path)]=hashlib.sha256(raw).hexdigest()
                records=list(map(json.loads,raw.splitlines()));expected=rows(source['split'])
                assert len(records)==len(expected)==source['n']
                for row,ref in zip(records,expected):
                    assert (row['id'],row['x'],row['chain'])==(ref['id'],ref['x'],ref['chain'])
                    assert row['operation_context']=='local';events+=audit_context(row,tok)
                assert sum(r['grade']['complete'] for r in records)==source['complete'];n+=len(records)
    assert n==16896
    freeze=json.loads((C/'analysis/source-freeze.json').read_text())
    for p,h in freeze.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
    write(C/'analysis/completion-audit.json',dict(complete=True,trajectories=n,events=events,files=hashes,
          generation_contexts_reconstructed=True,model_selected_names_and_actual_states_only=True))
    print('CONTEXT AUDIT PASSED',n,events)


if __name__=='__main__':main()
