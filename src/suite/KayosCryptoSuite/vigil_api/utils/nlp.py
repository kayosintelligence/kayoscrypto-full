import csv
import os
from difflib import SequenceMatcher

CAMINHO_CSV = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'links_afiliados_2025-07-15.csv'))

def calcular_similaridade(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def buscar_link_por_intencao(texto):
    resultados = []
    texto = texto.lower()
    tokens = texto.split()

    try:
        with open(CAMINHO_CSV, newline='', encoding='utf-8') as csvfile:
            leitor = csv.DictReader(csvfile)

            for linha in leitor:
                try:
                    nicho = linha["ramoNicho"].lower()
                    nome = linha["nomeProduto"].lower()
                    url = linha["linkAfiliado"]
                except KeyError:
                    continue

                score = 0
                for token in tokens:
                    if token in nome:
                        score += 2
                    elif token in nicho:
                        score += 1
                    else:
                        score += calcular_similaridade(token, nome)

                if url:
                    resultados.append((score, nicho, nome, url))

    except FileNotFoundError:
        print(f"[ERRO] Arquivo CSV não encontrado em: {CAMINHO_CSV}")
        return {
            "nicho": "Desconhecido",
            "produto": "Base de dados ausente",
            "link": "#"
        }

    if resultados:
        # Ordena do score mais alto para o menor
        resultados.sort(reverse=True)
        melhor = resultados[0]
        return {
            "nicho": melhor[1],
            "produto": melhor[2],
            "link": melhor[3]
        }

    return {
        "nicho": "Desconhecido",
        "produto": "Nenhum resultado encontrado",
        "link": "#"
    }
