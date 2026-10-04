"""Run the registered context intervention only after the main matrix audit."""
import concurrent.futures,hashlib,json,os,subprocess,sys,time,queue
from common import R,O,write
from wait_marker import wait_for_marker

C=R/'context-intervention'
for d in ['runs','analysis','logs']:(C/d).mkdir(parents=True,exist_ok=True)
write(C/'analysis/launch.json',dict(pid=os.getpid(),started=time.time(),waiting_for='main pipeline-complete.json'))
wait_for_marker(R/'analysis/pipeline-complete.json',[R/'analysis/pipeline-failed.json'])
assert json.loads((C/'analysis/controller-check.json').read_text())['passed']
assert json.loads((R/'analysis/completion-audit.json').read_text())['complete']
files=[R/'src'/n for n in ['context_run.py','context_audit.py','context_dispatch.py','context_check.py','common.py','wait_marker.py']]
files += [O/'src/evaluate.py',O/'src/protocol.py'] + list((R/'data').glob('*.jsonl'))
write(C/'analysis/source-freeze.json',{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
jobs=[dict(id=f'control-{m}',kind='control',model=m,seed=11) for m in ['qwen3b','qwen32b']]
jobs += [dict(id=f'{m}-s{s}-{route}',kind='formal',model=m,seed=s,route=route) for m in ['qwen32b','qwen3b'] for s in [11,22,33] for route in ['JJ','SJ','JE','SE']]
write(C/'analysis/jobs.json',jobs)


def run(job,gpu):
    p=C/'analysis'/f'{job["id"]}-job.json';write(p,job)
    command=[sys.executable,'-u',str(R/'src/context_run.py'),'--job',str(p)]
    env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu)
    with (C/'logs'/f'{job["id"]}.log').open('x') as log:
        process=subprocess.Popen(command,env=env,stdout=log,stderr=subprocess.STDOUT)
        status=dict(job=job,pid=process.pid,gpu=gpu,command=command,start=time.time())
        path=C/'analysis'/f'{job["id"]}-status.json';write(path,status)
        status['returncode']=process.wait();status['end']=time.time();write(path,status)
    return status


try:
    available=queue.Queue()
    for gpu in range(8):available.put(gpu)
    def scheduled(job):
        gpu=available.get()
        try:return run(job,gpu)
        finally:available.put(gpu)
    for kind in ['control','formal']:
        selected=[j for j in jobs if j['kind']==kind]
        write(C/'analysis/state.json',dict(phase=kind,time=time.time()))
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results=list(pool.map(scheduled,selected))
        assert all(r['returncode']==0 for r in results),results
    for name in ['context_analyze.py','context_audit.py']:
        write(C/'analysis/state.json',dict(phase=name,time=time.time()))
        subprocess.run([sys.executable,str(R/'src'/name)],check=True)
    write(C/'analysis/pipeline-complete.json',dict(finished=time.time(),note='Agent review and final interpretation remain required.'))
except BaseException as exc:
    write(C/'analysis/pipeline-failed.json',dict(error=repr(exc),time=time.time()))
    raise
