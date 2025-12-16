# verificador_links_afiliados.py

import csv
import requests
from bs4 import BeautifulSoup

CAMINHO_CSV = "links_afiliados_2025-07-15.csv"
RELATORIO_CSV = "relatorio_verificacao.csv"

def verificar_links():
    resultados = []

    with open(CAMINHO_CSV, newline='', encoding='utf-8') as csvfile:
        leitor = csv.DictReader(csvfile)

        for linha in leitor:
            produto_esperado = linha.get("nomeProduto", "").strip()
            url = linha.get("linkAfiliado", "").strip()

            if not url.startswith("http"):
                resultados.append({
                    "produtoCSV": produto_esperado,
                    "url": url,
                    "status": "Inválido",
                    "tituloExtraido": "",
                    "match": "N/A"
                })
                continue

            try:
                resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                if resp.status_code != 200:
                    status = f"Erro HTTP {resp.status_code}"
                    titulo = ""
                    match = "N/A"
                else:
                    soup = BeautifulSoup(resp.content, "html.parser")
                    titulo = soup.title.string.strip() if soup.title else ""
                    status = "OK"
                    match = "SIM" if produto_esperado.lower() in titulo.lower() else "NÃO"

            except Exception as e:
                status = f"Erro: {e.__class__.__name__}"
                titulo = ""
                match = "N/A"

            resultados.append({
                "produtoCSV": produto_esperado,
                "url": url,
                "status": status,
                "tituloExtraido": titulo,
                "match": match
            })

    with open(RELATORIO_CSV, "w", newline='', encoding='utf-8') as saida:
        campos = ["produtoCSV", "url", "status", "tituloExtraido", "match"]
        escritor = csv.DictWriter(saida, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(resultados)

    print(f" Relatório gerado: {RELATORIO_CSV}")


if __name__ == "__main__":
    verificar_links()
