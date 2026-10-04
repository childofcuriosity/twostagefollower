from pathlib import Path
import json,os,subprocess,time
R=Path(__file__).resolve().parents[1]
for name in ['compact-main-batch','controlled-v2-main-batch','controlled-v3-main-batch']:
 p=R/'analysis'/f'{name}-completed.json'
 while not p.exists():time.sleep(60)
 assert all(v==0 for v in json.loads(p.read_text()).values()),name
for script in ['final_audit.py','analyze_native.py','diagnose_native.py','mechanism_audit.py']:
 log=(R/'logs'/f'final-{script}.log').open('w');result=subprocess.run([os.sys.executable,str(R/'src'/script)],stdout=log,stderr=subprocess.STDOUT);log.close();assert result.returncode==0,script
(R/'analysis/evidence-pipeline-completed.json').write_text(json.dumps({'status':'passed','finished_at':time.time()}));print('All evidence checks complete')
