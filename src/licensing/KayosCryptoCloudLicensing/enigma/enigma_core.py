import hashlib
import base64

# Função para gerar uma chave baseada no UUID
def gerar_chave_licenca(uuid: str) -> str:
    hash = hashlib.sha256(uuid.encode()).digest()
    return base64.urlsafe_b64encode(hash[:16]).decode()

# Função para validar se a chave bate com o UUID
def validar_chave_licenca(uuid: str, chave: str) -> bool:
    return gerar_chave_licenca(uuid) == chave
