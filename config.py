import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "database.db")
HOST = "0.0.0.0"
PORT = 5000
WINDOW_TITLE = "Stock Manager"