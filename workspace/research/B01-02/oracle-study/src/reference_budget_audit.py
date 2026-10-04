"""Ensure reference trajectories fit budgets and fragment/full tokenizations agree."""
import json
from transformers import AutoTokenizer
from protocol import R,MODELS,fragments,read

out={}
for model,path in MODELS.items():
    tok=AutoTokenizer.from_pretrained(path,local_files_only=True);maxima=dict(header=0,body=0,generated=0,context=0);n=0
    for row in read('train')+read('test')+read('independent'):
        fs=fragments(row);tokens=[tok.encode(text,add_special_tokens=False) for kind,text in fs]
        assert sum(tokens,[])==tok.encode(''.join(t for k,t in fs),add_special_tokens=False)
        generated=sum(map(len,tokens[1:]));context=sum(map(len,tokens));assert generated<2048 and context+128<=4096
        for (kind,text),ids in zip(fs,tokens):
            if kind in ['header','finish']:assert len(ids)<=24;maxima['header']=max(maxima['header'],len(ids))
            if kind=='body':assert len(ids)<=128;maxima['body']=max(maxima['body'],len(ids))
        maxima['generated']=max(maxima['generated'],generated);maxima['context']=max(maxima['context'],context);n+=1
    out[model]=dict(reference_trajectories=n,maxima=maxima)
(R/'analysis/reference-budget-audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
