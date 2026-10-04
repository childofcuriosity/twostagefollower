"""Oracle subtask products and same-item joint success, never called end-to-end deployment."""
import collections,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
records={}
for run in (R/'runs').iterdir():
 if not (run/'evaluation-complete.json').exists():continue
 args=json.loads((run/'config.json').read_text())['args']
 for p in run.glob('evaluation-*-independent.jsonl'):
  for r in map(json.loads,p.read_text().splitlines()):records[args['model'],args['condition'],args['seed'],r['mode'],r['id']]=r
rows=[]
for model in ['qwen1.5b','qwen3b','qwen7b','qwen32b']:
 for L in [3,4,5,6,8]:
  ss=[]
  for seed in [11,22,33]:
   pairs=[]
   for key,b in records.items():
    if key[:4]!=(model,'order_oracle',seed,'order_oracle') or len(b['chain'])!=L:continue
    a=records.get((model,'operation_oracle',seed,'operation_oracle',key[4]));j=records.get((model,'joint',seed,'joint',key[4]))
    if a is None or j is None:continue
    assert (a['chain'],a['x'])==(b['chain'],b['x'])==(j['chain'],j['x'])
    pairs.append((a['grade']['complete'],b['grade']['complete'],j['grade']['complete']))
   if len(pairs)!=96:continue
   pa=sum(x[0] for x in pairs)/96;pb=sum(x[1] for x in pairs)/96
   ss.append(dict(seed=seed,n=96,A_sequence_specialist=pa,B_execution_specialist=pb,product=pa*pb,both_oracle_tasks_correct=sum(a and b for a,b,j in pairs)/96,joint_autonomous=sum(j for a,b,j in pairs)/96))
  if len(ss)==3:rows.append(dict(model=model,length=L,n=288,seeds=ss,**{k:sum(s[k] for s in ss)/3 for k in ['A_sequence_specialist','B_execution_specialist','product','both_oracle_tasks_correct','joint_autonomous']}))
(R/'analysis/oracle-products.json').write_text(json.dumps(dict(rows=rows,note='Specialist A learns names/Done with actual selected-tool execution provided; specialist B learns execution with correct names supplied. Product per seed. Same-item A&B is observed co-success in two separate oracle evaluations, not a run of a composed agent. Do not treat oracle-token correctness as learned capability.'),indent=2))
lines=['# Two separately trained subtasks and joint execution\n','Independent confirmation set; compute products separately for three seeds, then average. A and B come from different specialist checkpoints. Both subtasks correct on the same example is a paired statistic from two oracle evaluations, not an executed two-model composition. Only cells with all three seeds complete are shown.\n']
for model in ['qwen1.5b','qwen3b','qwen7b','qwen32b']:
 lines+=['\n## '+model,'|Calls|A sequence task|B all-expansions task|A x B|Both subtasks correct on the same example|Joint autonomous execution|','|---|---:|---:|---:|---:|---:|']
 for z in rows:
  if z['model']==model:lines.append('| '+str(z['length'])+' | '+' | '.join(f'{100*z[k]:.2f}%' for k in ['A_sequence_specialist','B_execution_specialist','product','both_oracle_tasks_correct','joint_autonomous'])+' |')
(R/'ORACLE_PRODUCTS.md').write_text('\n'.join(lines));print('Complete model/length cells:',len(rows))
