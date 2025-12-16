from flask import Blueprint, request, jsonify, make_response
import sqlite3
import csv
from .controllers import processar_busca
from .database import salvar_log_busca
import os
import io

routes = Blueprint("routes", __name__)

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'license_log.db'))

@routes.route("/kai-search")
def kai_search():
    query = request.args.get("query", "")
    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")

    resultado = processar_busca(query)

    produto = resultado.get("produto") if resultado else None
    link = resultado.get("link") if resultado else None
    nicho = resultado.get("nicho") if resultado else None

    salvar_log_busca(
        query=query,
        produto=produto,
        link=link,
        nicho=nicho,
        origem_ip=ip,
        user_agent=user_agent
    )

    return jsonify(resultado)

@routes.route("/admin/logs", methods=["GET"])
def exibir_logs():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM license_log ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        conn.close()

        logs = []
        for row in rows:
            logs.append({
                "id": row[0],
                "tipo": row[1],
                "texto": row[2],
                "resultado": row[3],
                "timestamp": row[4]
            })

        return jsonify(logs)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@routes.route("/admin/logs/export", methods=["GET"])
def exportar_logs():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM license_log ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        conn.close()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "tipo", "texto", "resultado", "timestamp"])
        writer.writerows(rows)

        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=license_logs.csv"
        response.headers["Content-type"] = "text/csv"
        return response

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

