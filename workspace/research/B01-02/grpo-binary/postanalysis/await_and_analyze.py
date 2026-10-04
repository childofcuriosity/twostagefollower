"""Wait for the existing computation supervisor; never starts or restarts model jobs."""
import json,subprocess,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1]
while not (R/'analysis/computation-complete.json').exists():
 time.sleep(30)
for name in ['analyze.py','report.py']:
 print('RUN',name,flush=True);subprocess.run([sys.executable,str(R/'postanalysis'/name)],check=True)
(R/'analysis/analysis-complete.json').write_text(json.dumps(dict(finished=time.time(),human_readable_report=str(R/'REPORT.md'),final_interpretation_and_resource_audit_pending=True),indent=2)+'\n')
print('ANALYSIS_COMPLETE',flush=True)
