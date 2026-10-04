from pathlib import Path
import json,os,re,shutil,subprocess,signal
R=Path(__file__).resolve().parents[1]
BASE=R/'runtime/base'
def build_runtime():
 if (BASE/'usr/bin/python3').exists():return
 (BASE/'usr/bin').mkdir(parents=True,exist_ok=True)
 shutil.copy2('/usr/bin/python3',BASE/'usr/bin/python3')
 shutil.copytree('/usr/lib/python3.12',BASE/'usr/lib/python3.12',ignore=shutil.ignore_patterns('__pycache__','test','tests','ensurepip','dist-packages'))
 files=[Path('/usr/bin/python3')]+list(Path('/usr/lib/python3.12/lib-dynload').glob('*.so'))
 for f in files:
  output=subprocess.run(['ldd',str(f)],capture_output=True,text=True).stdout
  for value in re.findall(r'(/[^\s()]+)',output):
   p=Path(value)
   if p.is_file():
    dst=BASE/str(p).lstrip('/');dst.parent.mkdir(parents=True,exist_ok=True)
    if not dst.exists():shutil.copy2(p,dst)
 for p in BASE.rglob('*'):
  if p.is_dir():p.chmod(0o755)
  else:p.chmod(0o755 if '/bin/' in str(p) or p.name.startswith('ld-linux') else 0o644)
def create(root,initial):
 if not root.exists():shutil.copytree(BASE,root)
 work=root/'work'
 if work.exists():shutil.rmtree(work)
 shutil.copytree(initial,work)
 for p in [work]+list(work.rglob('*')):
  os.chown(p,65534,65534);p.chmod(0o755 if p.is_dir() or p.name.startswith('ld-linux') else 0o644)
 return work
def execute(root,code,workspace_imports=True):
 # The child can only see its chroot and cannot create network sockets or processes.
 if workspace_imports:code='import sys;sys.path.insert(0,"/work")\n'+code
 proc=subprocess.Popen([str(R/'runtime/jail'),str(root.resolve()),code],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True)
 try:out,err=proc.communicate(timeout=12)
 except subprocess.TimeoutExpired:
  os.killpg(proc.pid,signal.SIGKILL);out,err=proc.communicate();return dict(returncode=-9,stdout=out[:12000],stderr=err[:12000],timeout=True)
 return dict(returncode=proc.returncode,stdout=out[:12000],stderr=err[:12000],timeout=False)
def safe_path(work,name):
 p=Path(name)
 if p.is_absolute() or '..' in p.parts:raise ValueError('Path must be relative to workspace')
 target=work/p
 if not target.resolve().is_relative_to(work.resolve()):raise ValueError('Path escapes workspace')
 return target
if __name__=='__main__':
 build_runtime();initial=R/'runtime/smoke-input';initial.mkdir(exist_ok=True);(initial/'hello.txt').write_text('ok')
 root=R/'runtime/smoke-jail'
 if root.exists():shutil.rmtree(root)
 create(root,initial)
 tests={'basic':"import json,csv,sqlite3,unittest;from pathlib import Path;assert Path('hello.txt').read_text()=='ok';Path('out.txt').write_text('pass');print('PASS')",'outside':"from pathlib import Path; print(Path('/etc/passwd').read_text())",'network':"import socket;socket.socket()",'process':"import subprocess;subprocess.run(['/usr/bin/python3','-c','print(1)'])",'runtime_write':"open('/usr/bin/python3','w')"}
 results={k:execute(root,v) for k,v in tests.items()}
 assert results['basic']['returncode']==0,results
 assert all(results[k]['returncode']!=0 for k in tests if k!='basic'),results
 (R/'analysis/sandbox-check.json').write_text(json.dumps(results,indent=2));print('Sandbox isolation checks passed')
