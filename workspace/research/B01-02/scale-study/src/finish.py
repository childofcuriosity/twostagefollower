from pathlib import Path
import time,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
markers=[ROOT/f'analysis/{m}-checkpoint-tests-completed.json' for m in ['qwen32b','qwen7b']]
print('Waiting for fixed checkpoints, 60s stage checks',flush=True)
while not all(p.exists() for p in markers):time.sleep(60)
for p in markers:
 rs=json.loads(p.read_text());assert len(rs)==6 and all(r['returncode']==0 for r in rs)
subprocess.run([sys.executable,str(ROOT/'src/analyze.py')],check=True)
d=json.loads((ROOT/'analysis/results.json').read_text());assert not d['missing'] and d['final_execution_records']==13440
(ROOT/'analysis/ANALYSIS_COMPLETE.json').write_text(json.dumps({'status':'raw_analysis_complete_manual_interpretation_pending','utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())},indent=2))
print('STAGE4 automated audit done; manual scientific review still required',flush=True)
