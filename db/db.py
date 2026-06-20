import sqlite3
import sys
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "gensou.db"

def get_conn(db_path=None):
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def pack(arr):
    # Python list --> JSON array from DB
    return json.dumps(arr, ensure_ascii=False)

def unpack(s):
    # JSON array from DB --> Python list
    return json.loads(s) if s else []

'''
import db.artists

if __name__ == "__main__":
    artists.add(name="ROSARIO",
               alt_names=['† ROSARIO †'], an_lang=['rnz'],
               description='vk band active from 1994 to 1995',
               country="JPN")
'''
