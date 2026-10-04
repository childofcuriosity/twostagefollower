from pathlib import Path
import subprocess,sys,json,time
R=Path(__file__).resolve().parents[1];W=R.parents[3]
log=W/'logs/training/scale-remote-qwen3b.log'
with log.open('x') as f:
 p=subprocess.Popen([sys.executable,'-u',str(R/'src/remote_3b.py')],cwd=W,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
record={'pid':p.pid,'log':str(log),'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
(R/'analysis/remote-qwen3b-process.json').write_text(json.dumps(record,indent=2));print(json.dumps(record))
