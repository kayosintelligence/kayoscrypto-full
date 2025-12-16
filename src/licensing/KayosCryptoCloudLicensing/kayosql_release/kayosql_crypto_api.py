import uuid
import datetime
import json
import os
import re

from quantumwheel_protocol import rodar_quantum
from rotor_protocol import rodar_rotor
from ofanim_protocol import ativar_ofanim

DB_JSON = "data/kayoscrypto/licencas.json"

# -----------------------------
# Utilitários de armazenamento
# -----------------------------
def carregar_licencas():
    if not os.path.exists(DB_JSON):
        return []
    with open(DB_JSON, "r") as f:
        return json.load(f)

def salvar_licencas(licencas):
    with open(DB_JSON, "w") as f:
        json.dump(licencas, f, indent=4)

# -----------------------------
# Geração de Chave Simbiótica
# -----------------------------
def gerar_chave_simbolica():
    quantum = rodar_quantum()
    rotor = rodar_rotor()
    ofanim = ativar_ofanim()

    print(f"[DEBUG] quantum: {quantum}")
    print(f"[DEBUG] rotor: {rotor}")
    print(f"[DEBUG] ofanim: {ofanim}")

    # Se quantum vier como dicionário, extrair a chave correta
    if isinstance(quantum, dict) and 'roda' in quantum:
        quantum = quantum['roda']

    chave = f"{quantum[:3]}{rotor[-3:]}{ofanim[2:5]}"
    print(f"[DEBUG] chave gerada: {chave}")
    return chave

# -----------------------------
# Validação da Chave Simbiótica
# -----------------------------
def verificar_chave(chave):
    """
    Valida se a chave simbiótica segue o padrão esperado.
    Deve conter 9 caracteres alfanuméricos.
    """
    if not isinstance(chave, str):
        return False
    if len(chave) != 9:
        return False
    if not re.match(r'^[A-Za-z0-9]{9}$', chave):
        return False
    return True

# -----------------------------
# Registro de Licença
# -----------------------------
def registrar_licenca(_dados=None):
    licencas = carregar_licencas()
    codigo = str(uuid.uuid4())
    chave = gerar_chave_simbolica()
    data_criacao = datetime.datetime.now().isoformat()

    nova_licenca = {
        "codigo": codigo,
        "chave": chave,
        "ativa": True,
        "data_criacao": data_criacao
    }

    licencas.append(nova_licenca)
    salvar_licencas(licencas)

    return {"codigo": codigo, "chave": chave}

# -----------------------------
# Consulta de Licença
# -----------------------------
def consultar_licenca(codigo):
    licencas = carregar_licencas()
    for licenca in licencas:
        if licenca["codigo"] == codigo:
            return licenca
    return None

# -----------------------------
# Desativação de Licença
# -----------------------------
def desativar_licenca(codigo):
    licencas = carregar_licencas()
    for licenca in licencas:
        if licenca["codigo"] == codigo:
            licenca["ativa"] = False
            salvar_licencas(licencas)
            return True
    return False

