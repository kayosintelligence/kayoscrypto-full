from vigil_api.utils.nlp import buscar_link_por_intencao
from vigil_api.license_log import registrar_evento

def processar_busca(texto):
    resultado = buscar_link_por_intencao(texto)
    registrar_evento("BUSCA", texto, resultado.get("redirect_to") if resultado else None)
    return resultado
