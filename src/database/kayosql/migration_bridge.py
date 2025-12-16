#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STORAGE MIGRATION BRIDGE
========================

Bridge para migração gradual de SQLite para KayosQL nativo.
Permite operação dual durante transição.

Características:
- Migração transparente
- Dual-write durante transição
- Fallback automático
- Migração automática de dados antigos
"""

import threading
from typing import Optional

try:
    from native_storage import KayosQLNativeStorage
except ImportError:
    # Fallback para import relativo se absoluto falhar
    try:
        from .native_storage import KayosQLNativeStorage
    except ImportError:
        # Classe mock se não conseguir importar
        class KayosQLNativeStorage:
            pass

class SQLiteCompatibilityStorage:
    """Stub para compatibilidade com SQLite - implementar conforme necessário"""
    def store_encrypted_data(self, data_id: str, encrypted_data: bytes, tunnel_id: str) -> bool:
        # TODO: Implementar armazenamento SQLite
        return True

    def retrieve_encrypted_data(self, data_id: str) -> Optional[bytes]:
        # TODO: Implementar recuperação SQLite
        return None

class StorageMigrationBridge:
    """
    Bridge para migração gradual entre sistemas de armazenamento.
    """

    def __init__(self):
        self.sqlite_storage = SQLiteCompatibilityStorage()
        self.native_storage = KayosQLNativeStorage()
        self.migration_complete = False
        self._lock = threading.RLock()

    def store_data(self, data_id: str, encrypted_data: bytes, tunnel_id: str) -> bool:
        """
        Armazena em ambos os sistemas durante transição.

        Args:
            data_id: ID dos dados
            encrypted_data: Dados criptografados
            tunnel_id: ID do túnel

        Returns:
            bool: True se armazenado com sucesso
        """
        with self._lock:
            # Primeiro no nativo (prioridade)
            native_success = self.native_storage.store_encrypted_data(
                data_id, encrypted_data, tunnel_id
            )

            # Depois no SQLite (fallback)
            sqlite_success = self.sqlite_storage.store_encrypted_data(
                data_id, encrypted_data, tunnel_id
            )

            return native_success and sqlite_success

    def retrieve_data(self, data_id: str) -> Optional[bytes]:
        """
        Recupera do nativo primeiro, com fallback para SQLite.

        Args:
            data_id: ID dos dados

        Returns:
            bytes: Dados recuperados ou None
        """
        with self._lock:
            # Tentar nativo primeiro
            data = self.native_storage.retrieve_encrypted_data(data_id)
            if data:
                return data

            # Fallback para SQLite
            data = self.sqlite_storage.retrieve_encrypted_data(data_id)
            if data:
                # Migrar automaticamente para nativo
                self.native_storage.store_encrypted_data(data_id, data, "migrated")
                return data

            return None

    def complete_migration(self):
        """
        Completa migração desativando SQLite.
        """
        with self._lock:
            self.migration_complete = True
            # Manter SQLite como backup por algum tempo

    def get_migration_stats(self) -> dict:
        """
        Retorna estatísticas da migração.

        Returns:
            dict: Estatísticas de migração
        """
        native_metrics = self.native_storage.get_performance_metrics()

        return {
            "migration_complete": self.migration_complete,
            "native_records": native_metrics["total_records"],
            "database_size_mb": native_metrics["database_size_mb"]
        }