from pathlib import Path
import json,csv
ROOT=Path(__file__).resolve().parents[1]
for name in ['robust-rows','loop-rows','loop-proposal-rows','coverage-rows']:
 rows=[json.loads(l) for l in (ROOT/f'analysis/{name}.jsonl').read_text().splitlines()]
 fields=sorted({k for r in rows for k in r})
 with (ROOT/f'analysis/{name}.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for r in rows:w.writerow({k:json.dumps(v) if isinstance(v,(list,dict)) else v for k,v in r.items()})
rows=json.loads((ROOT/'analysis/loop-results.json').read_text())['branch_rows']
with (ROOT/'analysis/branch-rows.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=sorted({k for r in rows for k in r}));w.writeheader();w.writerows(rows)
print('CSV tables exported')
