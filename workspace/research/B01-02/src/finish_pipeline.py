import json,time,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT.parents[2];python=PROJECT/'.training-venv/bin/python'
marker=ROOT/'analysis/core-completed.json'
while not marker.exists():time.sleep(60)
rows=json.loads(marker.read_text())
if any(r['returncode'] for r in rows):raise SystemExit('Core failures require inspection; interventions not started')
subprocess.run([str(python),'-u',str(ROOT/'src/launch_suite.py'),'--phase','intervention','--steps','512','--gpus','0,1,2,3'],check=True)
subprocess.run([str(python),str(ROOT/'src/analyze.py')],check=True)
subprocess.run([str(python),str(ROOT/'src/verify_artifacts.py')],check=True)
(ROOT/'analysis/PIPELINE_COMPLETE.json').write_text(json.dumps({'completed':True,'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'needs_human_readable_report':True},indent=2))
