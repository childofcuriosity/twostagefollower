import time,json,subprocess,sys
from common import ROOT
while not (ROOT/'analysis/completed.json').exists():time.sleep(60)
jobs=json.loads((ROOT/'analysis/completed.json').read_text());assert len(jobs)==12 and all(r['returncode']==0 for r in jobs)
for name in ['analyze.py','verify.py']:
 subprocess.run([sys.executable,str(ROOT/'src'/name)],check=True)
(ROOT/'analysis/analysis-completed.json').write_text(json.dumps({'status':'complete','utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}))
