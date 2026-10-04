from common import *
import argparse,time
p=argparse.ArgumentParser();p.add_argument('--final',action='store_true');a=p.parse_args()
base=[2,5,10,15,20,30,40]
rates={}
for f in (R/'analysis').glob('scores-explore-L*.json'):
 x=json.loads(f.read_text());rates[x['length']]=x['results']['STEP']['rate']
assert all(L in rates for L in base)
extra=[]
if rates[40]>.9:extra=[L for L in [50,60] if L not in rates]
if extra:
 print(json.dumps(dict(action='supplement',lengths=extra,step_rates=rates)));raise SystemExit(0)
# The registered maximum is two intermediate additions, total, rather than recursive refinement.
record=R/'analysis/intermediate-lengths.json'
if record.exists():intermediate=json.loads(record.read_text())['lengths']
else:
 intermediate=[]
 observed=sorted(rates)
 for lo,hi in zip(observed,observed[1:]):
  if rates[lo]>.9 and rates[hi]<.2:
   intermediate=sorted({int(lo+(hi-lo)*k/3+.5) for k in (1,2)}-{lo,hi});break
 write(record,dict(lengths=intermediate,step_rates=rates))
extra+= [L for L in intermediate if L not in rates]
if extra:
 print(json.dumps(dict(action='supplement',lengths=extra,step_rates=rates)));raise SystemExit(0)
eligible=sorted(L for L,r in rates.items() if .2<=r<=.9)
selected=sorted(set([eligible[0],eligible[-1]])) if eligible else [min(rates,key=lambda L:(abs(rates[L]-.5),L))]
result=dict(action='formal',lengths=selected,step_rates=rates,eligible=eligible,fallback=not bool(eligible),selection_uses='STEP only',selected_at=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
if a.final:write(R/'analysis/length-selection.json',result)
print(json.dumps(result))
