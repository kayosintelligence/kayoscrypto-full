#  Arquivo: k_vigil_api/proteger_payload.py

import os
import hashlib
import base64
from cryptography.fernet import Fernet

UPLOAD_FOLDER = "k_vigil_api/uploads"
PROTEGIDOS_FOLDER = "k_vigil_api/protegidos"

os.makedirs(PROTEGIDOS_FOLDER, exist_ok=True)

def gerar_chave_aes(uuid: str) -> bytes:
    hash_bytes = hashlib.sha256(uuid.encode()).digest()
    return base64.urlsafe_b64encode(hash_bytes)

def proteger(nome_arquivo: str, uuid: str) -> str:
    caminho_arquivo = os.path.join(UPLOAD_FOLDER, nome_arquivo)
    destino = os.path.join(PROTEGIDOS_FOLDER, nome_arquivo + ".kprotect")

    if not os.path.isfile(caminho_arquivo):
        raise FileNotFoundError(f"Arquivo '{nome_arquivo}' não encontrado em uploads.")

    chave = gerar_chave_aes(uuid)
    fernet = Fernet(chave)

    with open(caminho_arquivo, "rb") as f:
        conteudo = f.read()

    conteudo_criptografado = fernet.encrypt(conteudo)

    with open(destino, "wb") as f:
        f.write(conteudo_criptografado)

    return destino
