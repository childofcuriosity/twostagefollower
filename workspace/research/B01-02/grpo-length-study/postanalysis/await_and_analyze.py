import json,os,subprocess,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];PROJECT=R.parents[3]
while not (R/'analysis/computation-complete.json').exists():time.sleep(30)
for task in ['7b-L3','7b-L4','7b-L5','14b-L5','14b-L6','14b-L7']:
 env=dict(os.environ,GRPO_TASK_ROOT=str(R/task))
 for script in ['analyze_task.py','report_task.py']:
  print('RUN',task,script,flush=True)
  subprocess.run([str(PROJECT/'.analysis-venv/bin/python'),str(R/'postanalysis'/script)],env=env,check=True)
subprocess.run([str(PROJECT/'.analysis-venv/bin/python'),str(R/'postanalysis/aggregate.py')],check=True)
(R/'analysis/analysis-complete.json').write_text(json.dumps(dict(finished=time.time(),final_interpretation_and_resource_audit_pending=True),indent=2)+'\n')
print('ANALYSIS_COMPLETE',flush=True)
