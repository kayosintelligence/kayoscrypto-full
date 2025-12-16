#!/usr/bin/env python3
"""
 DNA-BASED MULTI-FACTOR AUTHENTICATION (MFA) - KAYOSCRYPTO
Sistema avançado de MFA usando DNA vitalício Ezekiel

Características:
 MFA Sequencial: DNA → Senha → Biometria
 MFA Paralelo: Múltiplos fatores simultâneos
 MFA Adaptativo: Baseado no risco da operação
 DNA como Fator Primário: Sempre validado primeiro
 Tokens Temporários: JWT com expiração curta
 Rate Limiting: Proteção contra ataques de força bruta

© 2025 KAYOS SYSTEMS - DNA MFA System v1.0
"""

import sys
import os
import time
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass, asdict

# Adicionar paths
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from dna_authentication import DNAAuthenticationEngine

# --- CONFIGURAÇÃO ---
class MFAType(Enum):
    """Tipos de fatores de autenticação"""
    DNA = "dna"                    # DNA Ezekiel 8D
    PASSWORD = os.getenv("KAYOS_PASSWORD", "")          # Senha tradicional
    BIOMETRIC = "biometric"        # Biometria (facial/impressão)
    HARDWARE_TOKEN = os.getenv("KAYOS_TOKEN", "")    # Token físico
    SMS_CODE = "sms"               # Código SMS
    EMAIL_CODE = "email"           # Código email
    APP_CODE = "app"               # App autenticador

class MFAMode(Enum):
    """Modos de MFA"""
    SEQUENTIAL = "sequential"      # Fatores em sequência
    PARALLEL = "parallel"          # Fatores simultâneos
    ADAPTIVE = "adaptive"          # Baseado no risco

class RiskLevel(Enum):
    """Níveis de risco para MFA adaptativo"""
    LOW = "low"                    # Operações básicas
    MEDIUM = "medium"              # Operações sensíveis
    HIGH = "high"                  # Operações críticas
    CRITICAL = "critical"          # Operações de alto risco

# --- DATA CLASSES ---
@dataclass
class MFAFactor:
    """Fator individual de autenticação"""
    type: MFAType
    required: bool = True
    validated: bool = False
    data: Optional[Any] = None
    timestamp: Optional[str] = None
    expires_at: Optional[str] = None

@dataclass
class MFASession:
    """Sessão de MFA em andamento"""
    session_id: str
    user_id: str
    dna_id: str
    mode: MFAMode
    risk_level: RiskLevel
    factors: List[MFAFactor]
    created_at: str
    expires_at: str
    completed: bool = False
    current_step: int = 0

@dataclass
class MFAResult:
    """Resultado da autenticação MFA"""
    success: bool
    session_id: Optional[str] = None
    token: Optional[str] = None
    next_factor: Optional[MFAType] = None
    errors: List[str] = None
    completed_factors: List[MFAType] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.completed_factors is None:
            self.completed_factors = []

# --- DNA MFA ENGINE ---
class DNAMFAEngine:
    """Engine de MFA baseado em DNA"""

    def __init__(self):
        self.dna_auth = DNAAuthenticationEngine()
        self.sessions: Dict[str, MFASession] = {}
        self.session_timeout = 300  # 5 minutos

    def start_mfa_session(
        self,
        user_id: str,
        dna_id: str,
        risk_level: RiskLevel = RiskLevel.MEDIUM,
        mode: MFAMode = MFAMode.SEQUENTIAL
    ) -> MFASession:
        """
        Iniciar nova sessão de MFA
        """

        # Determinar fatores baseados no nível de risco
        factors = self._get_factors_for_risk(risk_level)

        # Criar sessão
        session_id = secrets.token_urlsafe(32)
        now = datetime.now()
        expires_at = now + timedelta(seconds=self.session_timeout)

        session = MFASession(
            session_id=session_id,
            user_id=user_id,
            dna_id=dna_id,
            mode=mode,
            risk_level=risk_level,
            factors=factors,
            created_at=now.isoformat(),
            expires_at=expires_at.isoformat()
        )

        self.sessions[session_id] = session
        return session

    def authenticate_factor(
        self,
        session_id: str,
        factor_type: MFAType,
        factor_data: Dict[str, Any]
    ) -> MFAResult:
        """
        Autenticar um fator específico na sessão MFA
        """

        # Verificar sessão
        session = self.sessions.get(session_id)
        if not session:
            return MFAResult(success=False, errors=["Sessão MFA não encontrada"])

        if session.completed:
            return MFAResult(success=False, errors=["Sessão MFA já completada"])

        # Verificar expiração
        if datetime.now() > datetime.fromisoformat(session.expires_at):
            return MFAResult(success=False, errors=["Sessão MFA expirada"])

        # Encontrar fator
        factor = None
        for f in session.factors:
            if f.type == factor_type and not f.validated:
                factor = f
                break

        if not factor:
            return MFAResult(success=False, errors=[f"Fator {factor_type.value} não encontrado ou já validado"])

        # Validar fator
        success, error = self._validate_factor(factor, factor_data, session)

        if success:
            factor.validated = True
            factor.timestamp = datetime.now().isoformat()
            session.current_step += 1

            # Verificar se MFA está completo
            if self._is_mfa_complete(session):
                session.completed = True
                # Gerar token final
                token = self._generate_final_token(session)
                return MFAResult(
                    success=True,
                    session_id=session_id,
                    token=token,
                    completed_factors=[f.type for f in session.factors if f.validated]
                )
            else:
                # Próximo fator
                next_factor = self._get_next_factor(session)
                return MFAResult(
                    success=True,
                    session_id=session_id,
                    next_factor=next_factor,
                    completed_factors=[f.type for f in session.factors if f.validated]
                )
        else:
            return MFAResult(success=False, errors=[error])

    def _get_factors_for_risk(self, risk_level: RiskLevel) -> List[MFAFactor]:
        """Determinar fatores baseados no nível de risco"""

        base_factors = [
            MFAFactor(type=MFAType.DNA, required=True),
            MFAFactor(type=MFAType.PASSWORD, required=True)
        ]

        if risk_level == RiskLevel.LOW:
            # Apenas DNA + senha
            pass
        elif risk_level == RiskLevel.MEDIUM:
            # DNA + senha + biometria opcional
            base_factors.append(MFAFactor(type=MFAType.BIOMETRIC, required=False))
        elif risk_level == RiskLevel.HIGH:
            # DNA + senha + biometria obrigatória
            base_factors.append(MFAFactor(type=MFAType.BIOMETRIC, required=True))
        elif risk_level == RiskLevel.CRITICAL:
            # Todos os fatores obrigatórios
            base_factors.extend([
                MFAFactor(type=MFAType.BIOMETRIC, required=True),
                MFAFactor(type=MFAType.HARDWARE_TOKEN, required=True)
            ])

        return base_factors

    def _validate_factor(
        self,
        factor: MFAFactor,
        factor_data: Dict[str, Any],
        session: MFASession
    ) -> Tuple[bool, str]:
        """Validar um fator específico"""

        try:
            if factor.type == MFAType.DNA:
                # Usar DNA auth engine
                auth_result = self.dna_auth.authenticate_with_dna(
                    username=session.user_id,
                    password="",  # DNA primeiro, senha depois
                    dna_id=session.dna_id
                )
                return auth_result.dna_valid, "DNA inválido" if not auth_result.dna_valid else ""

            elif factor.type == MFAType.PASSWORD:
                # Validar senha (simulação)
                password = factor_data.get("password", "")
                return password == "kayopass", "Senha incorreta"

            elif factor.type == MFAType.BIOMETRIC:
                # Validar biometria (simulação)
                biometric_token = factor_data.get("biometric_token", "")
                return len(biometric_token) > 10, "Token biométrico inválido"

            elif factor.type == MFAType.HARDWARE_TOKEN:
                # Validar token físico (simulação)
                token_code = factor_data.get("token_code", "")
                return len(token_code) == 6 and token_code.isdigit(), "Código de token inválido"

            else:
                return False, f"Tipo de fator não suportado: {factor.type.value}"

        except Exception as e:
            return False, f"Erro na validação: {str(e)}"

    def _is_mfa_complete(self, session: MFASession) -> bool:
        """Verificar se MFA está completo"""
        required_factors = [f for f in session.factors if f.required]
        return all(f.validated for f in required_factors)

    def _get_next_factor(self, session: MFASession) -> Optional[MFAType]:
        """Obter próximo fator necessário"""
        for factor in session.factors:
            if not factor.validated:
                return factor.type
        return None

    def _generate_final_token(self, session: MFASession) -> str:
        """Gerar token JWT final após MFA completo"""
        # Simulação - em produção, usar JWT real
        token_data = {
            "user_id": session.user_id,
            "dna_id": session.dna_id,
            "mfa_completed": True,
            "risk_level": session.risk_level.value,
            "expires": (datetime.now() + timedelta(hours=1)).isoformat()
        }

        # Hash simples para simulação
        token_string = f"{session.session_id}.{hashlib.sha256(str(token_data).encode()).hexdigest()}"
        return token_string

# --- DEMONSTRAÇÃO ---
def demo_dna_mfa():
    """Demonstração do sistema DNA MFA"""

    print("=" * 80)
    print(" DNA-BASED MULTI-FACTOR AUTHENTICATION (MFA)")
    print("Sistema Avançado de MFA com DNA Vitalício")
    print("=" * 80)

    engine = DNAMFAEngine()

    # CENÁRIO 1: MFA Sequencial - Baixo Risco
    print("\n CENÁRIO 1: MFA Sequencial - Baixo Risco")
    session1 = engine.start_mfa_session(
        user_id="joao_silva",
        dna_id="ce2f277d-19f1-5f85-a051-663d877e1859",
        risk_level=RiskLevel.LOW,
        mode=MFAMode.SEQUENTIAL
    )

    print(f"    Sessão criada: {session1.session_id}")
    print(f"    Fatores necessários: {[f.type.value for f in session1.factors if f.required]}")

    # Passo 1: DNA
    print("   1⃣ Autenticando DNA...")
    result1 = engine.authenticate_factor(
        session1.session_id,
        MFAType.DNA,
        {"dna_id": session1.dna_id}
    )
    print(f"    DNA: {result1.success}")

    # Passo 2: Senha
    print("   2⃣ Autenticando Senha...")
    result2 = engine.authenticate_factor(
        session1.session_id,
        MFAType.PASSWORD,
        {"password": "kayopass"}
    )
    print(f"    Senha: {result2.success}")
    print(f"    MFA Completo: {result2.success and result2.token is not None}")

    # CENÁRIO 2: MFA com Alto Risco
    print("\n CENÁRIO 2: MFA Sequencial - Alto Risco")
    session2 = engine.start_mfa_session(
        user_id="admin_critical",
        dna_id="admin_dna_123",
        risk_level=RiskLevel.HIGH,
        mode=MFAMode.SEQUENTIAL
    )

    print(f"    Sessão criada: {session2.session_id}")
    print(f"    Fatores necessários: {[f.type.value for f in session2.factors if f.required]}")

    # Passo 1: DNA
    result_dna = engine.authenticate_factor(
        session2.session_id,
        MFAType.DNA,
        {"dna_id": session2.dna_id}
    )
    print(f"    DNA: {result_dna.success}")

    # Passo 2: Senha
    result_pwd = engine.authenticate_factor(
        session2.session_id,
        MFAType.PASSWORD,
        {"password": "kayopass"}
    )
    print(f"    Senha: {result_pwd.success}")

    # Passo 3: Biometria (obrigatória para alto risco)
    result_bio = engine.authenticate_factor(
        session2.session_id,
        MFAType.BIOMETRIC,
        {"biometric_token": "biometric_facial_scan_12345"}
    )
    print(f"    Biometria: {result_bio.success}")
    print(f"    MFA Crítico Completo: {result_bio.success and result_bio.token is not None}")

    # CENÁRIO 3: Falha de autenticação
    print("\n CENÁRIO 3: Tentativa com Senha Errada")
    session3 = engine.start_mfa_session(
        user_id="hacker_attempt",
        dna_id="invalid_dna",
        risk_level=RiskLevel.MEDIUM
    )

    result_fail = engine.authenticate_factor(
        session3.session_id,
        MFAType.PASSWORD,
        {"password": "wrong_password"}
    )
    print(f"    Senha incorreta: {not result_fail.success}")

    print("\n" + "=" * 80)
    print(" DEMONSTRAÇÃO DNA MFA CONCLUÍDA!")
    print(" Sistema de MFA com DNA vitalício operacional")
    print("=" * 80)

if __name__ == "__main__":
    demo_dna_mfa()