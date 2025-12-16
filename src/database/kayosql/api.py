#!/usr/bin/env python3
"""
KAYOSQL API UNIFICADA

API principal para uso do KayosQL no KayosCrypto.
Agora com suporte ao KayosQL REAL (Rust via PyO3)!

BACKENDS:
1. RealKayosQL (Rust) - PREFERIDO
2. KayosQLNativeStorage (Python) - FALLBACK

Version: 2.0.0
"""

import os
import json
import hashlib
import threading
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Tentar importar KayosQL Real (Rust)
try:
    from .real_kayosql import RealKayosQL, is_kayosql_available, get_kayosql_info
    REAL_KAYOSQL_AVAILABLE = is_kayosql_available()
except ImportError:
    REAL_KAYOSQL_AVAILABLE = False
    RealKayosQL = None
    
    def get_kayosql_info():
        return {'available': False}

# Imports dos modulos KayosQL fallback
try:
    from .native_storage import KayosQLNativeStorage
    from .storage_backend import KayosQLStorageBackend
    from .quantum_tunnels import OptimizedQuantumTunnelManager
except ImportError:
    try:
        from native_storage import KayosQLNativeStorage
        from storage_backend import KayosQLStorageBackend
        from quantum_tunnels import OptimizedQuantumTunnelManager
    except ImportError:
        KayosQLNativeStorage = None
        KayosQLStorageBackend = None
        OptimizedQuantumTunnelManager = None


class KayosQL:
    """
    API unificada para KayosQL.
    
    Auto-seleciona o melhor backend disponivel:
    1. KayosQL Rust (se disponivel)
    2. KayosQL Native JSON (fallback)
    """
    
    def __init__(self, db_path: Optional[str] = None, force_native: bool = False):
        """
        Inicializa KayosQL.
        
        Args:
            db_path: Caminho para o banco de dados.
            force_native: Se True, usa backend nativo mesmo se Rust disponivel.
        """
        self._db_path = db_path
        self._use_rust = REAL_KAYOSQL_AVAILABLE and not force_native
        self._backend = None
        self._lock = threading.Lock()
        
        if self._use_rust:
            try:
                self._backend = RealKayosQL(db_path, enable_optimizations=True)
                self._backend_type = "KayosQL Rust"
                logger.info("Usando KayosQL Rust backend")
            except Exception as e:
                logger.warning(f"Falha ao iniciar Rust backend: {e}, usando fallback")
                self._use_rust = False
        
        if not self._use_rust:
            if KayosQLNativeStorage:
                self._backend = KayosQLNativeStorage(db_path)
                self._backend_type = "KayosQL Native (JSON)"
                logger.info("Usando KayosQL Native backend")
            else:
                raise RuntimeError("Nenhum backend KayosQL disponivel")
    
    @property
    def backend_type(self) -> str:
        return self._backend_type
    
    @property
    def supports_sql(self) -> bool:
        return self._use_rust
    
    @property
    def is_rust_backend(self) -> bool:
        return self._use_rust
    
    # === Interface de Storage (key-value) ===
    
    def store(self, key: str, value: bytes, metadata: Optional[Dict] = None) -> bool:
        """Armazena dados com chave."""
        with self._lock:
            if self._use_rust:
                table_name = "_kv_store"
                try:
                    self._backend.execute(f"""
                        CREATE TABLE IF NOT EXISTS {table_name} (
                            key TEXT PRIMARY KEY,
                            value BLOB,
                            metadata TEXT,
                            created_at TEXT
                        )
                    """)
                except:
                    pass
                
                meta_json = json.dumps(metadata) if metadata else '{}'
                now = datetime.now().isoformat()
                
                try:
                    self._backend.execute(f"DELETE FROM {table_name} WHERE key = '{key}'")
                except:
                    pass
                
                value_hex = value.hex()
                self._backend.execute(
                    f"INSERT INTO {table_name} (key, value, metadata, created_at) "
                    f"VALUES ('{key}', X'{value_hex}', '{meta_json}', '{now}')"
                )
                return True
            else:
                return self._backend.store(key, value, metadata)
    
    def retrieve(self, key: str) -> Optional[bytes]:
        """Recupera dados pela chave."""
        with self._lock:
            if self._use_rust:
                try:
                    rows = self._backend.query(f"SELECT value FROM _kv_store WHERE key = '{key}'")
                    if rows:
                        return bytes(rows[0]['value'])
                except:
                    pass
                return None
            else:
                return self._backend.retrieve(key)
    
    def delete(self, key: str) -> bool:
        """Remove dados pela chave."""
        with self._lock:
            if self._use_rust:
                try:
                    self._backend.execute(f"DELETE FROM _kv_store WHERE key = '{key}'")
                    return True
                except:
                    return False
            else:
                return self._backend.delete(key)
    
    def exists(self, key: str) -> bool:
        """Verifica se chave existe."""
        return self.retrieve(key) is not None
    
    def list_keys(self, prefix: Optional[str] = None) -> List[str]:
        """Lista chaves, opcionalmente com prefixo."""
        with self._lock:
            if self._use_rust:
                try:
                    if prefix:
                        rows = self._backend.query(f"SELECT key FROM _kv_store WHERE key LIKE '{prefix}%'")
                    else:
                        rows = self._backend.query("SELECT key FROM _kv_store")
                    return [row['key'] for row in rows]
                except:
                    return []
            else:
                return self._backend.list_keys(prefix)
    
    # === Interface SQL (apenas com backend Rust) ===
    
    def execute(self, sql: str) -> Dict[str, Any]:
        """Executa SQL (CREATE, INSERT, UPDATE, DELETE)."""
        if not self._use_rust:
            raise RuntimeError("SQL nao suportado com backend nativo")
        return self._backend.execute(sql)
    
    def query(self, sql: str) -> List[Dict[str, Any]]:
        """Executa SELECT e retorna resultados."""
        if not self._use_rust:
            raise RuntimeError("SQL nao suportado com backend nativo")
        return self._backend.query(sql)
    
    # === Metodos de conveniencia SQL ===
    
    def create_table(self, table_name: str, columns: Dict[str, str]) -> bool:
        """Cria tabela."""
        if not self._use_rust:
            raise RuntimeError("SQL nao suportado com backend nativo")
        return self._backend.create_table(table_name, columns)
    
    def insert(self, table_name: str, data: Dict[str, Any]) -> int:
        """Insere registro."""
        if not self._use_rust:
            raise RuntimeError("SQL nao suportado com backend nativo")
        return self._backend.insert(table_name, data)
    
    def batch_insert(self, table_name: str, records: List[Dict[str, Any]]) -> int:
        """Insere multiplos registros em batch."""
        if not self._use_rust:
            raise RuntimeError("SQL nao suportado com backend nativo")
        return self._backend.batch_insert(table_name, records)
    
    def select(self, table_name: str, columns: Optional[List[str]] = None,
               where: Optional[Dict[str, Any]] = None, order_by: Optional[str] = None,
               limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Seleciona dados."""
        if not self._use_rust:
            raise RuntimeError("SQL nao suportado com backend nativo")
        return self._backend.select(table_name, columns, where, order_by, limit)
    
    def update(self, table_name: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        """Atualiza registros."""
        if not self._use_rust:
            raise RuntimeError("SQL nao suportado com backend nativo")
        return self._backend.update(table_name, data, where)
    
    def delete_from(self, table_name: str, where: Dict[str, Any]) -> int:
        """Deleta registros."""
        if not self._use_rust:
            raise RuntimeError("SQL nao suportado com backend nativo")
        return self._backend.delete(table_name, where)
    
    # === Otimizacoes ===
    
    def create_index(self, table_name: str, column_name: str) -> bool:
        """Cria indice B+Tree."""
        if not self._use_rust:
            return False
        return self._backend.create_index(table_name, column_name)
    
    def cached_query(self, sql: str, ttl: Optional[float] = None) -> List[Dict[str, Any]]:
        """Query com cache."""
        if not self._use_rust:
            raise RuntimeError("SQL nao suportado com backend nativo")
        return self._backend.cached_query(sql, ttl)
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Retorna estatisticas de otimizacao."""
        if self._use_rust:
            return self._backend.get_stats()
        return {}
    
    # === Utilitarios ===
    
    def close(self):
        """Fecha conexao."""
        if self._backend:
            if hasattr(self._backend, 'close'):
                self._backend.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
    
    def __repr__(self):
        return f"KayosQL(backend='{self._backend_type}')"


# === Funcoes de conveniencia ===

def get_kayosql(db_path: Optional[str] = None) -> KayosQL:
    """Retorna instancia KayosQL."""
    return KayosQL(db_path)


def quick_store(key: str, value: bytes, db_path: Optional[str] = None) -> bool:
    """Armazena rapidamente."""
    with KayosQL(db_path) as db:
        return db.store(key, value)


def quick_retrieve(key: str, db_path: Optional[str] = None) -> Optional[bytes]:
    """Recupera rapidamente."""
    with KayosQL(db_path) as db:
        return db.retrieve(key)


# === Info ===

def get_backend_info() -> Dict[str, Any]:
    """Retorna informacoes sobre backends disponiveis."""
    info = get_kayosql_info()
    return {
        'rust_available': REAL_KAYOSQL_AVAILABLE,
        'native_available': KayosQLNativeStorage is not None,
        'preferred_backend': 'Rust' if REAL_KAYOSQL_AVAILABLE else 'Native',
        'rust_info': info
    }


if __name__ == '__main__':
    print("KayosQL API Test")
    print("-" * 40)
    
    info = get_backend_info()
    print(f"Rust disponivel: {info['rust_available']}")
    print(f"Native disponivel: {info['native_available']}")
    print(f"Backend preferido: {info['preferred_backend']}")
    
    print("\nTestando...")
    with KayosQL() as db:
        print(f"Backend: {db.backend_type}")
        
        # Test key-value
        db.store('test', b'hello world')
        result = db.retrieve('test')
        print(f"Store/Retrieve: {result}")
        
        if db.supports_sql:
            # Test SQL
            db.create_table('test_table', {'id': 'INTEGER PRIMARY KEY', 'name': 'TEXT'})
            db.insert('test_table', {'id': 1, 'name': 'Alice'})
            rows = db.select('test_table')
            print(f"SQL Select: {rows}")
    
    print("\nTeste concluido!")
