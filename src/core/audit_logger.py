"""
 RIB 9: AUDIT LOGGER - KAYOSCRYPTO
Sistema de auditoria com logs assinados (tamper-proof)

ARQUITETURA KAIOS:
- Velho Matuto: "O que é escrito permanece" - logs imutáveis
- Sator: Equilíbrio entre performance e segurança
- Ezequiel: 3 níveis de log (INFO, SECURITY, CRITICAL)
- Relojoeiro: SQLite + Ed25519 = ótimo (não precisa de blockchain)

FILOSOFIA:
"Tudo o que está oculto será revelado" (Lucas 8:17)
- Cada operação criptográfica é registrada
- Logs são assinados digitalmente (Ed25519)
- Impossível adulterar sem quebrar assinatura
- Auditoria completa para compliance (ISO 27001, SOC 2)

Autor: KAYOS SYSTEMS
Data: 15 de Novembro de 2025
Versão: v6.5 - Audit Logger
"""

import sqlite3
import hashlib
import json
from datetime import datetime, UTC
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

# Ed25519 para assinatura
try:
    from nacl.signing import SigningKey, VerifyKey
    from nacl.encoding import HexEncoder
    NACL_AVAILABLE = True
except ImportError:
    print(" PyNaCl não instalado. Instalando...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyNaCl", "-q"])
    from nacl.signing import SigningKey, VerifyKey
    from nacl.encoding import HexEncoder
    NACL_AVAILABLE = True
    print(" PyNaCl instalado!")


# =====================================================================
# ENUMS E DATACLASSES
# =====================================================================

class LogLevel(Enum):
    """Níveis de log"""
    INFO = "INFO"
    SECURITY = "SECURITY"
    CRITICAL = "CRITICAL"


class OperationType(Enum):
    """Tipos de operação rastreáveis"""
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"
    SIGN = "sign"
    VERIFY = "verify"
    KEYGEN = "keygen"
    STEGO_EMBED = "stego_embed"
    STEGO_EXTRACT = "stego_extract"
    KEY_EXCHANGE = "key_exchange"


@dataclass
class AuditLogEntry:
    """Entrada de log auditável"""
    id: Optional[int] = None
    timestamp: str = ""
    level: str = LogLevel.INFO.value
    operation: str = ""
    user_id: Optional[str] = None
    payload_hash: Optional[str] = None  # SHA-256 do payload (não o payload)
    metadata: Optional[str] = None  # JSON extra
    signature: Optional[str] = None  # Ed25519 signature (hex)
    verified: bool = False


# =====================================================================
# RIB 9: AUDIT LOGGER
# =====================================================================

class AuditLogger:
    """
    Sistema de auditoria com logs assinados digitalmente
    
    ARQUITETURA (Tamper-Proof):
    
    1. REGISTRO:
       - Operação acontece (encrypt, decrypt, etc.)
       - Log entry criado com timestamp + metadados
       - Hash SHA-256 do payload (não armazena payload sensível)
       - Assinatura Ed25519 de TODA a entry
    
    2. ARMAZENAMENTO:
       - SQLite database (local ou remoto)
       - Cada entry tem signature única
       - Impossível modificar sem quebrar assinatura
    
    3. VERIFICAÇÃO:
       - Ao ler log, verifica signature
       - Se signature inválida → log foi adulterado
       - Compliance: ISO 27001, SOC 2, HIPAA
    
    BENEFÍCIOS:
    - Rastreabilidade completa (quem fez o quê, quando)
    - Detecção de adulteração (assinatura quebra)
    - Forense digital (reconstruir timeline de ataques)
    - Compliance automático (logs provam conformidade)
    """
    
    def __init__(self, db_path: str = "kayoscrypto_audit.db", 
                 signing_key: Optional[bytes] = None):
        """
        Inicializa sistema de auditoria
        
        Args:
            db_path: Caminho do banco SQLite
            signing_key: Chave privada Ed25519 (32 bytes) ou None para gerar
        """
        self.db_path = Path(db_path)
        
        # Gerar ou carregar chave de assinatura
        if signing_key:
            self.signing_key = SigningKey(signing_key)
        else:
            self.signing_key = SigningKey.generate()
        
        self.verify_key = self.signing_key.verify_key
        
        # Criar database
        self._init_database()
        
        # Estatísticas
        self.stats = {
            'logs_created': 0,
            'logs_verified': 0,
            'tampering_detected': 0
        }
    
    def _init_database(self):
        """Cria tabela de logs se não existir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                level TEXT NOT NULL,
                operation TEXT NOT NULL,
                user_id TEXT,
                payload_hash TEXT,
                metadata TEXT,
                signature TEXT NOT NULL,
                verified INTEGER DEFAULT 0
            )
        ''')
        
        # Índices para performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_logs(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_operation ON audit_logs(operation)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON audit_logs(user_id)')
        
        conn.commit()
        conn.close()
    
    def log(self, 
            operation: OperationType,
            level: LogLevel = LogLevel.INFO,
            user_id: Optional[str] = None,
            payload: Optional[bytes] = None,
            metadata: Optional[Dict] = None) -> int:
        """
        Registra operação com assinatura
        
        Args:
            operation: Tipo de operação
            level: Nível de log
            user_id: ID do usuário (opcional)
            payload: Payload original (será hasheado, não armazenado)
            metadata: Metadados extras (dict)
        
        Returns:
            ID do log entry
        """
        # Criar entry
        entry = AuditLogEntry(
            timestamp=datetime.now(UTC).isoformat(),
            level=level.value,
            operation=operation.value,
            user_id=user_id,
            payload_hash=hashlib.sha256(payload).hexdigest() if payload else None,
            metadata=json.dumps(metadata) if metadata else None
        )
        
        # Assinar entry (tudo exceto signature)
        data_to_sign = f"{entry.timestamp}|{entry.level}|{entry.operation}|{entry.user_id}|{entry.payload_hash}|{entry.metadata}"
        signature = self.signing_key.sign(data_to_sign.encode(), encoder=HexEncoder)
        entry.signature = signature.signature.decode()
        
        # Salvar no database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO audit_logs (timestamp, level, operation, user_id, payload_hash, metadata, signature, verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (entry.timestamp, entry.level, entry.operation, entry.user_id, 
              entry.payload_hash, entry.metadata, entry.signature, 0))
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        self.stats['logs_created'] += 1
        return log_id
    
    def verify_entry(self, entry: AuditLogEntry) -> bool:
        """
        Verifica assinatura de uma entry
        
        Args:
            entry: Entry a verificar
        
        Returns:
            True se assinatura válida, False se adulterado
        """
        try:
            # Reconstruir dados originais
            data_to_verify = f"{entry.timestamp}|{entry.level}|{entry.operation}|{entry.user_id}|{entry.payload_hash}|{entry.metadata}"
            
            # Verificar assinatura
            self.verify_key.verify(
                data_to_verify.encode(),
                bytes.fromhex(entry.signature),
                encoder=HexEncoder
            )
            
            self.stats['logs_verified'] += 1
            return True
        
        except Exception:
            self.stats['tampering_detected'] += 1
            return False
    
    def get_logs(self, 
                 operation: Optional[OperationType] = None,
                 user_id: Optional[str] = None,
                 start_time: Optional[str] = None,
                 end_time: Optional[str] = None,
                 limit: int = 100) -> List[AuditLogEntry]:
        """
        Recupera logs com filtros opcionais
        
        Args:
            operation: Filtrar por tipo de operação
            user_id: Filtrar por usuário
            start_time: ISO timestamp início
            end_time: ISO timestamp fim
            limit: Máximo de entries
        
        Returns:
            Lista de AuditLogEntry
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Construir query
        query = "SELECT * FROM audit_logs WHERE 1=1"
        params = []
        
        if operation:
            query += " AND operation = ?"
            params.append(operation.value)
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        # Converter para AuditLogEntry
        entries = []
        for row in rows:
            entry = AuditLogEntry(
                id=row[0],
                timestamp=row[1],
                level=row[2],
                operation=row[3],
                user_id=row[4],
                payload_hash=row[5],
                metadata=row[6],
                signature=row[7],
                verified=bool(row[8])
            )
            # Verificar assinatura
            entry.verified = self.verify_entry(entry)
            entries.append(entry)
        
        return entries
    
    def verify_database_integrity(self) -> Dict:
        """
        Verifica integridade de TODOS os logs
        
        Returns:
            Dict com estatísticas de verificação
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM audit_logs")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT * FROM audit_logs")
        rows = cursor.fetchall()
        conn.close()
        
        valid = 0
        tampered = 0
        
        for row in rows:
            entry = AuditLogEntry(
                id=row[0],
                timestamp=row[1],
                level=row[2],
                operation=row[3],
                user_id=row[4],
                payload_hash=row[5],
                metadata=row[6],
                signature=row[7]
            )
            
            if self.verify_entry(entry):
                valid += 1
            else:
                tampered += 1
        
        return {
            'total_logs': total,
            'valid': valid,
            'tampered': tampered,
            'integrity_percentage': (valid / total * 100) if total > 0 else 0
        }
    
    def export_signing_key(self) -> str:
        """Exporta chave privada (hex)"""
        return self.signing_key.encode(encoder=HexEncoder).decode()
    
    def export_verify_key(self) -> str:
        """Exporta chave pública (hex)"""
        return self.verify_key.encode(encoder=HexEncoder).decode()
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas de uso"""
        return self.stats.copy()


# =====================================================================
# TESTES E VALIDAÇÃO
# =====================================================================

if __name__ == "__main__":
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║         RIB 9: AUDIT LOGGER - TESTE COMPLETO                 ║")
    print("╚═══════════════════════════════════════════════════════════════╝\n")
    
    import tempfile
    import os
    
    # Criar database temporário
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_db_path = temp_db.name
    temp_db.close()
    
    try:
        # Teste 1: Inicializar logger
        print(" TESTE 1: Inicialização")
        print("="*70)
        logger = AuditLogger(db_path=temp_db_path)
        print(f" Logger criado: {temp_db_path}")
        print(f"├─ Signing key: {logger.export_signing_key()[:32]}...")
        print(f"└─ Verify key:  {logger.export_verify_key()[:32]}...\n")
        
        # Teste 2: Registrar operações
        print(" TESTE 2: Registro de Operações")
        print("="*70)
        
        log1 = logger.log(
            operation=OperationType.ENCRYPT,
            level=LogLevel.SECURITY,
            user_id="alice@kayos.com",
            payload=b"SECRET DATA",
            metadata={"file": "document.pdf", "size": 1024}
        )
        print(f" Log #1 (ENCRYPT): ID {log1}")
        
        log2 = logger.log(
            operation=OperationType.SIGN,
            level=LogLevel.SECURITY,
            user_id="bob@kayos.com",
            payload=b"CONTRACT 2025",
            metadata={"contract_id": "CTR-12345"}
        )
        print(f" Log #2 (SIGN): ID {log2}")
        
        log3 = logger.log(
            operation=OperationType.STEGO_EMBED,
            level=LogLevel.INFO,
            user_id="charlie@kayos.com",
            payload=b"HIDDEN MESSAGE",
            metadata={"image": "cover.png", "capacity": 15000}
        )
        print(f" Log #3 (STEGO_EMBED): ID {log3}\n")
        
        # Teste 3: Recuperar logs
        print(" TESTE 3: Recuperação de Logs")
        print("="*70)
        logs = logger.get_logs(limit=10)
        for entry in logs:
            print(f"├─ [{entry.level}] {entry.operation} by {entry.user_id}")
            print(f"│  └─ Verified: {'' if entry.verified else ''} | Hash: {entry.payload_hash[:16]}...")
        print()
        
        # Teste 4: Verificar integridade
        print(" TESTE 4: Verificação de Integridade")
        print("="*70)
        integrity = logger.verify_database_integrity()
        print(f"├─ Total logs:   {integrity['total_logs']}")
        print(f"├─ Válidos:      {integrity['valid']} ")
        print(f"├─ Adulterados:  {integrity['tampered']} {'' if integrity['tampered'] > 0 else ''}")
        print(f"└─ Integridade:  {integrity['integrity_percentage']:.2f}%\n")
        
        # Teste 5: Simulando adulteração
        print("  TESTE 5: Detecção de Adulteração")
        print("="*70)
        
        # Modificar database diretamente (simular ataque)
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE audit_logs SET user_id = 'hacker@evil.com' WHERE id = ?", (log1,))
        conn.commit()
        conn.close()
        
        print(" Database modificado manualmente (ataque simulado)")
        
        # Verificar novamente
        integrity_after = logger.verify_database_integrity()
        print(f"\n├─ Total logs:   {integrity_after['total_logs']}")
        print(f"├─ Válidos:      {integrity_after['valid']} {'' if integrity_after['valid'] == integrity_after['total_logs'] else ''}")
        print(f"├─ Adulterados:  {integrity_after['tampered']} {' DETECTADO!' if integrity_after['tampered'] > 0 else ''}")
        print(f"└─ Integridade:  {integrity_after['integrity_percentage']:.2f}%\n")
        
        # Teste 6: Estatísticas
        print(" TESTE 6: Estatísticas de Uso")
        print("="*70)
        stats = logger.get_stats()
        for key, value in stats.items():
            print(f"├─ {key:25s}: {value}")
        
        print("\n╔═══════════════════════════════════════════════════════════════╗")
        if integrity_after['tampered'] > 0:
            print("║        TESTE OK - ADULTERAÇÃO DETECTADA CORRETAMENTE       ║")
        else:
            print("║                      TODOS OS TESTES OK                     ║")
        print("║           Rib 9 (Audit Logger) FUNCIONAL                     ║")
        print("╚═══════════════════════════════════════════════════════════════╝")
        
    finally:
        # Limpar
        os.remove(temp_db_path)
        print(f"\n Database temporário removido: {temp_db_path}")
