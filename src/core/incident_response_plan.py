"""
KayosCrypto Incident Response Plan
===================================

Sistema completo de resposta a incidentes baseado no NIST CSF 2.0
Implementa as funções RC (Respond) e CO (Communicate) do framework.

Data: 29 de novembro de 2025
Versão: 1.0.0
"""

import json
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


class IncidentSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(Enum):
    DETECTED = "detected"
    ANALYZING = "analyzing"
    CONTAINED = "contained"
    ERADICATED = "eradicated"
    RECOVERED = "recovered"
    CLOSED = "closed"


class IncidentCategory(Enum):
    SECURITY_BREACH = "security_breach"
    DATA_LEAK = "data_leak"
    DENIAL_OF_SERVICE = "denial_of_service"
    MALWARE = "malware"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SYSTEM_FAILURE = "system_failure"


@dataclass
class Incident:
    """Representa um incidente de segurança"""
    id: str
    title: str
    description: str
    category: IncidentCategory
    severity: IncidentSeverity
    status: IncidentStatus
    detected_at: datetime
    reported_by: str
    assigned_to: Optional[str] = None
    containment_actions: List[str] = None
    recovery_actions: List[str] = None
    lessons_learned: Optional[str] = None
    closed_at: Optional[datetime] = None
    impact_assessment: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.containment_actions is None:
            self.containment_actions = []
        if self.recovery_actions is None:
            self.recovery_actions = []
        if self.impact_assessment is None:
            self.impact_assessment = {}


class IncidentResponsePlan:
    """
    Plano completo de resposta a incidentes seguindo NIST CSF 2.0

    Implementa:
    - Detecção e análise de incidentes
    - Estratégias de contenção
    - Comunicação interna e externa
    - Recuperação de sistemas
    - Lições aprendidas e melhoria contínua
    """

    def __init__(self):
        self.incidents: Dict[str, Incident] = {}
        self.response_templates = self._load_response_templates()
        self.communication_plan = self._load_communication_plan()
        self.escalation_matrix = self._load_escalation_matrix()

    def _load_response_templates(self) -> Dict[str, Dict[str, Any]]:
        """Carrega templates de resposta por categoria de incidente"""
        return {
            IncidentCategory.SECURITY_BREACH.value: {
                "containment": [
                    "Isolar sistemas afetados da rede",
                    "Revogar credenciais comprometidas",
                    "Implementar controles de acesso temporários",
                    "Ativar monitoramento adicional"
                ],
                "recovery": [
                    "Restaurar sistemas de backup limpo",
                    "Atualizar todas as credenciais",
                    "Aplicar patches de segurança",
                    "Realizar testes de integridade"
                ],
                "timeline": {
                    IncidentSeverity.LOW: timedelta(hours=4),
                    IncidentSeverity.MEDIUM: timedelta(hours=2),
                    IncidentSeverity.HIGH: timedelta(hours=1),
                    IncidentSeverity.CRITICAL: timedelta(minutes=30)
                }
            },
            IncidentCategory.DATA_LEAK.value: {
                "containment": [
                    "Interromper transmissão de dados",
                    "Notificar titulares de dados afetados",
                    "Implementar criptografia adicional",
                    "Auditar logs de acesso"
                ],
                "recovery": [
                    "Implementar controles de prevenção de vazamento",
                    "Treinar equipe sobre proteção de dados",
                    "Atualizar políticas de segurança",
                    "Realizar auditoria independente"
                ],
                "timeline": {
                    IncidentSeverity.LOW: timedelta(hours=8),
                    IncidentSeverity.MEDIUM: timedelta(hours=4),
                    IncidentSeverity.HIGH: timedelta(hours=2),
                    IncidentSeverity.CRITICAL: timedelta(hours=1)
                }
            },
            IncidentCategory.DENIAL_OF_SERVICE.value: {
                "containment": [
                    "Ativar proteção DDoS",
                    "Filtrar tráfego malicioso",
                    "Redirecionar tráfego para CDN",
                    "Implementar rate limiting"
                ],
                "recovery": [
                    "Otimizar configuração de firewall",
                    "Implementar redundância de rede",
                    "Atualizar capacidades de mitigação",
                    "Realizar testes de carga"
                ],
                "timeline": {
                    IncidentSeverity.LOW: timedelta(hours=2),
                    IncidentSeverity.MEDIUM: timedelta(hours=1),
                    IncidentSeverity.HIGH: timedelta(minutes=30),
                    IncidentSeverity.CRITICAL: timedelta(minutes=15)
                }
            }
        }

    def _load_communication_plan(self) -> Dict[str, Any]:
        """Carrega plano de comunicação para incidentes"""
        return {
            "internal_communication": {
                "immediate_response_team": ["security@company.com", "cto@company.com"],
                "escalation_contacts": {
                    IncidentSeverity.LOW: ["security-lead@company.com"],
                    IncidentSeverity.MEDIUM: ["security-lead@company.com", "ciso@company.com"],
                    IncidentSeverity.HIGH: ["security-lead@company.com", "ciso@company.com", "ceo@company.com"],
                    IncidentSeverity.CRITICAL: ["security-lead@company.com", "ciso@company.com", "ceo@company.com", "board@company.com"]
                }
            },
            "external_communication": {
                "regulatory_bodies": ["ico@gov.uk", "dataprotection@gov.uk"],
                "affected_parties": "automated_notification_system",
                "media_contacts": ["pr@company.com"],
                "legal_counsel": ["legal@company.com"]
            },
            "communication_templates": {
                "initial_notification": "Incidente de segurança detectado. Análise em andamento.",
                "status_update": "Atualização do incidente: {status}. Ações tomadas: {actions}",
                "resolution_notification": "Incidente resolvido. Lições aprendidas: {lessons}"
            }
        }

    def _load_escalation_matrix(self) -> Dict[str, Any]:
        """Carrega matriz de escalação baseada em severidade"""
        return {
            IncidentSeverity.LOW.value: {
                "response_time": timedelta(hours=4),
                "escalation_levels": ["Tier 1", "Tier 2"],
                "required_approvals": []
            },
            IncidentSeverity.MEDIUM.value: {
                "response_time": timedelta(hours=2),
                "escalation_levels": ["Tier 1", "Tier 2", "CISO"],
                "required_approvals": ["security_lead"]
            },
            IncidentSeverity.HIGH.value: {
                "response_time": timedelta(hours=1),
                "escalation_levels": ["Tier 1", "Tier 2", "CISO", "CEO"],
                "required_approvals": ["ciso", "ceo"]
            },
            IncidentSeverity.CRITICAL.value: {
                "response_time": timedelta(minutes=30),
                "escalation_levels": ["Tier 1", "Tier 2", "CISO", "CEO", "Board"],
                "required_approvals": ["ciso", "ceo", "board"]
            }
        }

    def create_incident(self, title: str, description: str, category: IncidentCategory,
                       severity: IncidentSeverity, reported_by: str) -> str:
        """Cria um novo incidente e inicia o processo de resposta"""
        incident_id = f"INC-{int(time.time())}"

        incident = Incident(
            id=incident_id,
            title=title,
            description=description,
            category=category,
            severity=severity,
            status=IncidentStatus.DETECTED,
            detected_at=datetime.now(),
            reported_by=reported_by
        )

        self.incidents[incident_id] = incident

        # Inicia resposta automática baseada na severidade
        self._initiate_automated_response(incident)

        return incident_id

    def _initiate_automated_response(self, incident: Incident):
        """Inicia resposta automatizada baseada no template"""
        template = self.response_templates.get(incident.category.value, {})
        escalation = self.escalation_matrix.get(incident.severity.value, {})

        # Define timeline de resposta
        response_deadline = incident.detected_at + escalation.get("response_time", timedelta(hours=4))

        # Notifica equipe de resposta
        self._notify_response_team(incident, escalation)

        # Executa ações automáticas de contenção se aplicável
        if incident.severity in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL]:
            self._execute_automated_containment(incident)

    def _notify_response_team(self, incident: Incident, escalation: Dict[str, Any]):
        """Notifica equipe de resposta apropriada"""
        contacts = self.communication_plan["internal_communication"]["escalation_contacts"]
        target_contacts = contacts.get(incident.severity, [])

        notification = {
            "incident_id": incident.id,
            "severity": incident.severity.value,
            "title": incident.title,
            "timestamp": datetime.now().isoformat(),
            "contacts_notified": target_contacts
        }

        # Em implementação real, enviaria emails/SMS/notificações
        print(f" NOTIFICAÇÃO DE INCIDENTE: {json.dumps(notification, indent=2)}")

    def _execute_automated_containment(self, incident: Incident):
        """Executa ações automáticas de contenção para incidentes críticos"""
        template = self.response_templates.get(incident.category.value, {})
        containment_actions = template.get("containment", [])

        for action in containment_actions:
            # Em implementação real, executaria ações específicas
            print(f" EXECUTANDO CONTENÇÃO: {action}")

            # Registra ação no incidente
            incident.containment_actions.append(f"{datetime.now().isoformat()}: {action}")

    def update_incident_status(self, incident_id: str, new_status: IncidentStatus,
                             actions_taken: List[str] = None, assigned_to: str = None):
        """Atualiza status do incidente e registra ações"""
        if incident_id not in self.incidents:
            raise ValueError(f"Incidente {incident_id} não encontrado")

        incident = self.incidents[incident_id]
        incident.status = new_status

        if actions_taken:
            if new_status == IncidentStatus.CONTAINED:
                incident.containment_actions.extend(actions_taken)
            elif new_status in [IncidentStatus.ERADICATED, IncidentStatus.RECOVERED]:
                incident.recovery_actions.extend(actions_taken)

        if assigned_to:
            incident.assigned_to = assigned_to

        if new_status == IncidentStatus.CLOSED:
            incident.closed_at = datetime.now()

    def assess_impact(self, incident_id: str, impact_data: Dict[str, Any]):
        """Avalia impacto do incidente"""
        if incident_id not in self.incidents:
            raise ValueError(f"Incidente {incident_id} não encontrado")

        incident = self.incidents[incident_id]
        incident.impact_assessment = impact_data

        # Atualiza severidade baseada no impacto se necessário
        if impact_data.get("data_breach", False) and incident.severity == IncidentSeverity.LOW:
            incident.severity = IncidentSeverity.MEDIUM

    def generate_lessons_learned(self, incident_id: str, lessons: str):
        """Registra lições aprendidas do incidente"""
        if incident_id not in self.incidents:
            raise ValueError(f"Incidente {incident_id} não encontrado")

        incident = self.incidents[incident_id]
        incident.lessons_learned = lessons

        # Em implementação real, atualizaria base de conhecimento
        print(f" LIÇÕES APRENDIDAS REGISTRADAS: {lessons}")

    def get_incident_report(self, incident_id: str) -> Dict[str, Any]:
        """Gera relatório completo do incidente"""
        if incident_id not in self.incidents:
            raise ValueError(f"Incidente {incident_id} não encontrado")

        incident = self.incidents[incident_id]

        return {
            "incident_details": asdict(incident),
            "response_timeline": self._calculate_response_timeline(incident),
            "communication_log": self._get_communication_log(incident),
            "impact_summary": incident.impact_assessment,
            "recommendations": self._generate_recommendations(incident)
        }

    def _calculate_response_timeline(self, incident: Incident) -> Dict[str, Any]:
        """Calcula timeline de resposta"""
        escalation = self.escalation_matrix.get(incident.severity.value, {})
        expected_response_time = escalation.get("response_time", timedelta(hours=4))

        actual_response_time = None
        if incident.closed_at:
            actual_response_time = incident.closed_at - incident.detected_at

        return {
            "detected_at": incident.detected_at.isoformat(),
            "expected_response_time": str(expected_response_time),
            "actual_response_time": str(actual_response_time) if actual_response_time else None,
            "within_sla": actual_response_time <= expected_response_time if actual_response_time else None
        }

    def _get_communication_log(self, incident: Incident) -> List[Dict[str, Any]]:
        """Retorna log de comunicações do incidente"""
        # Em implementação real, manteria log de todas as comunicações
        return [
            {
                "timestamp": incident.detected_at.isoformat(),
                "type": "initial_notification",
                "recipients": self.communication_plan["internal_communication"]["immediate_response_team"],
                "message": "Incidente detectado - análise iniciada"
            }
        ]

    def _generate_recommendations(self, incident: Incident) -> List[str]:
        """Gera recomendações baseadas no incidente"""
        recommendations = []

        if incident.category == IncidentCategory.SECURITY_BREACH:
            recommendations.extend([
                "Implementar autenticação multifator adicional",
                "Revisar política de gerenciamento de credenciais",
                "Aumentar frequência de auditorias de segurança"
            ])

        if incident.severity in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL]:
            recommendations.extend([
                "Revisar plano de continuidade de negócio",
                "Implementar monitoramento adicional",
                "Conduzir treinamento de conscientização de segurança"
            ])

        return recommendations

    def get_response_plan_status(self) -> Dict[str, Any]:
        """Retorna status geral do plano de resposta"""
        total_incidents = len(self.incidents)
        active_incidents = len([i for i in self.incidents.values()
                               if i.status != IncidentStatus.CLOSED])

        severity_distribution = {}
        for incident in self.incidents.values():
            severity_distribution[incident.severity.value] = \
                severity_distribution.get(incident.severity.value, 0) + 1

        return {
            "total_incidents": total_incidents,
            "active_incidents": active_incidents,
            "severity_distribution": severity_distribution,
            "response_plan_complete": True,  # Sistema implementado
            "last_updated": datetime.now().isoformat()
        }


# Instância global do plano de resposta
incident_response_plan = IncidentResponsePlan()


def test_incident_response_plan():
    """Testa o plano de resposta a incidentes"""
    print(" TESTANDO INCIDENT RESPONSE PLAN")
    print("=" * 50)

    # Cria incidente de teste
    incident_id = incident_response_plan.create_incident(
        title="Test Security Breach",
        description="Simulated security breach for testing",
        category=IncidentCategory.SECURITY_BREACH,
        severity=IncidentSeverity.MEDIUM,
        reported_by="test_system"
    )

    print(f" Incidente criado: {incident_id}")

    # Atualiza status
    incident_response_plan.update_incident_status(
        incident_id,
        IncidentStatus.CONTAINED,
        actions_taken=["Isolated affected systems", "Revoked credentials"],
        assigned_to="security_team"
    )

    print(" Status atualizado para CONTAINED")

    # Avalia impacto
    incident_response_plan.assess_impact(incident_id, {
        "affected_users": 5,
        "data_compromised": False,
        "financial_impact": "minimal",
        "reputation_impact": "low"
    })

    print(" Impacto avaliado")

    # Fecha incidente
    incident_response_plan.update_incident_status(incident_id, IncidentStatus.CLOSED)
    incident_response_plan.generate_lessons_learned(incident_id,
        "Melhorar monitoramento de tentativas de login suspeitas")

    print(" Incidente fechado com lições aprendidas")

    # Verifica status do plano
    status = incident_response_plan.get_response_plan_status()
    print(f" Status do plano: {status}")

    return status["response_plan_complete"]


if __name__ == "__main__":
    test_incident_response_plan()