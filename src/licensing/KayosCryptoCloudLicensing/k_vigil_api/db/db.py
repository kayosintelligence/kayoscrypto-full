import os
#  Arquivo: k_vigil_api/db/db.py

import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname="kayoscrypto",
        user="kayos",
        password = os.getenv("KAYOS_AUTH_PASSWORD", "default_insecure_password"),  # substitua pela senha que você criou
        host="localhost",
        port=5433  # ← PORTA CORRETA AQUI
    )

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS licencas (
            id SERIAL PRIMARY KEY,
            uuid TEXT NOT NULL,
            chave TEXT NOT NULL,
            ativa BOOLEAN DEFAULT TRUE,
            criada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()
