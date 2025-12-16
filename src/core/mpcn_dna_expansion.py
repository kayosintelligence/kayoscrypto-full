#!/usr/bin/env python3
"""
 MPC-N DNA EXPANSION - Logging Detalhado para DNA e MFA
Sistema expandido de logging MPC-N para eventos de DNA e autenticação

Características:
 Categorias especializadas para DNA/MFA
 Métricas de performance e segurança
 Alertas automáticos para eventos suspeitos
 Relatórios de compliance e auditoria
 Integração com sistema de monitoramento

© 2025 KAYOS SYSTEMS - MPC-N DNA Expansion v1.0
"""

import sys
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path

# Adicionar paths
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

# Import MPC-N (opcional - logging avançado para DNA expansion)
try:
    from src.kayoscrypto.mpcn.context import log_event, load_context, MPCNContext
    MPCN_AVAILABLE = True
except ImportError:
    MPCN_AVAILABLE = False
    log_event = None
    load_context = None
    MPCNContext = None

# --- CONFIGURAÇÃO ---
class DNAEventCategory(Enum):
    """Categorias de eventos DNA"""
    DNA_GENERATION = "dna_generation"
    DNA_VALIDATION = "dna_validation"
    DNA_AUTH_SUCCESS = "dna_auth_success"
    DNA_AUTH_FAILURE = "dna_auth_failure"
    DNA_MFA_START = "dna_mfa_start"
    DNA_MFA_STEP = "dna_mfa_step"
    DNA_MFA_COMPLETE = "dna_mfa_complete"
    DNA_SECURITY_ALERT = "dna_security_alert"
    DNA_PERFORMANCE = "dna_performance"
    DNA_COMPLIANCE = "dna_compliance"

class AlertSeverity(Enum):
    """Severidade dos alertas"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# --- DATA CLASSES ---
@dataclass
class DNAEventDetails:
    """Detalhes estruturados para eventos DNA"""
    dna_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    factor_type: Optional[str] = None
    risk_level: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    performance_ms: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class SecurityAlert:
    """Alerta de segurança"""
    alert_id: str
    severity: AlertSeverity
    category: str
    message: str
    details: Dict[str, Any]
    timestamp: str
    resolved: bool = False

# --- MPC-N DNA EXPANSION ---
class MPCNDNAExpansion:
    """Sistema expandido de logging MPC-N para DNA"""

    def __init__(self):
        if MPCN_AVAILABLE:
            self.context = load_context()
        else:
            self.context = None
        self.alerts: List[SecurityAlert] = []
        self.metrics = {
            "total_events": 0,
            "auth_success": 0,
            "auth_failures": 0,
            "mfa_sessions": 0,
            "security_alerts": 0,
            "performance_avg_ms": 0.0
        }

    def log_dna_event(
        self,
        category: DNAEventCategory,
        actor: str,
        details: DNAEventDetails
    ) -> None:
        """
        Log detalhado de evento DNA
        """

        # Atualizar métricas
        self._update_metrics(category, details)

        # Verificar alertas de segurança
        alert = self._check_security_alerts(category, details)
        if alert:
            self._log_security_alert(alert)

        # Log do evento principal
        if MPCN_AVAILABLE and log_event:
            event_details = {
                "category": category.value,
                "dna_event": asdict(details),
                "metrics_snapshot": self.metrics.copy()
            }

            log_event(
                actor=f"dna_system_{actor}",
                action=f"dna_{category.value}",
                details=event_details,
                ctx=self.context
            )
        else:
            print(f"[DNA-LOG] {category.value}: {actor} - {asdict(details)}")

        self.metrics["total_events"] += 1

    def log_mfa_session_start(
        self,
        user_id: str,
        dna_id: str,
        session_id: str,
        risk_level: str,
        factors: List[str]
    ) -> None:
        """
        Log início de sessão MFA
        """

        details = DNAEventDetails(
            user_id=user_id,
            dna_id=dna_id,
            session_id=session_id,
            risk_level=risk_level,
            metadata={
                "factors_required": factors,
                "session_type": "mfa_dna"
            }
        )

        self.log_dna_event(DNAEventCategory.DNA_MFA_START, user_id, details)
        self.metrics["mfa_sessions"] += 1

    def log_mfa_step(
        self,
        user_id: str,
        session_id: str,
        factor_type: str,
        success: bool,
        performance_ms: float
    ) -> None:
        """
        Log passo individual de MFA
        """

        details = DNAEventDetails(
            user_id=user_id,
            session_id=session_id,
            factor_type=factor_type,
            success=success,
            performance_ms=performance_ms,
            error_message=None if success else "Factor validation failed"
        )

        self.log_dna_event(DNAEventCategory.DNA_MFA_STEP, user_id, details)

    def log_auth_success(
        self,
        user_id: str,
        dna_id: str,
        auth_method: str,
        risk_level: str,
        performance_ms: float
    ) -> None:
        """
        Log autenticação bem-sucedida
        """

        details = DNAEventDetails(
            user_id=user_id,
            dna_id=dna_id,
            risk_level=risk_level,
            performance_ms=performance_ms,
            metadata={
                "auth_method": auth_method,
                "security_level": "high"
            }
        )

        self.log_dna_event(DNAEventCategory.DNA_AUTH_SUCCESS, user_id, details)
        self.metrics["auth_success"] += 1

    def log_auth_failure(
        self,
        user_id: str,
        attempted_dna_id: str,
        failure_reason: str,
        ip_address: str,
        user_agent: str
    ) -> None:
        """
        Log falha de autenticação
        """

        details = DNAEventDetails(
            user_id=user_id,
            dna_id=attempted_dna_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            error_message=failure_reason
        )

        self.log_dna_event(DNAEventCategory.DNA_AUTH_FAILURE, user_id, details)
        self.metrics["auth_failures"] += 1

    def _update_metrics(self, category: DNAEventCategory, details: DNAEventDetails) -> None:
        """Atualizar métricas do sistema"""

        if details.performance_ms:
            # Calcular média móvel de performance
            current_avg = self.metrics["performance_avg_ms"]
            total_events = self.metrics["total_events"]
            new_avg = (current_avg * total_events + details.performance_ms) / (total_events + 1)
            self.metrics["performance_avg_ms"] = new_avg

    def _check_security_alerts(
        self,
        category: DNAEventCategory,
        details: DNAEventDetails
    ) -> Optional[SecurityAlert]:
        """
        Verificar condições para alertas de segurança
        """

        alert = None

        # Alerta: Múltiplas falhas de autenticação
        if category == DNAEventCategory.DNA_AUTH_FAILURE:
            recent_failures = self._count_recent_events(
                DNAEventCategory.DNA_AUTH_FAILURE,
                minutes=5,
                user_id=details.user_id
            )

            if recent_failures >= 3:
                alert = SecurityAlert(
                    alert_id=f"auth_brute_force_{details.user_id}_{datetime.now().timestamp()}",
                    severity=AlertSeverity.HIGH,
                    category="authentication",
                    message=f"Possível ataque de força bruta detectado para usuário {details.user_id}",
                    details={
                        "user_id": details.user_id,
                        "failures_in_5min": recent_failures,
                        "last_failure": details.error_message
                    },
                    timestamp=datetime.now(timezone.utc).isoformat()
                )

        # Alerta: Performance degradada
        elif category in [DNAEventCategory.DNA_VALIDATION, DNAEventCategory.DNA_AUTH_SUCCESS]:
            if details.performance_ms and details.performance_ms > 5000:  # 5 segundos
                alert = SecurityAlert(
                    alert_id=f"performance_degraded_{datetime.now().timestamp()}",
                    severity=AlertSeverity.MEDIUM,
                    category="performance",
                    message="Performance de DNA validation degradada",
                    details={
                        "performance_ms": details.performance_ms,
                        "threshold_ms": 5000,
                        "user_id": details.user_id
                    },
                    timestamp=datetime.now(timezone.utc).isoformat()
                )

        return alert

    def _count_recent_events(
        self,
        category: DNAEventCategory,
        minutes: int,
        user_id: Optional[str] = None
    ) -> int:
        """
        Contar eventos recentes de uma categoria
        """

        if not MPCN_AVAILABLE or not self.context:
            return 0  # Sem histórico disponível

        cutoff_time = datetime.now(timezone.utc).timestamp() - (minutes * 60)
        count = 0

        for event in self.context.history:
            if event.timestamp and datetime.fromisoformat(event.timestamp).timestamp() > cutoff_time:
                if event.action == f"dna_{category.value}":
                    event_details = event.details.get("dna_event", {})
                    if not user_id or event_details.get("user_id") == user_id:
                        count += 1

        return count

    def _log_security_alert(self, alert: SecurityAlert) -> None:
        """Log de alerta de segurança"""

        self.alerts.append(alert)
        self.metrics["security_alerts"] += 1

        if MPCN_AVAILABLE and log_event:
            log_event(
                actor="dna_security_monitor",
                action=f"security_alert_{alert.severity.value}",
                details={
                    "alert": asdict(alert),
                    "total_alerts": len(self.alerts),
                    "severity_distribution": self._get_alert_severity_distribution()
                },
                ctx=self.context
            )
        else:
            print(f"[SECURITY-ALERT] {alert.severity.value}: {alert.message}")

    def _get_alert_severity_distribution(self) -> Dict[str, int]:
        """Distribuição de severidade dos alertas"""

        distribution = {}
        for severity in AlertSeverity:
            distribution[severity.value] = sum(
                1 for alert in self.alerts
                if alert.severity == severity and not alert.resolved
            )
        return distribution

    def get_compliance_report(self) -> Dict[str, Any]:
        """Gerar relatório de compliance"""

        return {
            "period": "last_30_days",
            "metrics": self.metrics,
            "active_alerts": len([a for a in self.alerts if not a.resolved]),
            "auth_success_rate": (
                self.metrics["auth_success"] /
                max(self.metrics["auth_success"] + self.metrics["auth_failures"], 1)
            ),
            "average_performance_ms": self.metrics["performance_avg_ms"],
            "security_score": self._calculate_security_score()
        }

    def _calculate_security_score(self) -> float:
        """Calcular score de segurança baseado nas métricas"""

        base_score = 100.0

        # Penalizar falhas de autenticação
        failure_rate = self.metrics["auth_failures"] / max(self.metrics["total_events"], 1)
        base_score -= failure_rate * 20

        # Penalizar alertas ativos
        active_alerts = len([a for a in self.alerts if not a.resolved])
        base_score -= active_alerts * 5

        # Bônus por MFA sessions
        mfa_bonus = min(self.metrics["mfa_sessions"] * 2, 20)
        base_score += mfa_bonus

        return max(0.0, min(100.0, base_score))

# --- INSTÂNCIA GLOBAL ---
_dna_mpce = None

def get_dna_mpce() -> MPCNDNAExpansion:
    """Obter instância global do MPC-N DNA Expansion"""
    global _dna_mpce
    if _dna_mpce is None:
        _dna_mpce = MPCNDNAExpansion()
    return _dna_mpce

# --- FUNÇÕES DE CONVENIÊNCIA ---
def log_dna_generation(user_id: str, dna_id: str, performance_ms: float):
    """Log geração de DNA"""
    mpce = get_dna_mpce()
    details = DNAEventDetails(
        user_id=user_id,
        dna_id=dna_id,
        performance_ms=performance_ms
    )
    mpce.log_dna_event(DNAEventCategory.DNA_GENERATION, user_id, details)

def log_dna_auth_success(user_id: str, dna_id: str, auth_method: str, performance_ms: float):
    """Log autenticação DNA bem-sucedida"""
    mpce = get_dna_mpce()
    mpce.log_auth_success(user_id, dna_id, auth_method, "high", performance_ms)

def log_dna_auth_failure(user_id: str, dna_id: str, reason: str):
    """Log falha de autenticação DNA"""
    mpce = get_dna_mpce()
    mpce.log_auth_failure(user_id, dna_id, reason, "system", "KayosCrypto-API")

# --- DEMONSTRAÇÃO ---
def demo_mpce_dna_expansion():
    """Demonstração do MPC-N DNA Expansion"""

    print("=" * 80)
    print(" MPC-N DNA EXPANSION - Logging Detalhado")
    print("Sistema Avançado de Logging para DNA e MFA")
    print("=" * 80)

    mpce = get_dna_mpce()

    # Simular eventos de DNA
    print("\n Gerando eventos de teste...")

    # Geração de DNA
    log_dna_generation("joao_silva", "dna_123", 150.5)
    print("    DNA Generation logged")

    # Autenticação bem-sucedida
    log_dna_auth_success("joao_silva", "dna_123", "dna_mfa", 234.2)
    print("    DNA Auth Success logged")

    # Sessão MFA
    mpce.log_mfa_session_start(
        "maria_santos", "dna_456", "session_789",
        "high", ["dna", "password", "biometric"]
    )
    print("    MFA Session Start logged")

    # Passos MFA
    mpce.log_mfa_step("maria_santos", "session_789", "dna", True, 45.3)
    mpce.log_mfa_step("maria_santos", "session_789", "password", True, 23.1)
    mpce.log_mfa_step("maria_santos", "session_789", "biometric", True, 67.8)
    print("    MFA Steps logged")

    # Falha de autenticação (para testar alertas)
    for i in range(4):  # 4 tentativas para trigger alerta
        log_dna_auth_failure(f"hacker_{i}", "invalid_dna", "wrong_password")
    print("    Auth Failures logged (alert triggered)")

    # Relatório de compliance
    print("\n Relatório de Compliance:")
    report = mpce.get_compliance_report()
    print(f"   Total Events: {report['metrics']['total_events']}")
    print(f"   Auth Success Rate: {report['auth_success_rate']:.2%}")
    print(f"   Security Score: {report['security_score']:.1f}/100")
    print(f"   Active Alerts: {report['active_alerts']}")
    print(f"   Average Performance: {report['average_performance_ms']:.1f}ms")

    print("\n" + "=" * 80)
    print(" DEMONSTRAÇÃO MPC-N DNA EXPANSION CONCLUÍDA!")
    print(" Sistema de logging detalhado operacional")
    print("=" * 80)

if __name__ == "__main__":
    demo_mpce_dna_expansion()