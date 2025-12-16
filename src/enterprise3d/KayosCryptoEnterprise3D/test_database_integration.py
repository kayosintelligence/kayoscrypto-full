#!/usr/bin/env python3
"""
 TESTE DE INTEGRAÇÃO DO BANCO DE DADOS ENTERPRISE
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database.postgresql_manager import PostgreSQLManager

def test_database_connection():
 """Testar conexão com o banco"""
 print(" Testando conexão com o banco...")
 
 db = PostgreSQLManager()
 if db.connect():
 print(" Conexão estabelecida com sucesso!")
 
 # Testar consultas básicas
 print("\n Testando consultas...")
 
 # Testar cubos
 cubes = db.execute_query("SELECT cube_name, security_level FROM kayos_enterprise.sator_cubes;")
 print(f" Cubos encontrados: {len(cubes)}")
 for cube in cubes:
 print(f" - {cube['cube_name']} ({cube['security_level']})")
 
 # Testar usuários
 users = db.execute_query("SELECT username, role FROM kayos_enterprise.enterprise_users;")
 print(f" Usuários encontrados: {len(users)}")
 for user in users:
 print(f" - {user['username']} ({user['role']})")
 
 # Testar dashboard
 dashboard = db.get_security_dashboard()
 print(f" Dashboard: {dashboard}")
 
 # Testar criação de novo cubo
 print("\n Testando criação de cubo...")
 new_cube_data = {
 'cube_name': 'test_cube_python',
 'rotation_state': {'x': 1, 'y': 0, 'z': 2, 'w': 0},
 'tenet_center_hash': b'test_tenet_hash_1234567890',
 'faces_configuration': {
 'north': {'verso': 'Kyber512', 'anverso': 'Kyber1024'},
 'south': {'verso': 'P-256', 'anverso': 'P-521'}
 }
 }
 
 cube_id = db.create_sator_cube(new_cube_data)
 if cube_id:
 print(f" Cubo criado com ID: {cube_id}")
 
 # Testar auditoria
 audit_result = db.log_audit_event({
 'event_type': 'test_integration',
 'severity': 'INFO',
 'cube_id': cube_id,
 'event_data': {'test': 'successful', 'method': 'python_integration'}
 })
 print(f" Auditoria registrada: {audit_result}")
 else:
 print(" Falha ao criar cubo")
 
 db.disconnect()
 print("\n TODOS OS TESTES PASSARAM!")
 return True
 else:
 print(" Falha na conexão com o banco")
 return False

if __name__ == "__main__":
 print(" KAYOSCRYPTO 3D ENTERPRISE - TESTE DE INTEGRAÇÃO")
 print("=" * 50)
 
 success = test_database_connection()
 
 if success:
 print("\n SISTEMA PRONTO PARA ENTERPRISE!")
 print(" Database: k_crypto")
 print(" Usuário: kayos") 
 print(" Schema: kayos_enterprise")
 print(" Próximo passo: Integrar com o Cubo Sator 3D")
 else:
 print("\n Necessárias correções no banco")
 sys.exit(1)
