"""
 PostgreSQL MANAGER ENTERPRISE
Gerenciamento do banco de dados KayosCrypto 3D Enterprise
"""

import logging
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime, timedelta
import json


class PostgreSQLManager:
 """
 Gerenciador Enterprise do PostgreSQL para KayosCrypto 3D
 """
 
 def __init__(self, connection_string: str = None):
 self.connection_string = connection_string or self._get_default_connection()
 self.logger = logging.getLogger(__name__)
 self._connection = None

 def _get_default_connection(self) -> str:
 """String de conexão padrão para KayosCrypto"""
 return (
 "dbname=k_crypto user=kayos password=kayopass "
 "host=localhost port=5432"
 )

 def connect(self):
 """Estabelecer conexão com o banco"""
 try:
 self._connection = psycopg2.connect(
 self.connection_string,
 cursor_factory=RealDictCursor
 )
 self._connection.autocommit = False
 self.logger.info(" Conectado ao PostgreSQL - KayosCrypto 3D Enterprise")
 return True
 
 except Exception as e:
 self.logger.error(f" Falha na conexão PostgreSQL: {e}")
 return False

 def disconnect(self):
 """Fechar conexão"""
 if self._connection:
 self._connection.close()
 self.logger.info(" Conexão PostgreSQL fechada")

 def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
 """Executar query e retornar resultados"""
 try:
 with self._connection.cursor() as cursor:
 cursor.execute(query, params)
 if query.strip().upper().startswith('SELECT'):
 return cursor.fetchall()
 else:
 self._connection.commit()
 return []
 
 except Exception as e:
 self._connection.rollback()
 self.logger.error(f" Erro na query: {e}")
 raise

 # OPERAÇÕES DO CUBO SATOR 3D

 def create_sator_cube(self, cube_data: Dict) -> Optional[str]:
 """Criar novo Cubo Sator 3D no banco"""
 try:
 cube_id = str(uuid.uuid4())
 
 query = """
 INSERT INTO kayos_enterprise.sator_cubes 
 (cube_id, cube_name, security_level, current_rotation_state, 
 tenet_center_hash, faces_configuration, created_by)
 VALUES (%s, %s, %s, %s, %s, %s, %s)
 RETURNING cube_id
 """
 
 result = self.execute_query(query, (
 cube_id,
 cube_data['cube_name'],
 cube_data.get('security_level', 'enterprise'),
 Json(cube_data['rotation_state']),
 cube_data['tenet_center_hash'],
 Json(cube_data['faces_configuration']),
 cube_data.get('created_by', 'system')
 ))
 
 self.logger.info(f" Cubo Sator criado: {cube_data['cube_name']}")
 return cube_id
 
 except Exception as e:
 self.logger.error(f" Falha ao criar cubo: {e}")
 return None

 def get_cube_by_name(self, cube_name: str) -> Optional[Dict]:
 """Buscar cubo pelo nome"""
 try:
 query = """
 SELECT * FROM kayos_enterprise.sator_cubes 
 WHERE cube_name = %s AND is_active = true
 """
 
 result = self.execute_query(query, (cube_name,))
 return result[0] if result else None
 
 except Exception as e:
 self.logger.error(f" Falha ao buscar cubo: {e}")
 return None

 def update_cube_rotation(self, cube_id: str, rotation_state: Dict) -> bool:
 """Atualizar estado de rotação do cubo"""
 try:
 # Registrar no histórico
 rotation_history_query = """
 INSERT INTO kayos_enterprise.cube_rotation_history 
 (cube_id, rotation_sequence, axes_rotated, previous_state, new_state, tenet_signature)
 VALUES (%s, %s, %s, %s, %s, %s)
 """
 
 # Atualizar cubo
 update_cube_query = """
 UPDATE kayos_enterprise.sator_cubes 
 SET current_rotation_state = %s, rotation_count = rotation_count + 1, updated_at = NOW()
 WHERE cube_id = %s
 """
 
 self.execute_query(rotation_history_query, (
 cube_id,
 Json(rotation_state['rotation_sequence']),
 Json(rotation_state['axes_rotated']),
 Json(rotation_state.get('previous_state', {})),
 Json(rotation_state['new_state']),
 rotation_state['tenet_signature']
 ))
 
 self.execute_query(update_cube_query, (
 Json(rotation_state['new_state']),
 cube_id
 ))
 
 self.logger.info(f" Rotações do cubo {cube_id} atualizadas")
 return True
 
 except Exception as e:
 self.logger.error(f" Falha ao atualizar rotação: {e}")
 return False

 # OPERAÇÕES DE CHAVES 4D

 def store_4d_key_material(self, key_material: Dict) -> Optional[str]:
 """Armazenar material de chaves 4D no banco"""
 try:
 key_id = str(uuid.uuid4())
 
 query = """
 INSERT INTO kayos_enterprise.cryptographic_keys_4d 
 (key_id, cube_id, meeting_point_data, master_secret_encrypted,
 kyber_public_key, kyber_secret_encrypted, ecc_public_key_pem,
 key_size_bits, algorithm_combination, security_level, hsm_provider)
 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
 RETURNING key_id
 """
 
 result = self.execute_query(query, (
 key_id,
 key_material['cube_id'],
 Json(key_material['meeting_point']),
 key_material['master_secret_encrypted'],
 key_material.get('kyber_public_key'),
 key_material.get('kyber_secret_encrypted'),
 key_material.get('ecc_public_key_pem'),
 key_material['key_size_bits'],
 key_material['algorithm_combination'],
 key_material['security_level'],
 key_material.get('hsm_provider')
 ))
 
 # Configurar rotação automática
 rotation_days = 90 # Padrão enterprise
 next_rotation = datetime.now() + timedelta(days=rotation_days)
 
 rotation_query = """
 INSERT INTO kayos_enterprise.key_rotation_schedule
 (key_id, rotation_interval_days, next_rotation_at)
 VALUES (%s, %s, %s)
 """
 
 self.execute_query(rotation_query, (key_id, rotation_days, next_rotation))
 
 self.logger.info(f" Chave 4D armazenada: {key_id}")
 return key_id
 
 except Exception as e:
 self.logger.error(f" Falha ao armazenar chave: {e}")
 return None

 def get_active_keys_for_cube(self, cube_id: str) -> List[Dict]:
 """Buscar chaves ativas para um cubo"""
 try:
 query = """
 SELECT * FROM kayos_enterprise.cryptographic_keys_4d 
 WHERE cube_id = %s AND is_active = true
 ORDER BY generated_at DESC
 """
 
 return self.execute_query(query, (cube_id,))
 
 except Exception as e:
 self.logger.error(f" Falha ao buscar chaves: {e}")
 return []

 # OPERAÇÕES DE CRIPTOGRAFIA

 def log_crypto_operation(self, operation_data: Dict) -> bool:
 """Registrar operação criptográfica para auditoria"""
 try:
 operation_id = str(uuid.uuid4())
 
 query = """
 INSERT INTO kayos_enterprise.crypto_operations 
 (operation_id, key_id, cube_id, operation_type, 
 cube_rotation_state, tenet_signature, operation_duration_ms,
 data_size_bytes, client_ip, user_agent, status)
 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
 """
 
 self.execute_query(query, (
 operation_id,
 operation_data['key_id'],
 operation_data['cube_id'],
 operation_data['operation_type'],
 Json(operation_data['cube_rotation_state']),
 operation_data['tenet_signature'],
 operation_data.get('operation_duration_ms'),
 operation_data.get('data_size_bytes'),
 operation_data.get('client_ip'),
 operation_data.get('user_agent'),
 operation_data.get('status', 'completed')
 ))
 
 self.logger.info(f" Operação {operation_data['operation_type']} registrada")
 return True
 
 except Exception as e:
 self.logger.error(f" Falha ao registrar operação: {e}")
 return False

 def store_encrypted_payload(self, payload_data: Dict) -> Optional[str]:
 """Armazenar payload criptografado no banco"""
 try:
 payload_id = str(uuid.uuid4())
 
 query = """
 INSERT INTO kayos_enterprise.encrypted_payloads_3d 
 (payload_id, key_id, cube_id, ciphertext, metadata_encrypted,
 encryption_algorithm, security_level, access_policy)
 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
 RETURNING payload_id
 """
 
 result = self.execute_query(query, (
 payload_id,
 payload_data['key_id'],
 payload_data['cube_id'],
 payload_data['ciphertext'],
 payload_data['metadata_encrypted'],
 payload_data['encryption_algorithm'],
 payload_data['security_level'],
 Json(payload_data.get('access_policy', {}))
 ))
 
 self.logger.info(f" Payload criptografado armazenado: {payload_id}")
 return payload_id
 
 except Exception as e:
 self.logger.error(f" Falha ao armazenar payload: {e}")
 return None

 # OPERAÇÕES DE MONITORING

 def get_security_dashboard(self) -> Dict:
 """Obter dados para dashboard de segurança"""
 try:
 query = "SELECT * FROM kayos_enterprise.security_dashboard"
 result = self.execute_query(query)
 return result[0] if result else {}
 
 except Exception as e:
 self.logger.error(f" Falha ao buscar dashboard: {e}")
 return {}

 def get_compliance_report(self) -> List[Dict]:
 """Obter relatório de compliance"""
 try:
 query = "SELECT * FROM kayos_enterprise.compliance_report"
 return self.execute_query(query)
 
 except Exception as e:
 self.logger.error(f" Falha ao buscar relatório: {e}")
 return []

 # OPERAÇÕES DE AUDITORIA

 def log_audit_event(self, event_data: Dict) -> bool:
 """Registrar evento de auditoria"""
 try:
 audit_id = str(uuid.uuid4())
 
 query = """
 INSERT INTO kayos_enterprise.audit_trail 
 (audit_id, event_type, severity, user_id, cube_id, key_id,
 event_data, event_hash, client_ip, user_agent)
 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
 """
 
 # Calcular hash do evento
 import hashlib
 event_hash = hashlib.sha256(json.dumps(event_data).encode()).digest()
 
 self.execute_query(query, (
 audit_id,
 event_data['event_type'],
 event_data.get('severity', 'INFO'),
 event_data.get('user_id'),
 event_data.get('cube_id'),
 event_data.get('key_id'),
 Json(event_data),
 event_hash,
 event_data.get('client_ip'),
 event_data.get('user_agent')
 ))
 
 self.logger.info(f" Evento de auditoria registrado: {event_data['event_type']}")
 return True
 
 except Exception as e:
 self.logger.error(f" Falha ao registrar auditoria: {e}")
 return False

 # OPERAÇÕES DE MANUTENÇÃO

 def rotate_expired_keys(self) -> int:
 """Rotacionar chaves expiradas (automático)"""
 try:
 # Buscar chaves para rotacionar
 query = """
 SELECT key_id, cube_id FROM kayos_enterprise.cryptographic_keys_4d 
 WHERE expires_at < NOW() AND is_active = true
 """
 
 expired_keys = self.execute_query(query)
 rotated_count = 0
 
 for key in expired_keys:
 # Marcar chave como inativa
 update_query = """
 UPDATE kayos_enterprise.cryptographic_keys_4d 
 SET is_active = false 
 WHERE key_id = %s
 """
 self.execute_query(update_query, (key['key_id'],))
 
 # Registrar evento
 self.log_audit_event({
 'event_type': 'key_rotation_auto',
 'severity': 'INFO',
 'key_id': key['key_id'],
 'cube_id': key['cube_id'],
 'event_data': {'reason': 'expiration', 'auto_rotated': True}
 })
 
 rotated_count += 1
 
 self.logger.info(f" {rotated_count} chaves expiradas rotacionadas")
 return rotated_count
 
 except Exception as e:
 self.logger.error(f" Falha na rotação automática: {e}")
 return 0


# Exemplo de uso Enterprise
if __name__ == "__main__":
 # Configurar logging
 logging.basicConfig(level=logging.INFO)
 
 # Conectar ao banco
 db_manager = PostgreSQLManager()
 if db_manager.connect():
 print(" Conectado ao KayosCrypto 3D Enterprise Database")
 
 # Testar dashboard
 dashboard = db_manager.get_security_dashboard()
 print(f" Dashboard: {dashboard}")
 
 # Testar compliance
 compliance = db_manager.get_compliance_report()
 print(f" Compliance: {len(compliance)} registros")
 
 db_manager.disconnect()
 else:
 print(" Falha na conexão com o banco")
