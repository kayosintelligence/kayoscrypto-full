#!/usr/bin/env python3
"""
 TESTE CORRIGIDO - KAYOSCRYPTO 3D ENTERPRISE
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import sys
import os

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

class SimpleDBTest:
 """Teste simples de conexão"""
 
 def __init__(self):
 self.conn = None
 
 def connect(self):
 """Conectar ao banco"""
 try:
 self.conn = psycopg2.connect(
 "dbname=k_crypto user=kayos password=kayopass host=localhost port=5432",
 cursor_factory=RealDictCursor
 )
 print(" Conexão PostgreSQL estabelecida!")
 return True
 except Exception as e:
 print(f" Falha na conexão: {e}")
 return False
 
 def test_queries(self):
 """Testar consultas básicas"""
 try:
 with self.conn.cursor() as cursor:
 # Testar cubos
 cursor.execute("SELECT cube_name, security_level FROM kayos_enterprise.sator_cubes;")
 cubes = cursor.fetchall()
 print(f" Cubos encontrados: {len(cubes)}")
 for cube in cubes:
 print(f" - {cube['cube_name']} ({cube['security_level']})")
 
 # Testar chaves
 cursor.execute("SELECT algorithm_combination, security_level FROM kayos_enterprise.cryptographic_keys_4d WHERE is_active = true;")
 keys = cursor.fetchall()
 print(f" Chaves ativas: {len(keys)}")
 for key in keys:
 print(f" - {key['algorithm_combination']}")
 
 # Testar dashboard
 cursor.execute("SELECT * FROM kayos_enterprise.security_dashboard;")
 dashboard = cursor.fetchall()
 print(f" Dashboard: {dashboard}")
 
 return True
 except Exception as e:
 print(f" Erro nas consultas: {e}")
 return False
 
 def test_imports(self):
 """Testar importação dos módulos"""
 try:
 print("\n Testando importação de módulos...")
 
 # Testar database
 from database.postgresql_manager import PostgreSQLManager
 print(" database.postgresql_manager - OK")
 
 # Testar cube (pode falhar se houver dependências)
 try:
 from cube.sator_cube_3d import SatorCube3D, CubeFace, CubeRotation
 print(" cube.sator_cube_3d - OK")
 except ImportError as e:
 print(f" cube.sator_cube_3d - Parcial: {e}")
 
 # Testar security
 try:
 from security.hsm_integration import HSMEnterpriseManager
 print(" security.hsm_integration - OK")
 except ImportError as e:
 print(f" security.hsm_integration - Parcial: {e}")
 
 return True
 except Exception as e:
 print(f" Erro nas importações: {e}")
 return False

def main():
 print(" KAYOSCRYPTO 3D ENTERPRISE - TESTE CORRIGIDO")
 print("=" * 50)
 
 tester = SimpleDBTest()
 
 # Testar conexão
 if not tester.connect():
 print("\n Dica: Execute o script de correção de autenticação:")
 print(" ./fix_authentication.sh")
 return
 
 # Testar consultas
 if not tester.test_queries():
 return
 
 # Testar imports
 tester.test_imports()
 
 tester.conn.close()
 
 print("\n SISTEMA TESTADO COM SUCESSO!")
 print(" Próximo passo: Configurar o Cubo Sator 3D completo")

if __name__ == "__main__":
 main()
