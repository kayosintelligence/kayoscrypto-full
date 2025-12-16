import os
import psycopg2
from datetime import datetime

# Configurações do PostgreSQL
DB_NAME = "kayoscrypto"
DB_USER = "kayos"
DB_PASSWORD = os.getenv("KAYOS_DB_PASSWORD", "")
DB_HOST = "localhost"
DB_PORT = "5432"

def salvar_log_busca(query=None, produto=None, link=None, nicho=None, origem_ip=None, user_agent=None):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO license_log (timestamp, query, produto, link, nicho, origem_ip, user_agent)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            datetime.now(), query, produto, link, nicho, origem_ip, user_agent
        ))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("Erro ao salvar log no banco de dados:", e)
