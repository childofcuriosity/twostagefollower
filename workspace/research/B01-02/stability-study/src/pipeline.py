import hashlib,json,os,subprocess,sys,time
from common import R,O,write
for phase,args in [('controls',['dispatch.py','--controls']),('formal',['dispatch.py']),('analysis',['analyze.py']),('audit',['audit.py'])]:
    write(R/'analysis/pipeline-state.json',dict(pid=os.getpid(),phase=phase,started=time.time()))
    if phase=='formal':
        files=list((R/'src').glob('*.py'))+list((R/'data').glob('*.jsonl'))+[O/'src/evaluate.py',O/'src/protocol.py']
        write(R/'analysis/formal-source-freeze.json',{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
    p=subprocess.run([sys.executable,'-u',str(R/'src'/args[0]),*args[1:]])
    if p.returncode:
        write(R/'analysis/pipeline-failed.json',dict(phase=phase,returncode=p.returncode,time=time.time()));raise SystemExit(p.returncode)
write(R/'analysis/pipeline-complete.json',dict(finished=time.time(),note='Computation and raw audit complete; scientific interpretation and delivery still required.'))
