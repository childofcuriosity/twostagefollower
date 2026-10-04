"""Account for measured job durations without treating allocated time as kernel activity."""
import json,time
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
records=[];unmeasured=[]
for p in (R/'infrastructure').glob('*.json'):
 if p.name.endswith(('.exit.json','.launched.json')):continue
 j=read(p);cmd=j.get('command','');exitfile=p.with_suffix(p.suffix+'.exit.json')
 if 'src/train.py' in cmd:kind='precheck' if '--precheck' in cmd else 'formal_training';ngpu=2
 elif 'src/evaluate.py' in cmd:kind='evaluation_worker';ngpu=1
 else:continue
 if not exitfile.exists():
  assert p.name in ['precheck-remote65.json','precheck-remote70.json'],f'Job not exited: {p}'
  assert 'ambiguous option: --run' in Path(j['log']).read_text()
  unmeasured.append(dict(job=p.name,reason='Initial launcher predates exit recorder; torchrun argument parsing failed before train.py executed; duration not recorded.'))
  continue
 ex=read(exitfile);records.append(dict(job=p.name,kind=kind,returncode=ex['returncode'],seconds=ex['seconds'],allocated_gpu_seconds=ngpu*ex['seconds'],includes_initialization_and_idle=True))
summary={kind:sum(x['allocated_gpu_seconds'] for x in records if x['kind']==kind)/3600 for kind in ['precheck','formal_training','evaluation_worker']}
evals=[read(p) for p in (R/'eval/outputs').glob('*/complete.json')]
summary['evaluation_task_wall_gpu_hours']=sum(x['wall_seconds'] for x in evals)/3600
summary['evaluation_generate_gpu_hours']=sum(x['generate_seconds'] for x in evals)/3600
out=dict(finished=time.time(),jobs=records,unmeasured_startup_failures=unmeasured,gpu_hours=summary,evaluation_output_tokens=sum(x['generated_tokens'] for x in evals),notes=['Allocated GPU seconds = assigned device count times launcher job wall duration, including initialization, saving, idle waits; not GPU kernel active time.', 'Only jobs with measured exit durations are summed; two initial argument-parser failures lack duration and are separately listed.', 'Short infrastructure probes, data building and CPU analysis are outside these model-job timings.', 'Evaluation worker totals include waiting for checkpoints; task and generate time separately reported.'])
(R/'analysis/cost-audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(summary,indent=2))
