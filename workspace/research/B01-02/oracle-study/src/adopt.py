"""Explicit one-job handoff: queued training waits for a registered external owner."""
import json,os,time
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def argument(argv,key):
 try:return argv[argv.index(key)+1]
 except (ValueError,IndexError):return None

def maybe_adopt(argv):
 if os.environ.get('ORACLE_EXTERNAL_OWNER')=='1':return False
 key=(argument(argv,'--model'),argument(argv,'--condition'),argument(argv,'--seed'))
 if key!=('qwen32b','operation_oracle','33') or '--probe' in argv:return False
 lease=R/'analysis/external-qwen32b-operation_oracle-s33.json'
 if not lease.exists():return False
 d=json.loads(lease.read_text());run=R/'runs'/'qwen32b-operation_oracle-s33';complete=run/'training-complete.json'
 while not complete.exists():
  proc=Path('/proc')/str(d['pid']);cmd=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode() if (proc/'cmdline').exists() else ''
  if 'oracle-study/src/train.py' not in cmd or '--seed 33' not in cmd:raise RuntimeError('Registered external training owner is absent; do not duplicate or overwrite partial results')
  time.sleep(30)
 t=json.loads(complete.read_text());a=t['config']['args'];assert (a['model'],a['condition'],a['seed'],a['microbatch'],t['steps'])==('qwen32b','operation_oracle',33,4,512)
 (R/'analysis/external-adoption-complete.json').write_text(json.dumps({'lease':str(lease),'owner_pid':d['pid'],'adopter_pid':os.getpid(),'training_complete':str(complete),'time':time.time()},indent=2))
 print('Registered training completed by external owner; original queue proceeds to evaluation.',flush=True);return True
