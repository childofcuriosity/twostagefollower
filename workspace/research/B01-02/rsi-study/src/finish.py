import time,subprocess,sys,json
from common import ROOT
for marker in ['replications','robust','loops','branches','gradients','coverage','length','legacy','timecourse']:
 p=ROOT/f'analysis/{marker}-completed.json'
 while not p.exists():time.sleep(60)
 jobs=json.loads(p.read_text());assert all(j['returncode']==0 for j in jobs),marker
for script in ['analyze_robust.py','analyze_loops.py','infer.py','analyze_coverage.py','analyze_length.py','analyze_timecourse.py','curriculum.py','export_tables.py','verify.py','report.py']:
 subprocess.run([sys.executable,str(ROOT/'src'/script)],check=True)
project=ROOT.parents[3];analysispython=project/'.analysis-venv/bin/python'
subprocess.run([str(analysispython),str(ROOT/'src/plots.py')],check=True)
(ROOT/'analysis/PIPELINE_COMPLETE.json').write_text(json.dumps({'status':'analysis_complete_manual_report_review_required','utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}))
