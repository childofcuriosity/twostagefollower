from pathlib import Path
import time,subprocess,sys
r=Path(__file__).resolve().parents[1]
print('Wait for complete 32B Base download before additional transfer',flush=True)
while not (r/'models/qwen32b/download-manifest.json').exists():time.sleep(60)
subprocess.run([sys.executable,'-u',str(r/'src/download.py'),'--repo','Qwen/Qwen2.5-32B-Instruct','--name','qwen32b-instruct'],check=True)
