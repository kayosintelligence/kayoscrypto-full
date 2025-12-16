#  Arquivo: k_vigil_core/core_license_engine.py

import hashlib

def gerar_chave_licenca(uuid_str: str, salt: str = "KAYOS_SALT"):
    """Gera uma chave de licença a partir do UUID e um salt fixo."""
    base = f"{uuid_str}{salt}".encode()
    return hashlib.sha256(base).hexdigest()

def validar_licenca(uuid_str: str, chave_fornecida: str, salt: str = "KAYOS_SALT"):
    """Valida a chave fornecida comparando com a derivada do UUID + salt."""
    chave_esperada = gerar_chave_licenca(uuid_str, salt)
    return chave_fornecida == chave_esperada
