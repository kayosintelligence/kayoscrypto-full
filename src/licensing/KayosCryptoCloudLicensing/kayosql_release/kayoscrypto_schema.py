import sqlite3
import os

def criar_banco_kayoscrypto():
    db_path = "data/kayoscrypto/kayoscrypto.kdb"
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS licencas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT NOT NULL,
        chave TEXT NOT NULL,
        ativa INTEGER NOT NULL DEFAULT 1,
        data_criacao TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    INSERT INTO licencas (codigo, chave)
    VALUES ('KAYOS-CRYPTO-0001', 'ExemploDeChave==')
    """)

    conn.commit()
    conn.close()

    print(f"Banco KayosCrypto criado com sucesso em: {db_path}")

if __name__ == "__main__":
    criar_banco_kayoscrypto()
