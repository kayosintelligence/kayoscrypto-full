#  Arquivo: k_vigil_api/utils/importar_licencas.py

import csv
from k_vigil_api.db.db import get_connection

def importar_licencas_csv(caminho_arquivo="licencas_exportadas.csv"):
    conn = get_connection()
    cur = conn.cursor()

    with open(caminho_arquivo, mode="r", newline="", encoding="utf-8") as arquivo_csv:
        leitor = csv.DictReader(arquivo_csv)
        total = 0

        for linha in leitor:
            uuid = linha["UUID"]
            chave = linha["Chave"]
            ativa = linha["Ativa"].lower() == "true"
            criada_em = linha["Criada Em"]

            cur.execute("""
                INSERT INTO licencas (uuid, chave, ativa, criada_em)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (uuid, chave, ativa, criada_em))

            total += 1

    conn.commit()
    cur.close()
    conn.close()
    print(f"[] {total} licenças importadas com sucesso de '{caminho_arquivo}'.")

if __name__ == "__main__":
    importar_licencas_csv()
