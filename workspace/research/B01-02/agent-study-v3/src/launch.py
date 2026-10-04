from pathlib import Path
import json,os,random,subprocess,sys,time
R=Path(__file__).resolve().parents[1]
def save(name,value):(R/'analysis'/name).write_text(json.dumps(value,indent=2))
def spawn(tag,jobs,gpu,seconds):
 p=R/'analysis'/f'{tag}-jobs.json';p.write_text(json.dumps(jobs,indent=2));log=(R/'logs'/f'{tag}.log').open('w');env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu)
 proc=subprocess.Popen([sys.executable,'-u',str(R/'src/agent.py'),'--jobs',str(p),'--tag',tag,'--wall-seconds',str(seconds)],stdout=log,stderr=subprocess.STDOUT,env=env)
 return dict(tag=tag,proc=proc,gpu=gpu,start=time.time(),log=log)
print('Waiting for registered preflight',flush=True)
while not (R/'analysis/registration.json').exists():time.sleep(15)
assert json.loads((R/'analysis/preflight.json').read_text())['workspace_import_pass']
cal=spawn('calibration',json.loads((R/'analysis/calibration-jobs.json').read_text()),0,900)
save('running-processes.json',[dict(tag=cal['tag'],pid=cal['proc'].pid,gpu=0)])
try:code=cal['proc'].wait(timeout=1020)
except subprocess.TimeoutExpired:cal['proc'].terminate();code=cal['proc'].wait(timeout=30)
cal['log'].close();save('calibration-process.json',dict(returncode=code,wall_seconds=time.time()-cal['start'],pid=cal['proc'].pid))
assert code==0
result=json.loads((R/'analysis/calibration-completed.json').read_text())
if result['jobs_completed']!=3 or any(x['category']!='complete' for x in result['results']):
 save('CALIBRATION_FAILED.json',result);sys.exit(2)
print('3/3 multi-requirement capability checks passed; starting96',flush=True)
manifest=json.loads((R/'analysis/task-manifest.json').read_text());jobs=[(t,c) for t in manifest['main_ids'] for c in ['plan','reminder','identity','todo']];random.Random(20260925).shuffle(jobs);save('main-order.json',jobs)
workers=[spawn(f'main-{i}',jobs[i::4],i,3600) for i in range(4)];save('running-processes.json',[dict(tag=w['tag'],pid=w['proc'].pid,gpu=w['gpu']) for w in workers])
while any(w['proc'].poll() is None for w in workers):
 for w in workers:
  if w['proc'].poll() is None and time.time()-w['start']>3720:w['proc'].terminate()
 time.sleep(60)
records=[]
for w in workers:
 w['log'].close();p=R/'analysis'/f"{w['tag']}-completed.json";seconds=json.loads(p.read_text())['seconds'] if p.exists() else time.time()-w['start'];records.append(dict(tag=w['tag'],pid=w['proc'].pid,returncode=w['proc'].returncode,wall_seconds=seconds,gpu=w['gpu']))
save('main-processes.json',records);subprocess.run([sys.executable,str(R/'src/analyze.py')],check=True)
print('Compatibility follow-up finished; audit required',flush=True)
