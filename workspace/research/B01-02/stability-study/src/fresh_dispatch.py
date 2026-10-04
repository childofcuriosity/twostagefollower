"""Queue the pre-frozen confirmation after the context intervention passes audit."""
import concurrent.futures,hashlib,json,os,subprocess,sys,time,queue
from common import R,O,write
from wait_marker import wait_for_marker

F=R/'fresh-confirmation';C=R/'context-intervention'
write(F/'analysis/launch.json',dict(pid=os.getpid(),started=time.time(),waiting_for='context-intervention pipeline-complete.json'))
wait_for_marker(C/'analysis/pipeline-complete.json',[C/'analysis/pipeline-failed.json',R/'analysis/pipeline-failed.json'])
assert json.loads((C/'analysis/completion-audit.json').read_text())['complete']
subprocess.run([sys.executable,str(R/'src/fresh_data_verify.py')],check=True)
files=[R/'src'/n for n in ['context_run.py','context_audit.py','fresh_analyze_audit.py','fresh_dispatch.py','fresh_data_verify.py','common.py','wait_marker.py']]
files += [O/'src/evaluate.py',O/'src/protocol.py',F/'data/independent.jsonl',F/'REGISTRATION.md']
write(F/'analysis/source-freeze.json',{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
jobs=[dict(id=f'{m}-s{s}-{route}-{scope}',kind='confirmation',model=m,seed=s,route=route,scope=scope) for m in ['qwen32b','qwen3b'] for s in [11,22,33] for route in ['JJ','SE'] for scope in ['full','local']]
write(F/'analysis/jobs.json',jobs)


def run(pair):
    job,gpu=pair;path=F/'analysis'/f'{job["id"]}-job.json';write(path,job)
    env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu)
    command=[sys.executable,'-u',str(R/'src/context_run.py'),'--job',str(path)]
    with (F/'logs'/f'{job["id"]}.log').open('x') as log:
        process=subprocess.Popen(command,env=env,stdout=log,stderr=subprocess.STDOUT)
        status=dict(job=job,pid=process.pid,gpu=gpu,command=command,start=time.time())
        record=F/'analysis'/f'{job["id"]}-status.json';write(record,status)
        status['returncode']=process.wait();status['end']=time.time();write(record,status)
    return status


try:
    available=queue.Queue()
    for gpu in range(8):available.put(gpu)
    def scheduled(job):
        gpu=available.get()
        try:return run((job,gpu))
        finally:available.put(gpu)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results=list(pool.map(scheduled,jobs))
    assert all(r['returncode']==0 for r in results),results
    subprocess.run([sys.executable,str(R/'src/fresh_analyze_audit.py')],check=True)
    write(F/'analysis/pipeline-complete.json',dict(finished=time.time(),note='Scientific review still required; not a goal-completion marker.'))
except BaseException as exc:
    write(F/'analysis/pipeline-failed.json',dict(error=repr(exc),time=time.time()));raise
