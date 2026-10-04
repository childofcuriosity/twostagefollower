import argparse,json,os,subprocess
from pathlib import Path
PROJECT=Path(__file__).resolve().parents[5]
PRIVATE=PROJECT/'.config/private-servers'
def execute(server,cmd,timeout=90):
 conf=json.loads((PRIVATE/'grpo-binary.json').read_text())[server]
 env=dict(os.environ,GRPO_SERVER_KEY=server,SSH_ASKPASS=str(PRIVATE/'grpo-askpass.py'),SSH_ASKPASS_REQUIRE='force',DISPLAY=':0')
 args=['ssh','-p',str(conf['port']),'-o','StrictHostKeyChecking=no','-o','UserKnownHostsFile=/dev/null','-o','ConnectTimeout=15','-o','NumberOfPasswordPrompts=1','-o','PreferredAuthentications=password',conf['user']+'@'+conf['host'],cmd]
 return subprocess.run(args,env=env,stdin=subprocess.DEVNULL,capture_output=True,text=True,timeout=timeout)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('server');p.add_argument('cmd');a=p.parse_args();r=execute(a.server,a.cmd);print(r.stdout,end='');print(r.stderr,end='');raise SystemExit(r.returncode)
