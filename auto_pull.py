import subprocess
from pathlib import Path

repo_path = "/home/EliotPotts/LISP"
subprocess.run(["git", "pull"], cwd=repo_path, check=True)

Path("/var/www/eliotpotts_pythonanywhere_com_wsgi.py").touch()