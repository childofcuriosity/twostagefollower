"""Local queue: GPU lanes, exact job records, no remote access or overwrite."""
import concurrent.futures,json,os,subprocess,sys,time
from common import R,write

jobs=json.loads((R/'analysis/jobs.json').read_text())
if '--controls' in sys.argv:jobs=[j for j in jobs if j['kind']=='control'];gpus=[6,7];tag='controls'
else:
    for model in ['qwen3b','qwen32b']:
        c=json.loads((R/'runs'/f'control-{model}-s11'/'control-check.json').read_text());assert c['n']==c['exact']==40
    assert (R/'analysis/controller-check.json').exists()
    jobs=[j for j in jobs if j['kind']!='control'];gpus=list(range(8));tag='formal'
import queue
pending=queue.Queue()
for job in jobs:pending.put(job)
def lane(gpu):
    records=[]
    while True:
        try:job=pending.get_nowait()
        except queue.Empty:return records
        env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu)
        cfg=R/'analysis/job-configs'/f'{job["id"]}.json'
        cmd=[sys.executable,'-u',str(R/'src/run.py'),'--job',str(cfg)]
        with (R/'logs'/f'{job["id"]}.log').open('x') as log:
            p=subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT)
            rec=dict(job=job,pid=p.pid,gpu=gpu,command=cmd,start=time.time());write(R/'analysis'/f'{job["id"]}-status.json',rec)
            rec.update(returncode=p.wait(),end=time.time());write(R/'analysis'/f'{job["id"]}-status.json',rec);records.append(rec)
        if rec['returncode']!=0:print('FAILED',job['id'],flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=len(gpus)) as pool:records=[r for lane_records in pool.map(lane,gpus) for r in lane_records]
write(R/'analysis'/f'{tag}-complete.json',dict(records=records,finished=time.time()))
assert all(r['returncode']==0 for r in records)
