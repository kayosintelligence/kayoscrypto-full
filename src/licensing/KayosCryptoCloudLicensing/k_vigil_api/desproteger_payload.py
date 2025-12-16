#  Arquivo: k_vigil_api/desproteger_payload.py

import os
import hashlib
import base64
from cryptography.fernet import Fernet

PROTEGIDOS_FOLDER = "k_vigil_api/protegidos"
RESULTADOS_FOLDER = "k_vigil_api/resultados"

os.makedirs(RESULTADOS_FOLDER, exist_ok=True)

def gerar_chave_aes(uuid: str) -> bytes:
    hash_bytes = hashlib.sha256(uuid.encode()).digest()
    return base64.urlsafe_b64encode(hash_bytes)

def desproteger(nome_arquivo_protegido: str, uuid: str) -> str:
    caminho_arquivo = os.path.join(PROTEGIDOS_FOLDER, nome_arquivo_protegido)
    destino = os.path.join(RESULTADOS_FOLDER, nome_arquivo_protegido.replace(".kprotect", ""))

    if not os.path.isfile(caminho_arquivo):
        raise FileNotFoundError(f"Arquivo '{nome_arquivo_protegido}' não encontrado em protegidos.")

    chave = gerar_chave_aes(uuid)
    fernet = Fernet(chave)

    with open(caminho_arquivo, "rb") as f:
        conteudo_criptografado = f.read()

    try:
        conteudo_descriptografado = fernet.decrypt(conteudo_criptografado)
    except Exception as e:
        raise ValueError("Erro ao descriptografar. UUID incorreto ou arquivo corrompido.") from e

    with open(destino, "wb") as f:
        f.write(conteudo_descriptografado)

    return destino
