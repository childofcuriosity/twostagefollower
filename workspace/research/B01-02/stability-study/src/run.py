"""Replay fixed checkpoints and route learned adapters without oracle corrections."""
import argparse,hashlib,json,os,time,sys
from common import *
from evaluate import evaluate,AutoTokenizer,AutoModelForCausalLM,PeftModel,torch

class Routed:
    def __init__(self,model,header,body):
        self.model=model;self.device=model.device;self.adapters={'header':header,'body':body}
    def generate(self,**kwargs):
        phase=kwargs['stopping_criteria'][0].phase
        self.model.set_adapter(self.adapters[phase])
        return self.model.generate(**kwargs)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--job',required=True);a=ap.parse_args()
    job=json.loads(Path(a.job).read_text());out=R/'runs'/job['id'];out.mkdir(exist_ok=False)
    torch.set_num_threads(4);torch.manual_seed(job['seed']);t0=time.time()
    write(out/'config.json',dict(job=job,pid=os.getpid(),started=t0,gpu=os.environ.get('CUDA_VISIBLE_DEVICES'),sources={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/'src').glob('*.py')}))
    tok=AutoTokenizer.from_pretrained(MODELS[job['model']],local_files_only=True);tok.pad_token=tok.eos_token
    base=AutoModelForCausalLM.from_pretrained(MODELS[job['model']],local_files_only=True,torch_dtype=torch.bfloat16,attn_implementation='sdpa',low_cpu_mem_usage=True).cuda()
    model=None;summary=[];cached=[]
    def adapter(condition,step):
        nonlocal model
        name=f'{condition}_{step}'
        if name not in cached:
            path=checkpoint(job['model'],condition,job['seed'],step)
            if model is None:model=PeftModel.from_pretrained(base,path,adapter_name=name).eval()
            else:model.load_adapter(path,adapter_name=name,is_trainable=False)
            cached.append(name)
        model.set_adapter(name);model.eval();return name
    if job['kind']=='curve':
        condition=job['condition']
        for step in [64,128,256,512]:
            adapter(condition,step)
            for mode in (['joint','order_oracle','operation_oracle'] if condition=='joint' else [condition]):
                for split in ['dev','independent']:
                    filename=f'step{step}-{mode}-{split}.jsonl'
                    if step==512 and split=='independent' and job['model']=='qwen32b':
                        source=O/'runs'/f'{job["model"]}-{condition}-s{job["seed"]}'/f'evaluation-{mode}-independent.jsonl'
                        records=[json.loads(l) for l in source.read_text().splitlines()]
                        assert len(records)==480
                        summary.append(dict(step=step,mode=mode,split=split,source=str(source),reuse=True,n=480,complete=sum(x['grade']['complete'] for x in records)))
                    else:
                        stats=evaluate(model,tok,rows(split),mode,out/filename,8)
                        summary.append(dict(step=step,mode=mode,split=split,source=str(out/filename),reuse=False,**stats))
    elif job['kind'] in ['compose','control']:
        control_reference=None
        if job['kind']=='control':
            adapter('joint',512)
            selected=[r for start in [0,96,192,288,384] for r in rows('independent')[start:start+8]]
            refpath=out/'single-adapter-reference.jsonl'
            evaluate(model,tok,selected,'joint',refpath,8)
            control_reference={x['id']:x for x in map(json.loads,refpath.read_text().splitlines())}
        for step in ([512] if job['kind']=='control' else [256,512]):
            names={c:adapter(c,step) for c in ['joint','operation_oracle','order_oracle']}
            combos=[('JJ','joint','joint')] if job['kind']=='control' else [('SE','operation_oracle','order_oracle'),('SJ','operation_oracle','joint'),('JE','joint','order_oracle')]
            for label,h,b in combos:
                for split in (['independent'] if job['kind']=='control' else ['dev','independent']):
                    selected=rows(split)
                    if job['kind']=='control':selected=[r for start in [0,96,192,288,384] for r in selected[start:start+8]]
                    path=out/f'step{step}-{label}-{split}.jsonl'
                    stats=evaluate(Routed(model,names[h],names[b]),tok,selected,'joint',path,8)
                    summary.append(dict(step=step,mode=label,split=split,source=str(path),reuse=False,**stats))
                    if job['kind']=='control':
                        old={x['id']:x for x in map(json.loads,(O/'runs'/f'{job["model"]}-joint-s{job["seed"]}'/'evaluation-joint-independent.jsonl').read_text().splitlines())}
                        actual=list(map(json.loads,path.read_text().splitlines()));exact=sum(x==control_reference[x['id']] for x in actual)
                        write(out/'control-check.json',dict(n=len(actual),exact=exact,old_record_exact=sum(x==old[x['id']] for x in actual),old_grade_equal=sum(x['grade']==old[x['id']]['grade'] for x in actual),comparison='Direct single adapter vs routed same adapter on current hardware; old output comparison reported separately.'))
                        assert exact==len(actual),(job,exact,len(actual))
    else:raise ValueError(job['kind'])
    write(out/'complete.json',dict(job=job,summary=summary,total_seconds=time.time()-t0,peak_memory_bytes=torch.cuda.max_memory_allocated(),finished=time.time()))
    print('COMPLETE',job['id'],flush=True)
if __name__=='__main__':main()
