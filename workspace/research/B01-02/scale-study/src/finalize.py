from pathlib import Path
import sys,time,json,subprocess
R=Path(__file__).resolve().parents[1]
markers=[R/'analysis/ANALYSIS_COMPLETE.json']+[R/f'extended/{m}/completed.json' for m in ['qwen1.5b','qwen3b','qwen7b','qwen32b']]
print('Waiting for main analysis and all independent confirmation evaluations',flush=True)
while not all(p.exists() for p in markers):time.sleep(60)
for p in markers[1:]:assert len(json.loads(p.read_text()))==7
for file in ['analyze.py','inference.py','report.py']:subprocess.run([sys.executable,str(R/'src'/file)],check=True)
(R/'analysis/REVIEW_READY.json').write_text(json.dumps({'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'status':'all_primary_and_confirmation_data_ready_manual_review_required'},indent=2));print('REVIEW READY; goal not automatically completed',flush=True)
