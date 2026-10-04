import json,subprocess,sys,time,traceback
from pathlib import Path
p=Path(sys.argv[1]);job=json.loads(p.read_text());begin=time.time()
try:
 result=subprocess.run(['bash','-lc',job['command']]);record=dict(returncode=result.returncode,seconds=time.time()-begin,finished=time.time())
except BaseException:
 record=dict(returncode=-1,seconds=time.time()-begin,error=traceback.format_exc(),finished=time.time())
p.with_suffix(p.suffix+'.exit.json').write_text(json.dumps(record,indent=2)+'\n');raise SystemExit(record['returncode'])
