import json,time,subprocess
from common import R,write
records=[]
for p in sorted((R/'analysis').glob('*-status.json')):
    d=json.loads(p.read_text())
    if 'job' not in d or 'pid' not in d:continue
    pid=d['pid'];q=__import__('pathlib').Path('/proc')/str(pid)/'cmdline'
    cmd=q.read_bytes().replace(b'\0',b' ').decode() if q.exists() else ''
    active=('stability-study/src/run.py' in cmd and d['job']['id'] in cmd)
    log=R/'logs'/f'{d["job"]["id"]}.log';tail=''
    if log.exists():
        with log.open('rb') as f:
            f.seek(max(0,log.stat().st_size-1800));tail=f.read().decode(errors='replace').splitlines()[-1:]
    records.append(dict(job=d['job']['id'],gpu=d['gpu'],pid=pid,alive=active,returncode=d.get('returncode'),elapsed_seconds=d.get('end',time.time())-d['start'],last_log=tail))
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=index,memory.used,utilization.gpu','--format=csv,noheader'],text=True)
d=dict(checked=time.time(),pipeline=json.loads((R/'analysis/pipeline-state.json').read_text()),jobs=records,gpu=gpu)
write(R/'analysis/live-status.json',d);print(json.dumps(d,indent=2))
