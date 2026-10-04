"""Deterministic development tasks, independent host-side validators and reference solvers."""
from pathlib import Path
import csv,hashlib,io,json,random,shutil
from sandbox import R,create,execute

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
def make(family,n,seed,tag):
 rng=random.Random(seed);base=R/'tasks'/tag;initial=base/'initial';initial.mkdir(parents=True,exist_ok=False)
 specs=[];required=[]
 if family=='files':
  for i in range(n):
   name=f'configs/service_{i+1:02d}.json';env=rng.choice(['prod','stage']);retry=rng.randrange(2,7);timeout=rng.randrange(30,90)
   old={'name':f'service_{i+1:02d}','owner':f'team-{seed%7}','enabled':False,'environment':'dev','retries':rng.randrange(0,2),'timeout_seconds':10,'metadata':{'ticket':seed*100+i,'keep':True}}
   dump(initial/name,old);specs.append(dict(path=name,environment=env,retries=retry,timeout_seconds=timeout))
   required.append(f'T{i+1:02d}: In {name}, set enabled=true, environment="{env}", retries={retry}, timeout_seconds={timeout}. Preserve every other key and value.')
 elif family=='data':
  rates={f'P{i}':rng.randrange(5,31) for i in range(6)}
  rows=[{'id':j+1,'region':rng.choice(['north','south','east','west']),'product':rng.choice(list(rates)),'quantity':rng.randrange(1,10),'status':rng.choice(['paid','paid','cancelled'])} for j in range(60)]
  for name,records in [('orders.csv',rows),('prices.csv',[{'product':p,'unit_price':v} for p,v in rates.items()])]:
   with (initial/name).open('w') as f:w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
  for i in range(n):
   region=['north','south','east','west'][i%4];q=1+(i//4)*2+rng.randrange(2);name=f'reports/report_{i+1:02d}.json';specs.append(dict(path=name,region=region,min_quantity=q))
   required.append(f'T{i+1:02d}: Write {name}: use paid orders for region {region} with quantity >= {q}; join prices by product. JSON keys must be row_ids (ascending order IDs), total_quantity, total_value (sum quantity * unit_price). Empty groups use []/0/0. Read source CSVs; do not modify them.')
 elif family=='code':
  (initial/'jobs').mkdir();(initial/'jobs/__init__.py').write_text('')
  for i in range(n):
   name=f'jobs/task_{i+1:02d}.py';q=rng.randrange(1,9);factor=rng.randrange(2,8);region=rng.choice(['north','south','east','west'])
   (initial/name).write_text('def summarize(records):\n    raise NotImplementedError("TODO")\n')
   specs.append(dict(path=name,region=region,min_quantity=q,factor=factor))
   required.append(f'T{i+1:02d}: Implement summarize(records) in {name}. records is a list of dicts with id(int), region(str), quantity(int), status(str). Keep status=="paid", region=="{region}", quantity>={q}. Return exactly {{"row_ids": sorted kept IDs, "score": sum(quantity * {factor})}}. Empty input/no matches returns {{"row_ids": [], "score": 0}}. Do not mutate input. Must work on unseen records, not only an example.')
 else:raise ValueError(family)
 (initial/'README.txt').write_text('Task workspace. All requirements are in the user request. Python 3 standard library is available.\n')
 protected={str(p.relative_to(initial)):sha(p) for p in initial.rglob('*') if p.is_file() and (p.name=='README.txt' or family=='data' or p.name=='__init__.py')}
 if family=='data':
  required.insert(0,'Input files are orders.csv and prices.csv at workspace root. orders.csv headers: id,region,product,quantity,status. prices.csv headers: product,unit_price. Each report is ONE aggregate JSON object with exactly three keys: {"row_ids": [1, 2], "total_quantity": 0, "total_value": 0}. These example values are placeholders, not answers. Do not return a mapping from order IDs to records. Calculate the fields from the selected paid rows. Create output directories if needed.')
 meta=dict(id=tag,family=family,n_requirements=n,seed=seed,specs=specs,protected=protected,requirements=required,user='Complete ALL items below in this workspace. You may batch operations in Python. Inspect and verify your work; finish only when all requested outputs are correct. Do not request extra user input: all necessary inputs are available.\n'+'\n'.join(required))
 dump(base/'task.json',meta);return meta

def expected_data(initial,s):
 with (initial/'orders.csv').open() as f:rows=list(csv.DictReader(f))
 with (initial/'prices.csv').open() as f:prices={x['product']:int(x['unit_price']) for x in csv.DictReader(f)}
 rows=[x for x in rows if x['status']=='paid' and x['region']==s['region'] and int(x['quantity'])>=s['min_quantity']]
 return dict(row_ids=sorted(int(x['id']) for x in rows),total_quantity=sum(int(x['quantity']) for x in rows),total_value=sum(int(x['quantity'])*prices[x['product']] for x in rows))

def cases(seed):
 rng=random.Random(seed+9382);return [[],[{'id':i+1,'region':rng.choice(['north','south','east','west']),'quantity':rng.randrange(0,15),'status':rng.choice(['paid','cancelled'])} for i in range(100)], [{'id':j+1,'region':region,'quantity':q,'status':status} for j,(region,q,status) in enumerate((r,q,s) for r in ['north','south','east','west'] for q in range(0,12) for s in ['paid','cancelled'])]]

def grade(meta,root):
 work=root/'work';initial=R/'tasks'/meta['id']/'initial';checks=[]
 protected=all((work/p).is_file() and sha(work/p)==h for p,h in meta['protected'].items())
 for s in meta['specs']:
  p=work/s['path'];detail='';ok=False
  try:
   if meta['family']=='files':
    expected=json.loads((initial/s['path']).read_text());expected.update({k:s[k] for k in ['environment','retries','timeout_seconds']});expected['enabled']=True;ok=json.loads(p.read_text())==expected
   elif meta['family']=='data':ok=json.loads(p.read_text())==expected_data(initial,s)
   else:
    inputs=cases(meta['seed']);expected=[]
    for rows in inputs:
     kept=[r for r in rows if r['status']=='paid' and r['region']==s['region'] and r['quantity']>=s['min_quantity']]
     expected.append({'value':{'row_ids':sorted(r['id'] for r in kept),'score':sum(r['quantity']*s['factor'] for r in kept)},'unchanged':True})
    # Agent code executes only in the jail; expected results remain in host validator.
    code='import importlib.util,json,copy\nspec=importlib.util.spec_from_file_location("candidate",'+repr(s['path'])+')\nm=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)\ninputs='+repr(inputs)+'\nout=[]\nfor rows in inputs:\n before=copy.deepcopy(rows);value=m.summarize(rows);out.append({"value":value,"unchanged":rows==before})\nprint(json.dumps(out))'
    result=execute(root,code);ok=result['returncode']==0 and json.loads(result['stdout'])==expected;detail=result['stderr'][:300]
  except Exception as ex:detail=type(ex).__name__+': '+str(ex)[:200]
  checks.append(dict(id=f'T{len(checks)+1:02d}',passed=bool(ok),detail=detail))
 return dict(complete=protected and all(x['passed'] for x in checks),completed_requirements=sum(x['passed'] for x in checks),total_requirements=len(checks),protected_inputs_unchanged=protected,checks=checks)

def reference(meta,work):
 initial=R/'tasks'/meta['id']/'initial'
 for s in meta['specs']:
  p=work/s['path']
  if meta['family']=='files':
   x=json.loads((initial/s['path']).read_text());x.update({k:s[k] for k in ['environment','retries','timeout_seconds']});x['enabled']=True;dump(p,x)
  elif meta['family']=='data':dump(p,expected_data(initial,s))
  else:p.write_text(f'def summarize(records):\n    kept = [r for r in records if r["status"] == "paid" and r["region"] == {s["region"]!r} and r["quantity"] >= {s["min_quantity"]}]\n    return {{"row_ids": sorted(r["id"] for r in kept), "score": sum(r["quantity"] * {s["factor"]} for r in kept)}}\n')

def build():
 metas=[]
 for family in ['files','data','code']:
  for n in [4,12]:
   for seed in range(4):metas.append(make(family,n,20260925+seed,f'{family}-n{n:02d}-s{seed}-v2'))
 for family in ['files','data','code']:
  for seed in range(2,4):make(family,1,9025+seed,f'cal-{family}-s{seed}')
 dump(R/'analysis/task-manifest.json',dict(main_ids=[x['id'] for x in metas],main_count=24,calibration_ids=[f'cal-{f}-s{s}' for f in ['files','data','code'] for s in range(2,4)],note='Development smoke only; three generator families, not 24 independent task templates. 4/12 requirements do not force a tool-call count.'))

def validate():
 results=[]
 manifest=json.loads((R/'analysis/task-manifest.json').read_text());ids=set(manifest['main_ids']+manifest['calibration_ids'])
 for p in sorted((R/'tasks').glob('*/task.json')):
  if p.parent.name not in ids:continue
  meta=json.loads(p.read_text());root=R/'runtime/reference-jail';work=create(root,p.parent/'initial');before=grade(meta,root);assert not before['complete']
  reference(meta,work);after=grade(meta,root);assert after['complete'],(meta['id'],after)
  # Every individual omission must fail independently, including last items.
  omissions=[]
  for s in meta['specs']:
   target=work/s['path'];saved=target.read_bytes();target.unlink();g=grade(meta|{'specs':[s]},root);assert not g['complete'] and g['completed_requirements']==0,(meta['id'],s,g);omissions.append(s['path']);target.parent.mkdir(exist_ok=True,parents=True);target.write_bytes(saved)
  results.append(dict(id=meta['id'],reference_pass=True,unsolved_fails=True,omissions_detected=omissions))
 dump(R/'analysis/task-validation-v2.json',results);print('Reference and every-item omission validation passed',len(results),flush=True)
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--validate',action='store_true');a=ap.parse_args()
 if a.validate:validate()
 else:build()
