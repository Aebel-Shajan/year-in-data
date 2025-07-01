from contextlib import contextmanager
import sqlite3
from app.core.config import DB_PATH  # centralize config
from typing import Generator

@contextmanager
def get_connection() -> Generator:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()