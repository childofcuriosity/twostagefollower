import concurrent.futures,hashlib,json,subprocess,time
from pathlib import Path
import httpx
root=Path(__file__).resolve().parents[4]
repo='Qwen/Qwen2.5-1.5B'
out=root/'workspace/research/B01-02/model';out.mkdir(exist_ok=True)
with httpx.Client(timeout=60) as c:
 r=c.get('https://huggingface.co/api/models/'+repo);r.raise_for_status();meta=r.json()
sha=meta['sha'];(out/'hub-metadata.json').write_text(json.dumps(meta,indent=2))
files=[s['rfilename'] for s in meta['siblings'] if s['rfilename'] in ['config.json','generation_config.json','tokenizer.json','tokenizer_config.json','vocab.json','merges.txt','LICENSE','README.md'] or s['rfilename'].endswith('.safetensors') or s['rfilename']=='model.safetensors.index.json']
def download(name):
 p=out/name;p.parent.mkdir(parents=True,exist_ok=True)
 url=f'https://huggingface.co/{repo}/resolve/{sha}/{name}'
 subprocess.run(['curl','--fail','--silent','--show-error','--location','--connect-timeout','30','--max-time','1800','--retry','5','--retry-delay','2','--retry-all-errors','--continue-at','-','--output',str(p),url],check=True)
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 print(name,p.stat().st_size,flush=True)
 return {'file':name,'bytes':p.stat().st_size,'sha256':h.hexdigest()}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:manifest=list(pool.map(download,files))
(out/'download-manifest.json').write_text(json.dumps({'repo':repo,'revision':sha,'files':manifest},indent=2))
