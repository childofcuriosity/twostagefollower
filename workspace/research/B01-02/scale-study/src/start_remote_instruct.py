from pathlib import Path
import subprocess,sys,json,time,socket
R=Path(__file__).resolve().parents[1];W=R.parents[3]
with (W/'logs/training/scale-remote-instruct.log').open('x') as f:
 p=subprocess.Popen([sys.executable,'-u',str(R/'src/launch_supplement.py'),'--lane','instruct','--remote-ready'],cwd=W,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
record=dict(pid=p.pid,hostname=socket.gethostname(),utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()));(R/'analysis/remote-instruct-process.json').write_text(json.dumps(record,indent=2));print(json.dumps(record))
