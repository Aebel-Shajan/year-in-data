import os
from pathlib import Path

# Get the base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Path to your SQLite database file
DB_PATH = os.getenv("DB_PATH", str(BASE_DIR.parent.parent / "data/gold/gold.db"))
