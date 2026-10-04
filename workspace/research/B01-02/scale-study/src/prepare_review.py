from pathlib import Path
import subprocess,sys,time,json
R=Path(__file__).resolve().parents[1]
while not (R/'analysis/REVIEW_READY.json').exists():time.sleep(60)
subprocess.run([sys.executable,str(R/'src/verify.py')],check=True)
subprocess.run([sys.executable,str(R/'src/mastery_diagnostics.py')],check=True)
subprocess.run([str(R.parents[3]/'.analysis-venv/bin/python'),str(R/'src/plots.py')],check=True)
(R/'analysis/ARTIFACTS_READY.json').write_text(json.dumps({'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'manual_scientific_review_required':True},indent=2));print('Artifacts ready; completion remains subject to manual audit',flush=True)
