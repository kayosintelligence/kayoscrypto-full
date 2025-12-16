#  Arquivo: k_vigil_api/utils/exportar_licencas.py

import csv
from k_vigil_api.db.db import get_connection

def exportar_licencas_csv(caminho_arquivo="licencas_exportadas.csv"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT uuid, chave, ativa, criada_em FROM licencas ORDER BY criada_em DESC")
    licencas = cur.fetchall()
    cur.close()
    conn.close()

    with open(caminho_arquivo, mode="w", newline="", encoding="utf-8") as arquivo_csv:
        escritor = csv.writer(arquivo_csv)
        escritor.writerow(["UUID", "Chave", "Ativa", "Criada Em"])
        for linha in licencas:
            escritor.writerow(linha)

    print(f"[] Licenças exportadas para: {caminho_arquivo}")

if __name__ == "__main__":
    exportar_licencas_csv()
