import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "golf.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jogadores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        handicap REAL,
        souhait TEXT,
        prioridade TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jogadores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        handicap REAL,
        souhait TEXT,
        prioridade TEXT,
        convidado INTEGER DEFAULT 0
)
""")

    conn.commit()
    conn.close()


# 🔥 IMPORTANT : créer la table automatiquement au démarrage
init_db()