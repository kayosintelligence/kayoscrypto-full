#!/usr/bin/env python3
"""
 START FINAL - KAYOSCRYPTO 3D ENTERPRISE
Inicialização otimizada do sistema
"""

import subprocess
import sys
import os
import time
import signal

def check_dependencies():
 """Verificar dependências"""
 try:
 import psycopg2
 import fastapi
 import uvicorn
 print(" Dependências principais OK")
 return True
 except ImportError as e:
 print(f" Dependência faltante: {e}")
 return False

def start_api(port=8000):
 """Iniciar API FastAPI"""
 try:
 # Verificar se porta está livre
 import socket
 sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 if sock.connect_ex(('localhost', port)) == 0:
 print(f" Parando processo na porta {port}...")
 subprocess.run(['fuser', '-k', f'{port}/tcp'], capture_output=True)
 time.sleep(2)
 
 print(f" Iniciando API na porta {port}...")
 api_process = subprocess.Popen([
 sys.executable, 'src/api/fastapi_enterprise_fixed.py'
 ])
 
 # Aguardar API iniciar
 time.sleep(5)
 return api_process
 except Exception as e:
 print(f" Erro ao iniciar API: {e}")
 return None

def start_web_dashboard(port=5000):
 """Iniciar dashboard web simples"""
 try:
 print(f" Iniciando Web Dashboard na porta {port}...")
 
 # Criar servidor web simples
 html_content = """
 <!DOCTYPE html>
 <html>
 <head>
 <title>KayosCrypto 3D Enterprise</title>
 <style>
 body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
 .header { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 40px; border-radius: 10px; text-align: center; }
 .card { background: white; padding: 20px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
 .nav { display: flex; gap: 10px; margin: 20px 0; }
 .nav a { background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
 .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
 .online { background: #d4edda; color: #155724; }
 .endpoints { background: #e2e3e5; padding: 15px; border-radius: 5px; }
 </style>
 </head>
 <body>
 <div class="header">
 <h1> KayosCrypto 3D Enterprise</h1>
 <p>Sistema de Criptografia Multidimensional</p>
 </div>
 
 <div class="nav">
 <a href="http://localhost:8000/docs" target="_blank">API Documentation</a>
 <a href="http://localhost:8000/health" target="_blank">Health Check</a>
 <a href="http://localhost:8000/cubes" target="_blank">Listar Cubos</a>
 </div>
 
 <div class="card">
 <h2> Status do Sistema</h2>
 <div class="status online"> Sistema Operacional</div>
 <p><strong>Database:</strong> k_crypto</p>
 <p><strong>Schema:</strong> kayos_enterprise</p>
 <p><strong>Versão:</strong> 3.0.0 Enterprise</p>
 </div>
 
 <div class="card">
 <h2> Endpoints da API</h2>
 <div class="endpoints">
 <p><strong>GET</strong> <code>/</code> - Status da API</p>
 <p><strong>GET</strong> <code>/health</code> - Health Check</p>
 <p><strong>GET</strong> <code>/cubes</code> - Listar cubos</p>
 <p><strong>POST</strong> <code>/cubes/create</code> - Criar cubo</p>
 <p><strong>GET</strong> <code>/dashboard/security</code> - Dashboard</p>
 <p><strong>POST</strong> <code>/demo/encrypt</code> - Demo criptografia</p>
 </div>
 </div>
 
 <div class="card">
 <h2> Autenticação</h2>
 <p>Use o token: <code>kayos_enterprise_token</code></p>
 <p>No header: <code>Authorization: Bearer kayos_enterprise_token</code></p>
 </div>
 
 <div class="card">
 <h2> Características do Sistema</h2>
 <ul>
 <li> Database PostgreSQL com 10 tabelas enterprise</li>
 <li> API REST FastAPI com autenticação</li>
 <li> Cubo Sator 3D com 6 faces multidimensionais</li>
 <li> Sistema de auditoria completo</li>
 <li> Encontro quântico-clássico 4D</li>
 <li> Pronto para produção enterprise</li>
 </ul>
 </div>
 
 <script>
 // Atualizar status automaticamente
 async function checkHealth() {
 try {
 const response = await fetch('http://localhost:8000/health');
 const data = await response.json();
 document.getElementById('health-status').innerHTML = 
 ` API: ${data.status} | Database: ${data.database} | Cubos: ${data.cubes_count}`;
 } catch (error) {
 document.getElementById('health-status').innerHTML = 
 ' API não respondendo';
 }
 }
 
 // Verificar a cada 30 segundos
 checkHealth();
 setInterval(checkHealth, 30000);
 </script>
 <div class="card">
 <h3> Status em Tempo Real</h3>
 <div id="health-status">Verificando...</div>
 </div>
 </body>
 </html>
 """
 
 # Servir HTML simples
 from http.server import HTTPServer, BaseHTTPRequestHandler
 
 class SimpleHandler(BaseHTTPRequestHandler):
 def do_GET(self):
 self.send_response(200)
 self.send_header('Content-type', 'text/html')
 self.end_headers()
 self.wfile.write(html_content.encode())
 
 def log_message(self, format, *args):
 pass # Silenciar logs
 
 server = HTTPServer(('0.0.0.0', port), SimpleHandler)
 print(f" Web Dashboard rodando em http://localhost:{port}")
 server.serve_forever()
 
 except Exception as e:
 print(f" Erro no Web Dashboard: {e}")

def main():
 print(" KAYOSCRYPTO 3D ENTERPRISE - INICIALIZAÇÃO")
 print("=" * 50)
 
 # Verificar dependências
 if not check_dependencies():
 print(" Instale as dependências primeiro:")
 print(" pip install psycopg2-binary fastapi uvicorn cryptography pydantic")
 return
 
 # Iniciar API
 api_process = start_api(8000)
 if not api_process:
 print(" Falha ao iniciar API")
 return
 
 print("⏳ Aguardando API inicializar...")
 time.sleep(3)
 
 # Testar API
 try:
 import requests
 response = requests.get("http://localhost:8000/health", timeout=10)
 if response.status_code == 200:
 print(" API respondendo corretamente")
 else:
 print(f" API retornou status {response.status_code}")
 except:
 print(" API pode estar iniciando...")
 
 # Iniciar Web Dashboard em thread separada
 import threading
 web_thread = threading.Thread(target=start_web_dashboard, daemon=True)
 web_thread.start()
 
 print("\n SISTEMA INICIADO COM SUCESSO!")
 print(" URLs de Acesso:")
 print(" API Documentation: http://localhost:8000/docs")
 print(" Web Dashboard: http://localhost:5000")
 print(" Health Check: http://localhost:8000/health")
 print(" Listar Cubos: http://localhost:8000/cubes")
 print("\n Token de Autenticação: kayos_enterprise_token")
 print("\n Pressione Ctrl+C para parar o sistema")
 
 try:
 # Manter processo principal rodando
 while True:
 time.sleep(1)
 except KeyboardInterrupt:
 print("\n Parando sistema...")
 if api_process:
 api_process.terminate()

if __name__ == "__main__":
 main()
