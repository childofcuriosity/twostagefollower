"""Low-frequency final artifact assembly; scientific review is still required."""
import json,os,subprocess,sys,time
from common import R,write
from wait_marker import wait_for_marker

write(R/'analysis/final-analysis-launch.json',dict(pid=os.getpid(),started=time.time()))
wait_for_marker(R/'fresh-confirmation/analysis/pipeline-complete.json',
                [phase/'analysis/pipeline-failed.json' for phase in [R,R/'context-intervention',R/'fresh-confirmation']])
for script in ['analyze.py','compare.py','attribution.py','decomposition.py','positions.py','accounting.py','context_cases.py','plots.py','context_plots.py']:
    python=str(R.parents[3]/'.analysis-venv/bin/python') if script.endswith('plots.py') else sys.executable
    subprocess.run([python,str(R/'src'/script)],check=True)
write(R/'analysis/final-analysis-complete.json',dict(finished=time.time(),note='All analysis artifacts assembled; agent must inspect results, figures, cases, resource release, and write scientific conclusions. Goal not automatically completed.'))
