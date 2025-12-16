#  Arquivo: k_armor_core/core_engine.py

import os
import base64
from cryptography.fernet import Fernet

def gerar_chave():
    return Fernet.generate_key()

def salvar_chave_em_arquivo(caminho, chave):
    with open(caminho, 'wb') as f:
        f.write(chave)

def carregar_chave(caminho):
    with open(caminho, 'rb') as f:
        return f.read()

def criptografar_arquivo(caminho_arquivo, chave):
    fernet = Fernet(chave)
    with open(caminho_arquivo, 'rb') as file:
        conteudo = file.read()
    conteudo_criptografado = fernet.encrypt(conteudo)
    with open(caminho_arquivo + '.enc', 'wb') as file:
        file.write(conteudo_criptografado)

def descriptografar_arquivo(caminho_arquivo_enc, chave):
    fernet = Fernet(chave)
    with open(caminho_arquivo_enc, 'rb') as file:
        conteudo_criptografado = file.read()
    conteudo = fernet.decrypt(conteudo_criptografado)
    with open(caminho_arquivo_enc.replace('.enc', ''), 'wb') as file:
        file.write(conteudo)
