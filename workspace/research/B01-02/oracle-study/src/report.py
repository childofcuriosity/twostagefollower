"""Render actual completed/interim oracle results, never invent completion status."""
import collections,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def main():
 audit=json.loads((R/'analysis/results-audit.json').read_text());groups=collections.defaultdict(collections.Counter)
 for x in audit['results']:
  key=(x['model'],x['condition'],x['mode'],x['split'],x['length']);groups[key].update(x['counts'])
 complete_runs=[p.parent.name for p in (R/'runs').glob('*/evaluation-complete.json')]
 lines=['# Second-stage oracle ablation results\n',f'Currently audited: {audit["records"]} outputs; {len(complete_runs)}/36 training jobs and corresponding evaluations have completion markers. See COMPLETION_AUDIT.md for completeness checks. Until counts reach 62400 and 36, this file is an interim result.\n',
 'All models are Qwen2.5 Base, using the same 4096 training examples, LoRA configuration, 512 steps, and three seeds. The three conditions see identical text and differ only in loss masks, sharing the EndTool/Done protocol. Earlier macro-name/step results cannot be the sole same-format controls.\n',
 'joint: the model generates sequence and operations. order_oracle: a program supplies correct names and the model generates operations. operation_oracle: the model selects names and termination, and a program executes the tools actually selected. Program-supplied content is not counted as prediction ability.\n',
 'The table reports full-task accuracy. Expansion requires correct expansion of every required call; sequence prediction requires the complete correct names and correct termination. joint+oracle evaluates the same jointly trained checkpoint in the corresponding oracle environment; single-task+oracle evaluates a specialist checkpoint supervised only on that component.\n']
 def value(model,cond,mode,split,L):
  c=groups.get((model,cond,mode,split,L));return f'{100*c["complete"]/c["n"]:.2f}% (n={c["n"]})' if c else 'Pending'
 for splitprefix in ['iid','ood','pressure','length']:
  for model in ['qwen1.5b','qwen3b','qwen7b','qwen32b']:
   label={'iid':'Original test: in-distribution short calls','ood':'Original test: unseen long compositions','pressure':'Original test: stress subset','length':'Independent confirmation'}[splitprefix]
   lines+=['\n## '+model+' / '+label,'|Calls|Joint free execution|Joint + sequence oracle|Single-task + sequence oracle|Joint + operation oracle|Single-task + operation oracle|','|---|---:|---:|---:|---:|---:|']
   for L in ([1,2] if splitprefix=='iid' else [3,4,5,6,8] if splitprefix=='length' else [3,4,5]):
    split='length'+str(L) if splitprefix=='length' else splitprefix
    vals=[value(model,c,m,split,L) for c,m in [('joint','joint'),('joint','order_oracle'),('order_oracle','order_oracle'),('joint','operation_oracle'),('operation_oracle','operation_oracle')]]
    lines.append('| '+str(L)+' | '+' | '.join(vals)+' |')
 lines+=['\n## Scope and reproduction\n','Oracle-assisted ability is distinct from autonomous ability. Seeds/examples are not selected for positive results; segment EOS/format failures are retained. Supervised-token counts differ across conditions and are recorded separately. B under earlier natural outputs covered only emitted calls; the correct-sequence oracle here covers all required calls.','\nRaw per-example trajectories are in runs/<run>/evaluation-*.jsonl, including all program/model segments and token IDs. Independent recomputation is in analysis/results-audit.json. Environment, model, and input hashes are in infrastructure/ and analysis/reproducibility-inputs.json; task configurations and frozen source are in analysis/formal-source-freeze.json.']
 (R/'REPORT.md').write_text('\n'.join(lines));print('Report updated from',audit['records'],'audited trajectories')
if __name__=='__main__':main()
