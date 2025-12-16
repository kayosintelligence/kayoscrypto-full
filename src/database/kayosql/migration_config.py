"""
 KAYOSCRYPTO → KAYOSQL MIGRATION CONFIGURATION
Configuração da migração do KayosCrypto para usar KayosQL como backend
Data: 30 de novembro de 2025
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

class KayosQLMigrationConfig:
    """Configuração da migração KayosCrypto → KayosQL"""

    def __init__(self):
        # Caminhos para KayosQL
        self.kayosql_root = Path("/home/kbe/KAYOS_SYSTEMS/KayosQL")
        self.kayosql_bridge = self.kayosql_root / "enterprise/core/src/crypto/kayoscrypto_bridge.py"
        self.kayosql_engine = self.kayosql_root / "kayos_engineer"

        # Configurações de migração
        self.migration_phases = {
            "phase_1": "database_layer",      # Camada de banco de dados
            "phase_2": "crypto_engine",       # Motor criptográfico
            "phase_3": "storage_backend",     # Backend de armazenamento
            "phase_4": "quantum_features",    # Recursos quânticos
            "phase_5": "enterprise_features"  # Recursos enterprise
        }

        # Status da migração
        self.migration_status = {
            "database_layer": False,
            "crypto_engine": False,
            "storage_backend": False,
            "quantum_features": False,
            "enterprise_features": False
        }

        # Configurações de compatibilidade
        self.compatibility_mode = True  # Mantém compatibilidade com APIs existentes
        self.fallback_to_sqlite = False  #  ELIMINADO: Não usar SQLite/PostgreSQL
        self.use_proprietary_storage = True  #  Usar sistema proprietário KayosQL

        # Configurações de performance
        self.performance_targets = {
            "inserts_per_sec": 200000,  # Target: 200K inserts/seg (KayosQL)
            "lookups_per_sec": 130000,  # Target: 130K lookups/seg (KayosQL)
            "quantum_ops_per_sec": 9000000  # Target: 9M ops/seg (GPS 3D)
        }

    def is_kayosql_available(self) -> bool:
        """Verifica se KayosQL está disponível"""
        try:
            from .enterprise_integration import KAYOSQL_AVAILABLE
            return KAYOSQL_AVAILABLE
        except ImportError:
            return False

    def get_bridge_path(self) -> Optional[Path]:
        """Retorna caminho para o bridge KayosCrypto"""
        return self.kayosql_bridge if self.kayosql_bridge.exists() else None

    def get_migration_status(self) -> Dict[str, bool]:
        """Retorna status atual da migração"""
        return self.migration_status.copy()

    def update_migration_status(self, phase: str, completed: bool):
        """Atualiza status de uma fase da migração"""
        if phase in self.migration_status:
            self.migration_status[phase] = completed
            print(f" Fase '{phase}' da migração: {'CONCLUÍDA' if completed else 'PENDENTE'}")

    def get_migration_progress(self) -> Dict[str, Any]:
        """Retorna progresso geral da migração"""
        completed_phases = sum(1 for status in self.migration_status.values() if status)
        total_phases = len(self.migration_status)

        return {
            "completed_phases": completed_phases,
            "total_phases": total_phases,
            "progress_percentage": (completed_phases / total_phases) * 100,
            "phase_details": self.migration_status.copy()
        }

# Instância global da configuração
migration_config = KayosQLMigrationConfig()

def get_migration_config() -> KayosQLMigrationConfig:
    """Retorna instância da configuração de migração"""
    return migration_config

def check_migration_readiness() -> Dict[str, Any]:
    """Verifica prontidão para migração"""
    config = get_migration_config()

    readiness_check = {
        "kayosql_available": config.is_kayosql_available(),
        "bridge_exists": config.get_bridge_path() is not None,
        "migration_config_loaded": True,
        "compatibility_mode": config.compatibility_mode,
        "fallback_available": config.fallback_to_sqlite
    }

    # Verificação de dependências críticas
    readiness_check["critical_dependencies"] = {
        "kayoscrypto_bridge": config.kayosql_bridge.exists(),
        "kayosql_engine": config.kayosql_engine.exists(),
        "migration_directory": Path("src/database/kayosql").exists()
    }

    return readiness_check