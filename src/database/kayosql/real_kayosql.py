"""
KayosQL Real - Wrapper para o KayosQL Rust via PyO3

Este modulo conecta ao KayosQL REAL (implementado em Rust) via os bindings kayosdrivers.
E DIFERENTE do native_storage.py que usa apenas JSON.

Funcionalidades REAIS do KayosQL:
- SATOR HyperCube Index (O(1) lookups)
- B+Tree Index (ORDER=128, range scans)
- WAL (Write-Ahead Log) com LZ4 compression
- MVCC (Multi-Version Concurrency Control)
- Full SQL Parser
- Constraints (PRIMARY KEY, UNIQUE, FOREIGN KEY, CHECK)
- Triggers, Views, Sequences

OTIMIZACOES v2.0 (superar PostgreSQL):
- Batch INSERT: Combina multiplos INSERTs em uma transacao
- Auto-Index: Cria indices automaticamente em colunas WHERE frequentes
- Query Cache: Cache de queries preparadas no lado Python
- Bulk Operations: INSERT/UPDATE/DELETE em batch

Author: KAIOS Systems
Version: 2.0.0
"""

import os
import tempfile
import hashlib
import time
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
from collections import defaultdict
from threading import Lock

try:
    import kayosdrivers
    KAYOSQL_AVAILABLE = True
except ImportError:
    KAYOSQL_AVAILABLE = False
    kayosdrivers = None


class KayosQLConnectionError(Exception):
    pass


class KayosQLExecutionError(Exception):
    pass


class RealKayosQL:
    """Wrapper para KayosQL Rust via PyO3."""
    
    _query_cache: Dict[str, Tuple[float, Any]] = {}
    _cache_lock = Lock()
    _cache_ttl = 60.0
    _cache_max_size = 1000
    _where_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    _auto_index_threshold = 10
    
    def __init__(self, db_path: Optional[str] = None, enable_optimizations: bool = True):
        if not KAYOSQL_AVAILABLE:
            raise KayosQLConnectionError("KayosQL (Rust) nao disponivel")
        
        if db_path is None:
            db_path = os.path.join(tempfile.mkdtemp(), 'kayoscrypto.kayos')
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            self._engine = kayosdrivers.Engine(str(self.db_path))
        except Exception as e:
            raise KayosQLConnectionError(f"Falha ao criar Engine: {e}")
        
        self._initialized = True
        self._enable_optimizations = enable_optimizations
        self._created_indexes: set = set()
        self._batch_buffer: List[str] = []
        self._batch_size = 100
    
    @property
    def version(self) -> str:
        return "7.0.0"
    
    @property
    def engine_type(self) -> str:
        return "KayosQL Rust"
    
    @property
    def is_real_kayosql(self) -> bool:
        return True
    
    def execute(self, sql: str) -> Dict[str, Any]:
        try:
            result = self._engine.execute(sql)
            return {
                'type': result.result_type(),
                'rows_affected': result.row_count(),
                'table_name': result.table_name(),
                'raw': str(result)
            }
        except SyntaxError as e:
            raise KayosQLExecutionError(f"Erro de sintaxe SQL: {e}")
        except Exception as e:
            raise KayosQLExecutionError(f"Erro de execucao: {e}")
    
    def query(self, sql: str) -> List[Dict[str, Any]]:
        try:
            rows = self._engine.query(sql)
            return [dict(row) for row in rows]
        except TypeError as e:
            raise KayosQLExecutionError(f"Use execute() para comandos nao-SELECT: {e}")
        except SyntaxError as e:
            raise KayosQLExecutionError(f"Erro de sintaxe SQL: {e}")
        except Exception as e:
            raise KayosQLExecutionError(f"Erro de query: {e}")
    
    def stats(self) -> Dict[str, Any]:
        try:
            return dict(self._engine.stats())
        except Exception:
            return {'version': self.version, 'engine': self.engine_type, 'db_path': str(self.db_path)}
    
    # === Metodos de conveniencia ===
    
    def create_table(self, table_name: str, columns: Dict[str, str]) -> bool:
        cols = ', '.join(f'{name} {typ}' for name, typ in columns.items())
        sql = f'CREATE TABLE IF NOT EXISTS {table_name} ({cols})'
        try:
            result = self.execute(sql)
            return result['type'] == 'created'
        except KayosQLExecutionError as e:
            if 'already exists' in str(e).lower():
                return False
            raise
    
    def insert(self, table_name: str, data: Dict[str, Any]) -> int:
        columns = ', '.join(data.keys())
        placeholders = ', '.join(self._format_value(v) for v in data.values())
        sql = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
        result = self.execute(sql)
        return result['rows_affected']
    
    # === OTIMIZACOES v2.0 ===
    
    def batch_insert(self, table_name: str, records: List[Dict[str, Any]]) -> int:
        """Insere multiplos registros em uma transacao."""
        if not records:
            return 0
        
        total_inserted = 0
        try:
            self._engine.execute("BEGIN")
            for record in records:
                columns = ', '.join(record.keys())
                values = ', '.join(self._format_value(v) for v in record.values())
                sql = f'INSERT INTO {table_name} ({columns}) VALUES ({values})'
                result = self._engine.execute(sql)
                total_inserted += result.row_count()
            self._engine.execute("COMMIT")
        except Exception as e:
            try:
                self._engine.execute("ROLLBACK")
            except:
                pass
            raise KayosQLExecutionError(f"Batch insert falhou: {e}")
        return total_inserted
    
    def create_index(self, table_name: str, column_name: str, index_name: Optional[str] = None) -> bool:
        """Cria indice B+Tree em uma coluna."""
        if index_name is None:
            index_name = f"idx_{table_name}_{column_name}"
        
        index_key = f"{table_name}.{column_name}"
        if index_key in self._created_indexes:
            return False
        
        try:
            sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({column_name})"
            self.execute(sql)
            self._created_indexes.add(index_key)
            return True
        except KayosQLExecutionError as e:
            if 'already exists' in str(e).lower():
                self._created_indexes.add(index_key)
                return False
            raise
    
    def auto_index(self, table_name: str, column_name: str) -> bool:
        """Cria indice automaticamente se coluna for frequentemente usada em WHERE."""
        if not self._enable_optimizations:
            return False
        
        RealKayosQL._where_stats[table_name][column_name] += 1
        count = RealKayosQL._where_stats[table_name][column_name]
        
        if count >= self._auto_index_threshold:
            index_key = f"{table_name}.{column_name}"
            if index_key not in self._created_indexes:
                return self.create_index(table_name, column_name)
        return False
    
    def cached_query(self, sql: str, ttl: Optional[float] = None) -> List[Dict[str, Any]]:
        """Executa SELECT com cache local."""
        if ttl is None:
            ttl = self._cache_ttl
        
        cache_key = hashlib.md5(sql.encode()).hexdigest()
        
        with self._cache_lock:
            if cache_key in RealKayosQL._query_cache:
                timestamp, result = RealKayosQL._query_cache[cache_key]
                if time.time() - timestamp < ttl:
                    return result
        
        result = self.query(sql)
        
        with self._cache_lock:
            if len(RealKayosQL._query_cache) >= self._cache_max_size:
                sorted_keys = sorted(
                    RealKayosQL._query_cache.keys(),
                    key=lambda k: RealKayosQL._query_cache[k][0]
                )
                for k in sorted_keys[:self._cache_max_size // 5]:
                    del RealKayosQL._query_cache[k]
            RealKayosQL._query_cache[cache_key] = (time.time(), result)
        
        return result
    
    def invalidate_cache(self, table_name: Optional[str] = None):
        """Invalida cache de queries."""
        with self._cache_lock:
            RealKayosQL._query_cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatisticas de otimizacao."""
        return {
            'cache_size': len(RealKayosQL._query_cache),
            'cache_max_size': self._cache_max_size,
            'cache_ttl': self._cache_ttl,
            'indexes_created': list(self._created_indexes),
            'where_stats': dict(RealKayosQL._where_stats),
            'auto_index_threshold': self._auto_index_threshold,
            'optimizations_enabled': self._enable_optimizations
        }
    
    def select(self, table_name: str, columns: Optional[List[str]] = None,
               where: Optional[Dict[str, Any]] = None, order_by: Optional[str] = None,
               limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Seleciona dados de uma tabela."""
        if where and self._enable_optimizations:
            for col in where.keys():
                self.auto_index(table_name, col)
        
        cols = '*' if columns is None else ', '.join(columns)
        sql = f'SELECT {cols} FROM {table_name}'
        
        if where:
            conditions = ' AND '.join(f'{k} = {self._format_value(v)}' for k, v in where.items())
            sql += f' WHERE {conditions}'
        
        if order_by:
            sql += f' ORDER BY {order_by}'
        
        if limit:
            sql += f' LIMIT {limit}'
        
        return self.query(sql)
    
    def update(self, table_name: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        """Atualiza dados em uma tabela."""
        updates = ', '.join(f'{k} = {self._format_value(v)}' for k, v in data.items())
        conditions = ' AND '.join(f'{k} = {self._format_value(v)}' for k, v in where.items())
        sql = f'UPDATE {table_name} SET {updates} WHERE {conditions}'
        result = self.execute(sql)
        return result['rows_affected']
    
    def delete(self, table_name: str, where: Dict[str, Any]) -> int:
        """Deleta dados de uma tabela."""
        conditions = ' AND '.join(f'{k} = {self._format_value(v)}' for k, v in where.items())
        sql = f'DELETE FROM {table_name} WHERE {conditions}'
        result = self.execute(sql)
        return result['rows_affected']
    
    @staticmethod
    def _format_value(value: Any) -> str:
        """Formata valor Python para SQL."""
        if value is None:
            return 'NULL'
        elif isinstance(value, bool):
            return 'TRUE' if value else 'FALSE'
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            escaped = value.replace("'", "''")
            return f"'{escaped}'"
        elif isinstance(value, bytes):
            return f"X'{value.hex()}'"
        else:
            return f"'{str(value)}'"
    
    def close(self):
        self._initialized = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
    
    def __repr__(self):
        return f"RealKayosQL(db_path='{self.db_path}', engine='{self.engine_type}')"


def is_kayosql_available() -> bool:
    return KAYOSQL_AVAILABLE


def get_kayosql_info() -> Dict[str, Any]:
    if KAYOSQL_AVAILABLE:
        return {
            'available': True,
            'type': 'Rust (via PyO3)',
            'module': 'kayosdrivers',
            'version': '7.0.0',
            'features': ['SATOR HyperCube Index', 'B+Tree Index', 'WAL with LZ4', 'MVCC', 'Full SQL Parser']
        }
    return {
        'available': False,
        'type': None,
        'module': None,
        'version': None,
        'features': [],
        'install_hint': 'cd KayosQL/py && pip install -e .'
    }


if __name__ == '__main__':
    print("Verificando KayosQL...")
    info = get_kayosql_info()
    
    if info['available']:
        print(f"KayosQL disponivel: {info['type']} v{info['version']}")
        
        print("\nExecutando teste rapido...")
        with RealKayosQL() as db:
            db.create_table('test', {'id': 'INTEGER PRIMARY KEY', 'value': 'TEXT'})
            db.insert('test', {'id': 1, 'value': 'hello'})
            rows = db.select('test')
            print(f"Resultado: {rows}")
            print("Teste passou!")
    else:
        print(f"KayosQL nao disponivel")
        print(f"Instalacao: {info['install_hint']}")
