from common import *
import statistics
rows=[];matches=[]
for p in (ROOT/'runs').glob('timecourse-*/summary.json'):
 meta=json.loads(p.read_text());matches.append(dict(seed=meta['seed'],matches_original_final_weights=meta['matches_original_final_weights']))
 for q in p.parent.glob('step*/summary.json'):
  r=json.loads(q.read_text());rows.append(dict(seed=meta['seed'],step=r['step'],iid_accuracy=r['execution']['groups']['iid']['accuracy'],ood_accuracy=r['execution']['groups']['ood']['accuracy'],proposal_compression=statistics.mean(x['compression'] for x in r['proposal'])))
assert len(matches)==3 and len(rows)==18
summary={}
for step in [0,16,64,128,256,512]:
 rs=[r for r in rows if r['step']==step];summary[str(step)]={k:statistics.mean(r[k] for r in rs) for k in ['iid_accuracy','ood_accuracy','proposal_compression']}
(ROOT/'analysis/timecourse-results.json').write_text(json.dumps(dict(posthoc=True,summary=summary,rows=rows,final_weight_matches=matches),indent=2));print(json.dumps(summary,indent=2));print(matches)

import time
while not (ROOT/'analysis/original-gradients-completed.json').exists():time.sleep(60)
assert all(r['returncode']==0 for r in json.loads((ROOT/'analysis/original-gradients-completed.json').read_text()))
