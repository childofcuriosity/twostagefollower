"""Validate raw model/oracle token provenance and exact reconstructed model contexts."""
import argparse,hashlib,json
from pathlib import Path
from protocol import R,MODELS,prompt
from transformers import AutoTokenizer

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--complete-only',action='store_true');a=ap.parse_args();counts={};files={}
 for model,path in MODELS.items():
  tok=AutoTokenizer.from_pretrained(path,local_files_only=True);total=events=0
  for run in sorted((R/'runs').glob(model+'-*')):
   if a.complete_only and not (run/'evaluation-complete.json').exists():continue
   for p in sorted(run.glob('evaluation-*.jsonl')):
    data=p.read_bytes();files[str(p.relative_to(R))]=hashlib.sha256(data).hexdigest()
    for line in data.splitlines():
     try:row=json.loads(line)
     except json.JSONDecodeError:
      if not (run/'evaluation-complete.json').exists():continue
      raise
     ctx=tok.encode(prompt(row),add_special_tokens=False)
     for e in row['events']:
      assert len(ctx)==e['prefix_tokens']
      assert hashlib.sha256(json.dumps(ctx).encode()).hexdigest()==e['prefix_sha256']
      assert tok.decode(e['token_ids'],clean_up_tokenization_spaces=False)==e['text']
      if e['source']=='oracle':assert tok.encode(e['text'],add_special_tokens=False)==e['token_ids']
      else:assert e['source']=='model'
      ctx+=e['token_ids'];events+=1
     total+=1
  counts[model]=dict(trajectories=total,events=events)
 (R/'analysis/token-replay.json').write_text(json.dumps(dict(counts=counts,files=files),indent=2));print(counts)
if __name__=='__main__':main()
