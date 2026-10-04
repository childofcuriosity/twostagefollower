from pathlib import Path
import json,os,random,subprocess,sys,time
R=Path(__file__).resolve().parents[1]
def write(name,x):(R/'analysis'/name).write_text(json.dumps(x,indent=2))
def start(tag,jobs,gpu,seconds):
 p=R/'analysis'/f'{tag}-jobs.json';p.write_text(json.dumps(jobs,indent=2));log=(R/'logs'/f'{tag}.log').open('w')
 env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu)
 proc=subprocess.Popen([sys.executable,'-u',str(R/'src/agent.py'),'--jobs',str(p),'--tag',tag,'--wall-seconds',str(seconds)],env=env,stdout=log,stderr=subprocess.STDOUT)
 return dict(tag=tag,proc=proc,start=time.time(),gpu=gpu,jobs=jobs,log=log)
def wait(record,cap):
 try:code=record['proc'].wait(timeout=cap+120)
 except subprocess.TimeoutExpired:record['proc'].terminate();code=record['proc'].wait(timeout=30)
 record['log'].close();return dict(tag=record['tag'],pid=record['proc'].pid,returncode=code,wall_seconds=time.time()-record['start'],gpu=record['gpu'])
print('Waiting for validated reference solutions and omission checks',flush=True)
while not (R/'analysis/task-validation-v2.json').exists():
 try:os.kill(int(os.environ['AGENT_VALIDATION_PID']),0)
 except ProcessLookupError:raise RuntimeError('Validation process ended without success; inspect task-validation.log')
 time.sleep(15)
validation=json.loads((R/'analysis/task-validation-v2.json').read_text());assert len(validation)==30 and all(x['reference_pass'] for x in validation)
manifest=json.loads((R/'analysis/task-manifest.json').read_text())
cal=start('calibration-v2',[(x,'plan') for x in manifest['calibration_ids']],0,1800)
write('running-processes.json',[dict(tag=cal['tag'],pid=cal['proc'].pid,gpu=0)])
record=wait(cal,1800);write('calibration-v2-process.json',record)
if record['returncode']!=0:raise RuntimeError('Calibration worker failed')
summary=json.loads((R/'analysis/calibration-v2-completed.json').read_text())
if summary['jobs_completed']!=6 or any(x['category']!='complete' for x in summary['results']):
 write('CALIBRATION_V2_FAILED.json',dict(reason='Below registered6/6 single-task capability threshold; main96 not started',summary=summary));sys.exit(2)
print('Calibration6/6 passed; launching registered96 trajectories',flush=True)
jobs=[(task,c) for task in manifest['main_ids'] for c in ['plan','reminder','identity','todo']]
random.Random(20260925).shuffle(jobs);write('main-order.json',jobs)
workers=[start(f'main-{i}',jobs[i::4],i,5400) for i in range(4)]
write('running-processes.json',[dict(tag=w['tag'],pid=w['proc'].pid,gpu=w['gpu']) for w in workers])
# Check at long intervals; budget watchdog, not intervention in agent behavior.
while any(w['proc'].poll() is None for w in workers):
 for w in workers:
  if w['proc'].poll() is None and time.time()-w['start']>5520:w['proc'].terminate()
 time.sleep(60)
records=[]
for w in workers:
 records.append(dict(tag=w['tag'],pid=w['proc'].pid,returncode=w['proc'].returncode,wall_seconds=json.loads((R/'analysis'/f"{w['tag']}-completed.json").read_text())['seconds'] if (R/'analysis'/f"{w['tag']}-completed.json").exists() else time.time()-w['start'],gpu=w['gpu']));w['log'].close()
write('main-processes.json',records)
subprocess.run([sys.executable,str(R/'src/analyze.py')],check=True)
print('Main runs ended; manual evidence review still required',flush=True)
