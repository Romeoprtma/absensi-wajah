import sqlite3
from config import DB_CONFIG

def get_db_connection():
    return sqlite3.connect(DB_CONFIG["database"])
