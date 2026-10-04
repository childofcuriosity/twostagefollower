from pathlib import Path
import subprocess,sys,json,time,socket
R=Path(__file__).resolve().parents[1];W=R.parents[3];seeds=sys.argv[1]
with (W/f'logs/training/scale-remote-checkpoints-{seeds.replace(",","-")}.log').open('x') as f:
 p=subprocess.Popen([sys.executable,'-u',str(R/'src/remote_checkpoints.py'),'--seeds',seeds],cwd=W,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
record=dict(pid=p.pid,seeds=seeds,hostname=socket.gethostname(),utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()));(R/f'analysis/remote-checkpoints-process-{seeds.replace(",","-")}.json').write_text(json.dumps(record,indent=2));print(json.dumps(record))
