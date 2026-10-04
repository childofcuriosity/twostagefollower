import hashlib,importlib.util,json,random,re,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];B=R.parent;PROJECT=R.parents[3]
OLD=B/'prompt-only/fallback14';MODEL=B/'prompt-only/models/qwen14b'
sys.path.insert(0,str(OLD/'src'))
spec=importlib.util.spec_from_file_location('frozen_prompt_reference',OLD/'src/common.py');prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
spec=importlib.util.spec_from_file_location('legacy_strict_audit',B/'scale-study/src/audit.py');legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
dsl=prior.dsl;LIB=prior.LIB;NAMES=prior.NAMES;EXAMPLE=prior.EXAMPLE
CONDITIONS=('STEP','NAME');SEEDS=(301,302,303)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.tmp');tmp.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');tmp.replace(p)
def readrows(p):return [json.loads(s) for s in Path(p).read_text().splitlines()]
def saverows(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(''.join(json.dumps(row)+'\n' for row in x))
def key(row):return tuple(row['chain']),tuple(row['x'])
def prompt(row,c):
 assert c in CONDITIONS
 return prior.prompt(row,c)
def target(row,c):return prior.target(row,c)
HEADER=re.compile(r'^[A-Za-z][A-Za-z0-9]*:$')
OP=re.compile(r'^(rev|rot|inc|neg|swap|ends) ([0-9]) ([0-9]) ([0-9]) ([0-9])$')
def score(row,raw,c,tokens,finish):
 normalized='\n'.join('step:' if HEADER.fullmatch(s) else s for s in raw.splitlines())
 pred=dsl.answer(normalized);expected=list(dsl.execute(row['x'],dsl.expand(row['chain'],LIB)))
 rr=dict(row,raw=normalized,expected=expected,prediction=list(pred) if pred is not None else None,correct=pred is not None and list(pred)==expected,generated_tokens=tokens,max_new_tokens=256)
 g=legacy.check(rr)
 headings=[s[:-1] for s in raw.splitlines() if HEADER.fullmatch(s)];need=prior.labels(row,c)
 return dict(reward=g['strict_trace'],strict=g['strict_trace'],header_compliant=int(headings==need),numeric_error=g['numeric_step_error'],operation_mismatch=int([m.group(1) for s in raw.splitlines() if (m:=OP.fullmatch(s))]!=list(dsl.expand(row['chain'],LIB))),early_end=g['operation_prefix_only'],extra_output=g['format_extra_lines'],extra_ops=int(g['emitted_ops']>g['required_ops']),missing_ops=int(g['emitted_ops']<g['required_ops']),finish_reason=finish,legacy=g)
