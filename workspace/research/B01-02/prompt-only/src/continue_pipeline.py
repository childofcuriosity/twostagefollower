"""Stage completion orchestration; hardware inspections remain hourly in dispatch."""
from common import *
import os,shutil,subprocess,sys,time,traceback
BASE=R
base_lengths=[2,5,10,15,20,30,40]
def run(root,script,*args):
 cmd=[sys.executable,str(root/'src'/script),*map(str,args)]
 print('COMMAND',cmd,flush=True);subprocess.run(cmd,check=True)
def scores_ready(root):return all((root/f'analysis/scores-explore-L{L}.json').exists() for L in base_lengths)
def rate(root,L):return json.loads((root/f'analysis/scores-explore-L{L}.json').read_text())['results']['STEP']['rate']
try:
 # The already-launched 7B dispatcher owns these runs; never duplicate them.
 while not scores_ready(BASE):
  failed=[]
  for f in (BASE/'analysis').glob('dispatch-explore-*.json'):
   d=json.loads(f.read_text());failed.extend(x for x in d['results'] if x['returncode'])
  if failed:raise RuntimeError(f'7B exploration failed: {failed}')
  time.sleep(20)
 root=BASE
 if rate(BASE,2)<.2 and rate(BASE,5)<.2:
  diagnosis=json.loads((BASE/'analysis/precheck-diagnosis.json').read_text());assert diagnosis['ends'].get('length',0)==0
  write(BASE/'analysis/fallback-decision.json',dict(reason='Both L2 and L5 STEP below20%; independent precheck and raw-response diagnosis found arithmetic/expansion errors, no implementation or generation-budget defect. Activate user-authorized 14B fallback; no Prompt change.',step_L2=rate(BASE,2),step_L5=rate(BASE,5),time=time.time(),not_independent_cross_model_replication=True))
  root=BASE/'fallback14';root.mkdir(exist_ok=True)
  for d in ['src','data','analysis','runs','logs','prompts']:(root/d).mkdir(exist_ok=True)
  # Separate immutable attempt; only model and output-root references differ.
  for f in (BASE/'src').glob('*.py'):
   if f.name=='continue_pipeline.py':continue
   shutil.copy2(f,root/'src'/f.name)
  s=(root/'src/common.py').read_text().replace('B=R.parent\n','B=R.parent.parent\n').replace("MODEL=R/'models/qwen7b'","MODEL=R.parent/'models/qwen14b'")
  (root/'src/common.py').write_text(s)
  shutil.copy2(BASE/'REGISTRATION.md',root/'REGISTRATION.md')
  (root/'FALLBACK.md').write_text('User-authorized fallback from 7B due to short-task floor. Prompt unchanged. Data generation rules and seeds unchanged; 14B repeats the same flow. 7B evidence remains in parent directory. This is model selection, not an independent cross-model confirmation.\n')
  if not (BASE/'models/qwen14b/download-manifest.json').exists():run(BASE,'download.py','--repo','Qwen/Qwen2.5-14B-Instruct','--name','qwen14b')
  run(root,'validate.py')
  run(root,'prepare.py','--phase','precheck','--lengths',2,5,10)
  run(root,'dispatch.py','--phase','precheck','--lengths',2,5,10,'--batch',4)
  # No tuning based on precheck accuracy. Same already-validated definitions and scorer.
  run(root,'prepare.py','--phase','explore','--lengths',*base_lengths)
  run(root,'dispatch.py','--phase','explore','--lengths',*base_lengths,'--conditions','STEP','NAME','--batch',32)
 while True:
  output=subprocess.check_output([sys.executable,str(root/'src/select.py')],text=True);decision=json.loads(output)
  print('SELECTION',decision,flush=True)
  if decision['action']=='formal':break
  lengths=decision['lengths']
  run(root,'prepare.py','--phase','explore','--lengths',*lengths)
  run(root,'dispatch.py','--phase','explore','--lengths',*lengths,'--conditions','STEP','NAME','--batch',32)
 run(root,'select.py','--final')
 lengths=json.loads((root/'analysis/length-selection.json').read_text())['lengths']
 frozen=root/'frozen-source';frozen.mkdir(exist_ok=True)
 for f in (root/'src').glob('*.py'):shutil.copy2(f,frozen/f.name)
 run(root,'prepare.py','--phase','formal','--lengths',*lengths)
 write(BASE/'analysis/active-formal.json',dict(root=str(root),lengths=lengths,started=time.time(),model='14B' if root!=BASE else '7B'))
 run(root,'dispatch.py','--phase','formal','--lengths',*lengths,'--batch',32)
 run(root,'report.py')
 write(BASE/'analysis/pipeline-complete.json',dict(root=str(root),lengths=lengths,report=str(root/'REPORT.md'),time=time.time(),requires_final_research_review=True))
 print('PIPELINE_COMPLETE',root,flush=True)
except BaseException:
 (BASE/'logs/pipeline-failure.txt').write_text(traceback.format_exc());raise
