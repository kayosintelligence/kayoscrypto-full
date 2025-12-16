"""
 CONFIGURAÇÃO DE BANCO DE DADOS ENTERPRISE
Configurações para PostgreSQL KayosCrypto 3D
"""

import os
from typing import Dict, Any

# Configurações principais do banco
DATABASE_CONFIG = {
 'default': {
 'dbname': 'k_crypto',
 'user': 'kayos', 
 'password': 'kayopass',
 'host': 'localhost',
 'port': 5432,
 'schema': 'kayos_enterprise'
 },
 
 'production': {
 'dbname': 'k_crypto_prod',
 'user': 'kayos_prod',
 'password': os.getenv('KAYOS_DB_PASSWORD', 'kayopass'),
 'host': os.getenv('DB_HOST', 'localhost'),
 'port': int(os.getenv('DB_PORT', 5432)),
 'schema': 'kayos_enterprise'
 },
 
 'replica': {
 'dbname': 'k_crypto',
 'user': 'kayos_readonly',
 'password': os.getenv('KAYOS_DB_PASSWORD_READONLY', 'kayopass'),
 'host': os.getenv('DB_REPLICA_HOST', 'localhost'),
 'port': int(os.getenv('DB_PORT', 5432)),
 'schema': 'kayos_enterprise'
 }
}

# Configurações de pool de conexões
CONNECTION_POOL_CONFIG = {
 'min_connections': 1,
 'max_connections': 20,
 'connection_timeout': 30,
 'retry_attempts': 3,
 'retry_delay': 1
}

# Configurações de performance
PERFORMANCE_CONFIG = {
 'statement_timeout': 30000, # 30 seconds
 'idle_in_transaction_session_timeout': 60000, # 60 seconds
 'lock_timeout': 10000 # 10 seconds
}

# Configurações de backup
BACKUP_CONFIG = {
 'enabled': True,
 'schedule': '0 2 * * *', # 2 AM daily
 'retention_days': 30,
 'encrypt_backups': True
}

# Configurações de monitoramento
MONITORING_CONFIG = {
 'slow_query_threshold_ms': 1000,
 'log_queries': True,
 'metrics_collection_interval': 60 # seconds
}

def get_database_url(environment: str = 'default') -> str:
 """Get database connection string for environment"""
 config = DATABASE_CONFIG[environment]
 return (
 f"dbname={config['dbname']} "
 f"user={config['user']} "
 f"password={config['password']} "
 f"host={config['host']} "
 f"port={config['port']}"
 )

def get_connection_params(environment: str = 'default') -> Dict[str, Any]:
 """Get connection parameters for psycopg2"""
 config = DATABASE_CONFIG[environment].copy()
 config['options'] = f"-c search_path={config.pop('schema', 'kayos_enterprise')}"
 return config
