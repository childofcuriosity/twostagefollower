"""Exact new-process checkpoint replay; original batch composition preserved."""
import argparse,json,time
from evaluate import *
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--model',choices=MODELS,required=True);a=ap.parse_args();torch.set_num_threads(4);torch.manual_seed(11)
 run=R/'runs'/f'{a.model}-joint-s11';assert (run/'evaluation-complete.json').exists()
 tok=AutoTokenizer.from_pretrained(MODELS[a.model],local_files_only=True);tok.pad_token=tok.eos_token
 base=AutoModelForCausalLM.from_pretrained(MODELS[a.model],local_files_only=True,torch_dtype=torch.bfloat16,attn_implementation='sdpa',low_cpu_mem_usage=True).cuda();model=PeftModel.from_pretrained(base,run/'adapter').eval()
 rows=read('independent');assert len(rows)==480;selected=[r for start in [0,96,192,288,384] for r in rows[start:start+8]];out=R/'analysis'/'reproduction'/a.model;out.mkdir(parents=True,exist_ok=False);results=[]
 for mode in MODES:
  p=out/f'{mode}.jsonl';evaluate(model,tok,selected,mode,p,8);old={r['id']:r for r in map(json.loads,(run/f'evaluation-{mode}-independent.jsonl').read_text().splitlines())}
  for row in map(json.loads,p.read_text().splitlines()):
   ref=old[row['id']];same=row==ref
   results.append(dict(mode=mode,id=row['id'],length=len(row['chain']),full_record_identical=same,grade_identical=row['grade']==ref['grade']))
 record=dict(model=a.model,records=len(results),exact=sum(x['full_record_identical'] for x in results),grades=sum(x['grade_identical'] for x in results),results=results)
 (out/'summary.json').write_text(json.dumps(record,indent=2));print(json.dumps({k:v for k,v in record.items() if k!='results'}),flush=True)
if __name__=='__main__':main()
