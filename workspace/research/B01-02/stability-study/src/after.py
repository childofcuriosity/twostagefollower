"""Low-frequency postprocessor; does not declare the research goal complete."""
import json,subprocess,sys,time,os
from common import R,write
write(R/'analysis/postprocessor-launch.json',dict(pid=os.getpid(),started=time.time()))
while not (R/'analysis/pipeline-complete.json').exists():
    if (R/'analysis/pipeline-failed.json').exists():raise SystemExit('Pipeline needs repair; no postprocessing success claimed')
    time.sleep(900)
for script in ['compare.py','attribution.py','plots.py']:
    python=str(R.parents[3]/'.analysis-venv/bin/python') if script=='plots.py' else sys.executable
    p=subprocess.run([python,str(R/'src'/script)])
    if p.returncode:raise SystemExit(p.returncode)
write(R/'analysis/postprocessor-complete.json',dict(finished=time.time(),note='Agent still must review evidence, determine necessary mechanism followup and finish delivery.'))
