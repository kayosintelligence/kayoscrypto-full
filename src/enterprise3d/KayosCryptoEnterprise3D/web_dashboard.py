import os
"""
 WEB DASHBOARD - KAYOSCRYPTO 3D ENTERPRISE
Interface web para gerenciamento do sistema
"""

from flask import Flask, render_template, request, jsonify, session
import requests
import json

app = Flask(__name__)
app.secret_key = os.getenv("KAYOS_CRYPTO_KEY", "default_insecure_key").encode()

# Configuração da API
API_BASE_URL = "http://localhost:8000"
API_TOKEN = os.getenv("KAYOS_TOKEN", "")

@app.route('/')
def index():
 """Página principal do dashboard"""
 return render_template('index.html')

@app.route('/dashboard')
def dashboard():
 """Dashboard de segurança"""
 try:
 # Buscar dados da API
 headers = {"Authorization": f"Bearer {API_TOKEN}"}
 response = requests.get(f"{API_BASE_URL}/dashboard/security", headers=headers)
 
 if response.status_code == 200:
 data = response.json()
 return render_template('dashboard.html', data=data)
 else:
 return render_template('error.html', error="Falha ao carregar dashboard")
 except Exception as e:
 return render_template('error.html', error=str(e))

@app.route('/cubes')
def cubes_management():
 """Gerenciamento de cubos"""
 try:
 response = requests.get(f"{API_BASE_URL}/cubes")
 if response.status_code == 200:
 cubes = response.json()
 return render_template('cubes.html', cubes=cubes)
 else:
 return render_template('error.html', error="Falha ao carregar cubos")
 except Exception as e:
 return render_template('error.html', error=str(e))

@app.route('/api/create_cube', methods=['POST'])
def api_create_cube():
 """API endpoint para criar cubo"""
 try:
 data = request.json
 headers = {"Authorization": f"Bearer {API_TOKEN}"}
 response = requests.post(f"{API_BASE_URL}/cubes/create", json=data, headers=headers)
 return jsonify(response.json()), response.status_code
 except Exception as e:
 return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/rotate_cube', methods=['POST'])
def api_rotate_cube():
 """API endpoint para rotacionar cubo"""
 try:
 data = request.json
 headers = {"Authorization": f"Bearer {API_TOKEN}"}
 cube_name = data.get('cube_name')
 response = requests.post(f"{API_BASE_URL}/cubes/{cube_name}/rotate", json=data, headers=headers)
 return jsonify(response.json()), response.status_code
 except Exception as e:
 return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/generate_keys', methods=['POST'])
def api_generate_keys():
 """API endpoint para gerar chaves"""
 try:
 data = request.json
 headers = {"Authorization": f"Bearer {API_TOKEN}"}
 response = requests.post(f"{API_BASE_URL}/keys/generate", json=data, headers=headers)
 return jsonify(response.json()), response.status_code
 except Exception as e:
 return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
 app.run(host=os.getenv('FLASK_HOST', '127.0.0.1'), port=5000, debug=False)
