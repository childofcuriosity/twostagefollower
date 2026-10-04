import argparse,sys,os
from common import *
ap=argparse.ArgumentParser();ap.add_argument('--model',required=True);ap.add_argument('--condition',required=True);ap.add_argument('--seed',type=int,required=True);a=ap.parse_args()
r=ROOT/'replications'/a.model;r.mkdir(parents=True,exist_ok=True)
for name,path in [('model',model_path(a.model)),('data',PARENT/'data')]:
 p=r/name
 if not p.exists():
  try:p.symlink_to(os.path.relpath(path,r),target_is_directory=True)
  except FileExistsError:pass
(r/'runs').mkdir(exist_ok=True)
import run
run.ROOT=r
sys.argv=['run.py','--condition',a.condition,'--seed',str(a.seed),'--steps','512']
run.main()
