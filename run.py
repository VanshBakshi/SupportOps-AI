import os,sys,subprocess
from pathlib import Path
root=Path(__file__).resolve(); backend=root/'backend'
os.chdir(root)
if str(backend) not in sys.path: sys.path.insert(0,str(backend))
subprocess.run([sys.executable,'-m','pip','install','-r',str(backend/'requirements.txt')],check=True)
subprocess.run([sys.executable,str(root/'scripts'/'seed.py')],check=True)
subprocess.run([sys.executable,'-m','uvicorn','app.main:app','--app-dir',str(backend),'--host','127.0.0.1','--port','8000','--reload'])
