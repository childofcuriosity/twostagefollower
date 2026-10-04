"""Actual execution with a local operation context; no oracle correction."""
import argparse,hashlib,json,os,time
from common import R,MODELS,checkpoint,rows,write,Path
from protocol import prompt,NAMES
from evaluate import (Session,Boundary,evaluate,torch,AutoTokenizer,AutoModelForCausalLM,
                      PeftModel,StoppingCriteriaList)

C=R/'context-intervention'


def digest(ids):
    return hashlib.sha256(json.dumps(ids).encode()).hexdigest()


def generation_context(session,scope):
    if scope=='full' or session.phase=='header':
        return session.ids.copy()
    assert scope=='local' and session.phase=='body'
    tool=session.calls[-1]['tool']
    # Only model-selected tool and current observed state enter this input.
    local={'x':list(session.state),'chain':[tool]}
    return session.tok.encode(prompt(local)+NAMES[tool]+':\n',add_special_tokens=False)


class Routed:
    def __init__(self,model,header,body):
        self.model=model;self.device=model.device;self.adapters={'header':header,'body':body}

    def generate(self,**kwargs):
        self.model.set_adapter(self.adapters[kwargs['stopping_criteria'][0].phase])
        return self.model.generate(**kwargs)


def scoped_evaluate(model,tok,selected,path,scope,batch_size=8):
    assert not path.exists()
    start=time.time();total=correct=0
    with path.open('x',buffering=1) as f:
        for offset in range(0,len(selected),batch_size):
            sessions=[Session(row,tok,'joint') for row in selected[offset:offset+batch_size]]
            while any(s.stop is None for s in sessions):
                for s in sessions:
                    if s.stop is None and (s.generated>=2048 or len(s.ids)+128>4096):
                        s.stop='token_or_context_budget'
                for phase in ['header','body']:
                    active=[s for s in sessions if s.stop is None and s.phase==phase]
                    if not active:continue
                    contexts=[generation_context(s,scope) for s in active]
                    n=max(map(len,contexts))
                    ids=torch.full((len(active),n),tok.pad_token_id,dtype=torch.long,device=model.device)
                    mask=torch.zeros_like(ids)
                    for i,context in enumerate(contexts):
                        ids[i,-len(context):]=torch.tensor(context,device=model.device)
                        mask[i,-len(context):]=1
                    with torch.inference_mode():
                        z=model.generate(input_ids=ids,attention_mask=mask,max_new_tokens=24 if phase=='header' else 128,
                                         do_sample=False,pad_token_id=tok.pad_token_id,eos_token_id=tok.eos_token_id,
                                         stopping_criteria=StoppingCriteriaList([Boundary(tok,n,phase)]),use_cache=True)
                    for s,new,context in zip(active,z[:,n:].tolist(),contexts):
                        s.accept(new)
                        s.events[-1]['generation_context']=dict(
                            scope='local' if scope=='local' and phase=='body' else 'full',
                            token_ids=context.copy(),sha256=digest(context))
            for s in sessions:
                result=s.finish();result['operation_context']=scope
                f.write(json.dumps(result)+'\n');total+=1;correct+=result['grade']['complete']
            if offset%64==0:
                print(json.dumps(dict(file=path.name,completed=total,total=len(selected),seconds=time.time()-start)),flush=True)
    return dict(n=total,complete=correct,seconds=time.time()-start,source=str(path))


def strip_context(row):
    row=json.loads(json.dumps(row));row.pop('operation_context',None)
    for event in row['events']:event.pop('generation_context',None)
    return row


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--job',required=True);args=parser.parse_args()
    job=json.loads(Path(args.job).read_text())
    root=R/'fresh-confirmation' if job['kind']=='confirmation' else C
    out=root/'runs'/job['id'];out.mkdir(exist_ok=False)
    torch.set_num_threads(4);torch.manual_seed(job['seed']);start=time.time()
    write(out/'config.json',dict(job=job,pid=os.getpid(),started=start,gpu=os.environ.get('CUDA_VISIBLE_DEVICES'),
                               sources={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/'src').glob('*.py')}))
    tok=AutoTokenizer.from_pretrained(MODELS[job['model']],local_files_only=True);tok.pad_token=tok.eos_token
    base=AutoModelForCausalLM.from_pretrained(MODELS[job['model']],local_files_only=True,
          torch_dtype=torch.bfloat16,attn_implementation='sdpa',low_cpu_mem_usage=True).cuda()
    model=None
    for condition in ['joint','operation_oracle','order_oracle']:
        p=checkpoint(job['model'],condition,job['seed'],512)
        if model is None:model=PeftModel.from_pretrained(base,p,adapter_name=condition).eval()
        else:model.load_adapter(p,adapter_name=condition,is_trainable=False)
    summary=[]
    if job['kind']=='control':
        chosen=[r for start in [0,96,192,288,384] for r in rows('independent')[start:start+8]]
        routed=Routed(model,'joint','joint')
        original=out/'original.jsonl';current=out/'full-context.jsonl'
        evaluate(routed,tok,chosen,'joint',original,8)
        scoped_evaluate(routed,tok,chosen,current,'full',8)
        a=list(map(json.loads,original.read_text().splitlines()))
        b=list(map(json.loads,current.read_text().splitlines()))
        exact=sum(x==strip_context(y) for x,y in zip(a,b))
        write(out/'control-check.json',dict(n=len(a),exact=exact))
        assert exact==len(a)==len(b)==40
    elif job['kind']=='confirmation':
        selected=list(map(json.loads,(root/'data/independent.jsonl').read_text().splitlines()))
        assert len(selected)==400
        for label,header,body in [('JJ','joint','joint'),('SE','operation_oracle','order_oracle')]:
            if label!=job['route']:continue
            for scope in ['full','local']:
                if scope!=job['scope']:continue
                p=out/f'{label}-{scope}.jsonl'
                summary.append(dict(route=label,scope=scope,**scoped_evaluate(Routed(model,header,body),tok,selected,p,scope,8)))
    else:
        assert job['kind']=='formal'
        for label,header,body in [('JJ','joint','joint'),('SJ','operation_oracle','joint'),
                                  ('JE','joint','order_oracle'),('SE','operation_oracle','order_oracle')]:
            if label!=job['route']:continue
            for split in ['dev','independent']:
                p=out/f'{label}-{split}.jsonl'
                summary.append(dict(route=label,split=split,**scoped_evaluate(Routed(model,header,body),tok,rows(split),p,'local',8)))
    write(out/'complete.json',dict(job=job,summary=summary,seconds=time.time()-start,
                                  peak_memory_bytes=torch.cuda.max_memory_allocated()))
    print('COMPLETE',job['id'],flush=True)


if __name__=='__main__':main()
