"""Low-frequency completion watcher; audits after all registered jobs finish."""
import json,os,subprocess,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];tags=['formal-local32']+['formal-worker%02d'%i for i in range(1,7)]
while True:
 files=[R/'analysis'/f'{tag}-completed.json' for tag in tags]
 existing=[p for p in files if p.exists()]
 failed=[]
 for p in existing:
  d=json.loads(p.read_text());failed.extend((p.name,r) for r in d['records'] if r['status']!='complete')
 state=dict(pid=os.getpid(),checked=time.time(),completed_hosts=len(existing),expected_hosts=len(tags),failed=failed)
 (R/'analysis/supervisor-state.json').write_text(json.dumps(state,indent=2))
 if len(existing)==len(files):break
 time.sleep(900)
if failed:
 (R/'analysis/SUPERVISOR_NEEDS_REPAIR.json').write_text(json.dumps(state,indent=2));raise SystemExit('Some jobs failed; preserve all outputs and request agent repair; no false completion')
for script in ['audit_results.py','token_replay.py','diagnostics.py','compare.py','report.py','completion_audit.py']:
 p=subprocess.run([sys.executable,str(R/'src'/script)])
 if p.returncode:
  (R/'analysis/SUPERVISOR_NEEDS_REPAIR.json').write_text(json.dumps({'script':script,'returncode':p.returncode,'time':time.time()},indent=2));raise SystemExit(p.returncode)
(R/'analysis/supervisor-complete.json').write_text(json.dumps({'finished':time.time(),'note':'Automated evidence audit complete; research interpretation and agent/user review still required.'},indent=2))
