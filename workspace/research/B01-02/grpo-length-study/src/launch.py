import argparse,json,os,subprocess,time,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT.parents[3]
p=argparse.ArgumentParser();p.add_argument('--job',required=True);a=p.parse_args();job=json.loads(Path(a.job).read_text())
log=Path(job['log']);log.parent.mkdir(parents=True,exist_ok=True)
with log.open('a') as f:
 proc=subprocess.Popen([sys.executable,str(ROOT/'src/job_runner.py'),str(Path(a.job).resolve())],cwd=PROJECT,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True)
state=dict(pid=proc.pid,started=time.time(),job=a.job,host=os.uname().nodename)
Path(a.job+'.launched.json').write_text(json.dumps(state,indent=2)+'\n');print(json.dumps(state))
