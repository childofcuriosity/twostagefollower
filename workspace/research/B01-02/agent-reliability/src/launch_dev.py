from pathlib import Path
import os,subprocess,time,json
R=Path(__file__).resolve().parents[1]
# Refuse inference unless independent preflight completed.
for _ in range(40):
 if (R/'analysis/preflight.json').exists():break
 time.sleep(15)
assert (R/'analysis/preflight.json').exists(), 'Preflight did not pass within 10 minutes'
workers=[]
for gpu,mode in enumerate(['zero','fewshot']):
 tag='dev-'+mode;env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu)
 log=(R/'logs'/f'{tag}.log').open('w')
 p=subprocess.Popen([os.sys.executable,str(R/'src/native.py'),'--jobs',str(R/'queues/dev.json'),'--tag',tag,'--mode',mode],env=env,stdout=log,stderr=subprocess.STDOUT)
 workers.append((tag,p,log))
(R/'analysis/dev-pids.json').write_text(json.dumps({tag:p.pid for tag,p,_ in workers}))
exitcodes={}
for tag,p,log in workers:exitcodes[tag]=p.wait();log.close()
(R/'analysis/dev-launch-completed.json').write_text(json.dumps(exitcodes));assert all(x==0 for x in exitcodes.values()),exitcodes
