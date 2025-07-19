import subprocess
from pathlib import Path

subprocess.run(["git", "pull"], check=True)

Path("/var/www/eliotpotts_pythonanywhere_com_wsgi.py").touch()