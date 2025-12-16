import sqlite3
import os
from datetime import datetime, timezone

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'license_log.db'))

def registrar_evento(tipo, texto, resultado=None):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS license_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT,
                texto TEXT,
                resultado TEXT,
                timestamp TEXT
            )
        ''')
        conn.commit()

        cursor.execute('''
            INSERT INTO license_log (tipo, texto, resultado, timestamp)
            VALUES (?, ?, ?, ?)
    ''', (tipo, texto, resultado, datetime.now(timezone.utc).isoformat()))
        conn.commit()

    except Exception as e:
        print(f"[ERRO LOG] {e}")
    finally:
        conn.close()
