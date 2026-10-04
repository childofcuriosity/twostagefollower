import argparse,concurrent.futures,hashlib,json,subprocess
from pathlib import Path
import urllib.request
ap=argparse.ArgumentParser();ap.add_argument('--repo',required=True);ap.add_argument('--name',required=True);a=ap.parse_args()
root=Path(__file__).resolve().parents[1];out=root/'models'/a.name;out.mkdir(exist_ok=True)
with urllib.request.urlopen('https://huggingface.co/api/models/'+a.repo,timeout=90) as response:meta=json.load(response)
sha=meta['sha'];(out/'hub-metadata.json').write_text(json.dumps(meta,indent=2))
files=[s['rfilename'] for s in meta['siblings'] if s['rfilename'] in ['config.json','generation_config.json','tokenizer.json','tokenizer_config.json','special_tokens_map.json','vocab.json','merges.txt','LICENSE','README.md','model.safetensors.index.json'] or s['rfilename'].endswith('.safetensors') and '/' not in s['rfilename']]
def fetch(name):
 p=out/name;subprocess.run(['curl','--fail','--silent','--show-error','--location','--connect-timeout','30','--max-time','1800','--retry','5','--retry-all-errors','--continue-at','-','--output',str(p),f'https://huggingface.co/{a.repo}/resolve/{sha}/{name}'],check=True)
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 print(name,p.stat().st_size,flush=True);return dict(file=name,bytes=p.stat().st_size,sha256=h.hexdigest())
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as p:manifest=list(p.map(fetch,files))
(out/'download-manifest.json').write_text(json.dumps(dict(repo=a.repo,revision=sha,files=manifest),indent=2))
