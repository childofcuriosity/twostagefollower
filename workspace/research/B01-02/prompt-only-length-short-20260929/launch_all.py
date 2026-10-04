from pathlib import Path
import sys,json,subprocess,time
R=Path(__file__).resolve().parent;B=R.parent;PROJECT=B.parents[2]
sys.path.insert(0,str(B/'grpo-binary/src'))
from remote import execute
for L in [3,4,6,7,8,9]:
 p=R/'7b'/f'data/explore-L{L}.jsonl';q=R/'14b'/f'data/explore-L{L}.jsonl';assert p.read_bytes()==q.read_bytes()
 a=json.loads((R/'7b'/f'data/explore-L{L}-manifest.json').read_text());b=json.loads((R/'14b'/f'data/explore-L{L}-manifest.json').read_text());assert a['max_new_tokens']==b['max_new_tokens'];assert a['prompts']==b['prompts']
(R/'jobs').mkdir(exist_ok=True);(R/'logs').mkdir(exist_ok=True)
assign=[]
for mi,model in enumerate(['7b','14b']):
 for i,L in enumerate([3,4,6,7]):assign.append(('local',4*mi+i,model,L,['STEP','NAME']))
for server,model in [('remote65','7b'),('remote70','14b')]:
 for gpu,(L,c) in enumerate([(8,'STEP'),(8,'NAME'),(9,'STEP'),(9,'NAME')]):assign.append((server,gpu,model,L,[c]))
started=time.time();jobs=[]
for server,gpu,model,L,conds in assign:
 name=f'{server}-gpu{gpu}-{model}-L{L}';p=R/f'jobs/{name}.json'
 command=f'source training-env.sh && CUDA_VISIBLE_DEVICES={gpu} python {R/model}/src/worker.py --phase explore --lengths {L} --conditions {" ".join(conds)} --batch 32'
 job=dict(log=str(R/f'logs/{name}.log'),command=command,server=server,gpu=gpu,model=model,length=L,conditions=conds)
 assert not p.exists();p.write_text(json.dumps(job,indent=2)+'\n')
 cmd=f'cd {PROJECT} && python {B}/grpo-binary/src/launch.py --job {p}'
 result=subprocess.run(['bash','-lc',cmd],capture_output=True,text=True) if server=='local' else execute(server,cmd)
 assert result.returncode==0,(name,result.stderr)
 jobs.append(str(p));print('LAUNCHED',name,flush=True)
(R/'dispatch.json').write_text(json.dumps(dict(started=started,jobs=jobs),indent=2)+'\n')
