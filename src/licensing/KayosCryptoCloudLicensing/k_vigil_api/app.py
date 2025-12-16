from flask import Flask, jsonify, request, abort
from kayosql_release.kayosql_crypto_api import (
    registrar_licenca,
    consultar_licenca,
    desativar_licenca,
    verificar_chave
)
from k_vigil_api.auth import verificar_token, gerar_token
from k_vigil_api.logger import registrar_log
from utils.auth_utils import token_required  #  Importação para a rota protegida

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import os
import json
import glob
import hashlib

app = Flask(__name__)
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    storage_uri="redis://redis-kayos:6379",
    default_limits=["10 per minute"]
)

WHITELISTED_IPS = {"127.0.0.1"}

def verificar_ip_autorizado():
    ip_cliente = request.remote_addr
    if ip_cliente not in WHITELISTED_IPS:
        abort(403, description="Acesso negado: IP não autorizado.")

def autenticar_request():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    return verificar_token(token)

@app.route("/api/gerar", methods=["POST"])
@limiter.limit("5 per minute")
def gerar_licenca():
    verificar_ip_autorizado()
    ip = request.remote_addr

    if not autenticar_request():
        registrar_log(ip, "/api/gerar", "POST", 401)
        return jsonify({"erro": "Não autorizado"}), 401

    resultado = registrar_licenca()
    status = 200 if verificar_chave(resultado["chave"]) else 422
    registrar_log(ip, "/api/gerar", "POST", status, dados_extra=resultado)

    if status == 422:
        return jsonify({"erro": "Chave simbiótica inválida. Falha de composição criptossimbólica."}), 422
    return jsonify(resultado)

@app.route("/api/licenca/<codigo>", methods=["GET"])
def buscar_licenca(codigo):
    verificar_ip_autorizado()
    ip = request.remote_addr

    if not autenticar_request():
        registrar_log(ip, f"/api/licenca/{codigo}", "GET", 401)
        return jsonify({"erro": "Não autorizado"}), 401

    licenca = consultar_licenca(codigo)
    status = 200 if licenca else 404
    registrar_log(ip, f"/api/licenca/{codigo}", "GET", status)

    if not licenca:
        return jsonify({"erro": "Licença não encontrada."}), 404
    return jsonify(licenca)

@app.route("/api/desativar/<codigo>", methods=["POST"])
def desativar(codigo):
    verificar_ip_autorizado()
    ip = request.remote_addr

    if not autenticar_request():
        registrar_log(ip, f"/api/desativar/{codigo}", "POST", 401)
        return jsonify({"erro": "Não autorizado"}), 401

    sucesso = desativar_licenca(codigo)
    status = 200 if sucesso else 404
    registrar_log(ip, f"/api/desativar/{codigo}", "POST", status)

    if not sucesso:
        return jsonify({"erro": "Licença não encontrada ou já desativada."}), 404
    return jsonify({"mensagem": "Licença desativada com sucesso."})

@app.route("/api/token", methods=["POST"])
def token():
    ip = request.remote_addr
    try:
        response = gerar_token(request)
        registrar_log(ip, "/api/token", "POST", 200)
        return response
    except Exception as e:
        registrar_log(ip, "/api/token", "POST", 500, dados_extra={"erro": str(e)})
        return jsonify({"erro": "Erro interno ao gerar token."}), 500

@app.route("/api/logs/validar", methods=["GET"])
def validar_logs():
    verificar_ip_autorizado()
    ip = request.remote_addr

    if not autenticar_request():
        registrar_log(ip, "/api/logs/validar", "GET", 401)
        return jsonify({"erro": "Não autorizado"}), 401

    logs_path = "logs/logs_auditaveis/"
    resultados = []

    for filepath in sorted(glob.glob(os.path.join(logs_path, "log_*.json"))):
        try:
            with open(filepath, "r") as f:
                log = json.load(f)

            hash_original = log.get("hash_integridade")
            log_temp = dict(log)
            del log_temp["hash_integridade"]
            hash_recalculado = hashlib.sha256(
                json.dumps(log_temp, sort_keys=True).encode()
            ).hexdigest()

            status = "válido" if hash_original == hash_recalculado else "comprometido"

            resultados.append({
                "arquivo": os.path.basename(filepath),
                "status": status,
                "hash_esperado": hash_original,
                "hash_encontrado": hash_recalculado if status == "comprometido" else None
            })

        except Exception as e:
            resultados.append({
                "arquivo": os.path.basename(filepath),
                "status": "erro na leitura",
                "erro": str(e)
            })

    registrar_log(ip, "/api/logs/validar", "GET", 200)
    return jsonify({"validacoes": resultados})

#  NOVA ROTA PROTEGIDA
@app.route("/api/segredo", methods=["GET"])
@token_required
def segredo():
    return jsonify({"mensagem": "Acesso autorizado ao segredo da Engenharia KAYOS!"})

if __name__ == "__main__":
    app.run(host=os.getenv('FLASK_HOST', '127.0.0.1'), port=5000)

