import jwt
import datetime
import os
from flask import jsonify

# Chave secreta vinda do ambiente, com fallback seguro
CHAVE_SECRETA = os.getenv("SECRET_KEY", "chave-secreta")

def gerar_token(request):
    """
    Gera um token JWT com validade de 2 horas, caso usuário e senha estejam corretos.
    """
    dados = request.get_json()
    usuario = dados.get("usuario")
    senha = dados.get("senha")

    if usuario == "admin" and senha == "segredo123":
        payload = {
            "usuario": usuario,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }
        token = jwt.encode(payload, CHAVE_SECRETA, algorithm="HS256")
        return jsonify({"token": token})

    return jsonify({"erro": "Credenciais inválidas"}), 401

def verificar_token(token):
    """
    Verifica a validade do token JWT. Retorna True se válido, False se inválido.
    Pode ser estendido futuramente para retornar dados do payload.
    """
    try:
        jwt.decode(token, CHAVE_SECRETA, algorithms=["HS256"])
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False
