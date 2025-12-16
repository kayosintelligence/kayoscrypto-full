#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rib 6: CertificationTracker
============================

Responsabilidade: Rastrear progresso para certificações (FIPS 140-3, ISO 27001,
                 Common Criteria, NIST PQC) e gerar gap analysis detalhado.

Arquitetura: Fishbone Rib (Specialized Module)
Filosofia: KAIOS - O Relojoeiro (otimização de timeline e custos)
Versão: v6.0.0-alpha

Author: KAYOS Systems
Date: 15 de Novembro de 2025
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Any
import json
from pathlib import Path
from datetime import datetime, timezone


class CertificationStatus(Enum):
    """Status de certificação"""
    NOT_STARTED = " Não iniciado"
    IN_PROGRESS = " Em progresso"
    READY = " Pronto para submissão"
    SUBMITTED = " Submetido"
    CERTIFIED = " Certificado"


@dataclass
class Certification:
    """Certificação formal"""
    name: str
    cost_usd: int
    timeline_months: Tuple[int, int]  # (min, max)
    priority: int  # 1=alta, 2=média, 3=baixa
    requirements: List[str]
    
    def __repr__(self):
        return f"{self.name} (${self.cost_usd:,}, {self.timeline_months[0]}-{self.timeline_months[1]} meses)"


@dataclass
class ReadinessReport:
    """Relatório de prontidão para certificação"""
    certification_name: str
    current_readiness: float  # 0.0-1.0
    status: str  # Semáforo
    gaps: List[str]
    actions_required: List[Dict]
    estimated_effort_weeks: int
    estimated_cost_usd: int
    
    def to_dict(self) -> Dict:
        return {
            'certification': self.certification_name,
            'readiness': f"{self.current_readiness:.1%}",
            'status': self.status,
            'gaps': self.gaps,
            'actions': self.actions_required,
            'effort_weeks': self.estimated_effort_weeks,
            'cost_usd': self.estimated_cost_usd
        }


class CertificationTracker:
    """
    Rastreador de Certificações
    
    Gerencia 4 certificações principais:
    1. FIPS 140-3 (NIST - validação criptográfica)
    2. ISO 27001 (segurança da informação)
    3. Common Criteria EAL4+ (avaliação de segurança)
    4. NIST PQC (criptografia pós-quântica)
    
    Princípios KAIOS:
    - Relojoeiro: Otimizar custos e timeline
    - Vidente: Prever próximos passos necessários
    - Neurônio Espelho: Entender requisitos profundamente
    """
    
    # Catálogo de certificações
    CERTIFICATIONS = {
        'FIPS1403': Certification(
            name="FIPS 140-3",
            cost_usd=50000,
            timeline_months=(12, 18),
            priority=1,
            requirements=[
                "Documentação formal do algoritmo",
                "Análise de segurança por terceiros",
                "Implementação em hardware validado",
                "Testes CAVP (Cryptographic Algorithm Validation Program)",
                "Gerenciamento de chaves certificado",
                "Self-tests implementados",
                "Proteção física do módulo"
            ]
        ),
        'ISO27001': Certification(
            name="ISO 27001",
            cost_usd=30000,
            timeline_months=(6, 12),
            priority=2,
            requirements=[
                "ISMS (Information Security Management System)",
                "Política de segurança documentada",
                "Avaliação de riscos formal",
                "Controles de acesso implementados",
                "Plano de continuidade de negócios",
                "Auditoria interna completa",
                "Treinamento de equipe"
            ]
        ),
        'COMMONCRITERIA': Certification(
            name="Common Criteria EAL4+",
            cost_usd=80000,
            timeline_months=(18, 24),
            priority=3,
            requirements=[
                "Protection Profile (PP) definido",
                "Security Target (ST) documentado",
                "Análise formal de ameaças",
                "Testes de penetração por terceiros",
                "Revisão de código por especialistas",
                "Documentação de design detalhada",
                "Evidências de desenvolvimento seguro"
            ]
        ),
        'NISTPQC': Certification(
            name="NIST PQC Submission",
            cost_usd=0,  # Submissão gratuita, mas requer recursos
            timeline_months=(24, 36),
            priority=1,
            requirements=[
                "Prova matemática de segurança",
                "Implementação de referência",
                "Especificação formal completa",
                "Análise de resistência quântica",
                "Benchmarks de performance",
                "Análise de side-channels",
                "Whitepaper acadêmico"
            ]
        )
    }
    
    SNAPSHOT_DIR = Path("reports/certifications")

    def __init__(self):
        # Estado atual do KayosCrypto (baseline v5.0.1)
        self.current_state = {
            'documentation': 0.95,  # Docs excelentes
            'testing': 1.00,        # 9/9 testes passando
            'performance': 0.85,    # 351-500 KB/s
            'quantum_resistance': 0.75,  # Estimativa atual
            'code_quality': 0.90,   # Bem estruturado
            'security_analysis': 0.30,  # Falta análise formal
        }
        self.SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    
    def assess_readiness(self, cert_key: str) -> ReadinessReport:
        """
        Avalia prontidão para certificação específica
        
        Args:
            cert_key: Chave da certificação (FIPS1403, ISO27001, etc.)
        
        Returns:
            ReadinessReport com gap analysis detalhado
        """
        if cert_key not in self.CERTIFICATIONS:
            raise ValueError(f"Certificação inválida: {cert_key}")
        
        cert = self.CERTIFICATIONS[cert_key]
        
        # Cálculo de readiness baseado em requisitos
        if cert_key == 'FIPS1403':
            readiness, gaps, actions = self._assess_fips140()
        elif cert_key == 'ISO27001':
            readiness, gaps, actions = self._assess_iso27001()
        elif cert_key == 'COMMONCRITERIA':
            readiness, gaps, actions = self._assess_common_criteria()
        elif cert_key == 'NISTPQC':
            readiness, gaps, actions = self._assess_nist_pqc()
        else:
            readiness, gaps, actions = 0.0, ["Não implementado"], []
        
        # Determinar status
        if readiness >= 0.85:
            status = CertificationStatus.READY.value
        elif readiness >= 0.50:
            status = CertificationStatus.IN_PROGRESS.value
        else:
            status = CertificationStatus.NOT_STARTED.value
        
        # Estimar esforço
        effort_weeks = int((1.0 - readiness) * cert.timeline_months[1] * 4)
        cost = int((1.0 - readiness) * cert.cost_usd)
        
        return ReadinessReport(
            certification_name=cert.name,
            current_readiness=readiness,
            status=status,
            gaps=gaps,
            actions_required=actions,
            estimated_effort_weeks=effort_weeks,
            estimated_cost_usd=cost
        )

    # ------------------------------------------------------------------
    # Dynamic state updates (Quantum Assurance integration)
    # ------------------------------------------------------------------

    def update_system_state(self, **kwargs) -> None:
        """Atualiza estado interno com valores normalizados (0-1)."""
        for key, value in kwargs.items():
            if key in self.current_state:
                try:
                    numeric = float(value)
                except (TypeError, ValueError):
                    continue
                self.current_state[key] = max(0.0, min(1.0, numeric))

    def update_from_assurance(
        self,
        metrics: Dict[str, float],
        *,
        hooks: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
        performance_kbps: Optional[float] = None,
        scorecard: Optional[Dict[str, Any]] = None,
        findings: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Atualiza métricas internas com relatório Quantum Assurance e persiste snapshot."""

        readiness_index = None
        target_delta = None
        semaphore = None
        if scorecard:
            readiness_index = float(scorecard.get('readiness_index', 0.0) or 0.0)
            target_delta = scorecard.get('target_delta')
            semaphore = scorecard.get('semaphore')
        quantum_score = readiness_index if readiness_index is not None else self._score_quantum_resistance(metrics)
        self.current_state['quantum_resistance'] = quantum_score
        if target_delta is not None:
            self.current_state['quantum_target_delta'] = target_delta

        if performance_kbps is not None:
            normalized_perf = min(max(performance_kbps / 500.0, 0.0), 1.0)
            self.current_state['performance'] = max(self.current_state['performance'], normalized_perf)

        # Ajuste adicional: key strength reforça security_analysis (parcial)
        key_bits = float(metrics.get('key_bits', 0.0) or 0.0)
        if key_bits > 0:
            key_strength = min(key_bits / 1024.0, 1.0)
            self.current_state['security_analysis'] = max(
                self.current_state['security_analysis'],
                key_strength * 0.5,
            )

        roadmap = self.generate_roadmap()
        timestamp = datetime.now(timezone.utc).isoformat()
        snapshot = {
            'timestamp': timestamp,
            'metrics': metrics,
            'quantum_score': quantum_score,
            'performance_kbps': performance_kbps,
            'hooks': hooks or {},
            'suggestions': suggestions or [],
            'context': context or {},
            'roadmap': roadmap,
        }
        if scorecard:
            snapshot['scorecard'] = scorecard
            snapshot['target_delta'] = target_delta
            snapshot['quantum_semaphore'] = semaphore
        if findings:
            snapshot['findings'] = findings
        self._persist_snapshot(snapshot)
        return snapshot

    @staticmethod
    def _score_quantum_resistance(metrics: Dict[str, float]) -> float:
        avalanche = max(0.0, min(1.0, float(metrics.get('avalanche', 0.0) or 0.0)))
        entropy = max(0.0, min(1.0, float(metrics.get('entropy', 0.0) or 0.0)))
        log_sensitivity = float(metrics.get('log_sensitivity', 0.0) or 0.0)
        sensitivity_component = 1.0 - max(0.0, min(1.0, log_sensitivity))
        key_bits = float(metrics.get('key_bits', 0.0) or 0.0)
        key_component = min(max(key_bits / 512.0, 0.0), 1.0)
        components = [avalanche, entropy, sensitivity_component, key_component]
        return sum(components) / len(components)

    def _persist_snapshot(self, snapshot: Dict[str, Any]) -> Optional[str]:
        try:
            timestamp = snapshot.get('timestamp', datetime.now(timezone.utc).isoformat())
            safe_timestamp = timestamp.replace(':', '-').replace('.', '_')
            filename = self.SNAPSHOT_DIR / f"cert_snapshot_{safe_timestamp}.json"
            with filename.open('w', encoding='utf-8') as f:
                json.dump(snapshot, f, indent=2)
            snapshot['persisted_to'] = str(filename)
            return str(filename)
        except OSError:
            # Persistência é melhor-effort; ignorar erros de IO
            return None

    @classmethod
    def latest_snapshot(cls) -> Optional[Dict[str, Any]]:
        directory = cls.SNAPSHOT_DIR
        if not directory.exists():
            return None
        candidates = sorted(
            directory.glob("cert_snapshot_*.json"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        for candidate in candidates:
            try:
                with candidate.open('r', encoding='utf-8') as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError):
                continue
        return None
    
    def _assess_fips140(self) -> Tuple[float, List[str], List[Dict]]:
        """Avalia FIPS 140-3 readiness"""
        scores = {
            'documentation': self.current_state['documentation'] * 0.20,
            'algorithm_formal': 0.30 * 0.15,  # 30% completo
            'cavp_tests': 0.00 * 0.20,  # Não implementado
            'key_management': 0.50 * 0.15,  # Parcial
            'self_tests': 0.00 * 0.15,  # Não implementado
            'hardware': 0.00 * 0.15  # Não implementado
        }
        
        readiness = sum(scores.values())
        
        gaps = [
            " Falta documentação formal matemática do algoritmo",
            " Testes CAVP não implementados",
            " Self-tests ausentes",
            " Implementação em hardware não validado",
            " Gerenciamento de chaves precisa auditoria"
        ]
        
        actions = [
            {
                'action': 'Contratar consultor FIPS certificado',
                'priority': 'CRÍTICA',
                'cost_usd': 15000,
                'weeks': 2
            },
            {
                'action': 'Desenvolver self-tests (POST/KAT)',
                'priority': 'ALTA',
                'cost_usd': 8000,
                'weeks': 4
            },
            {
                'action': 'Implementar em HSM validado',
                'priority': 'ALTA',
                'cost_usd': 12000,
                'weeks': 6
            }
        ]
        
        return readiness, gaps, actions
    
    def _assess_iso27001(self) -> Tuple[float, List[str], List[Dict]]:
        """Avalia ISO 27001 readiness"""
        scores = {
            'isms': 0.40 * 0.25,  # Parcial
            'policy': self.current_state['documentation'] * 0.20,
            'risk_assessment': 0.50 * 0.20,
            'access_control': 0.70 * 0.15,
            'bcp': 0.00 * 0.10,  # Business Continuity Plan
            'audit': 0.00 * 0.10
        }
        
        readiness = sum(scores.values())
        
        gaps = [
            " ISMS não formalizado",
            " Plano de continuidade ausente",
            " Auditoria interna não realizada",
            " Avaliação de riscos incompleta"
        ]
        
        actions = [
            {
                'action': 'Implementar ISMS básico',
                'priority': 'ALTA',
                'cost_usd': 10000,
                'weeks': 8
            },
            {
                'action': 'Criar plano de continuidade',
                'priority': 'MÉDIA',
                'cost_usd': 5000,
                'weeks': 4
            }
        ]
        
        return readiness, gaps, actions
    
    def _assess_common_criteria(self) -> Tuple[float, List[str], List[Dict]]:
        """Avalia Common Criteria EAL4+ readiness"""
        scores = {
            'protection_profile': 0.00 * 0.20,
            'security_target': 0.20 * 0.20,
            'threat_analysis': 0.40 * 0.15,
            'penetration_tests': 0.00 * 0.15,
            'code_review': 0.60 * 0.15,
            'design_docs': self.current_state['documentation'] * 0.15
        }
        
        readiness = sum(scores.values())
        
        gaps = [
            " Protection Profile não definido",
            " Security Target ausente",
            " Testes de penetração não realizados",
            " Análise de ameaças incompleta"
        ]
        
        actions = [
            {
                'action': 'Desenvolver Protection Profile',
                'priority': 'ALTA',
                'cost_usd': 20000,
                'weeks': 12
            },
            {
                'action': 'Contratar pentest especializado',
                'priority': 'ALTA',
                'cost_usd': 15000,
                'weeks': 6
            }
        ]
        
        return readiness, gaps, actions
    
    def _assess_nist_pqc(self) -> Tuple[float, List[str], List[Dict]]:
        """Avalia NIST PQC submission readiness"""
        scores = {
            'math_proof': 0.30 * 0.25,  # Parcial
            'reference_impl': 0.80 * 0.15,  # Python OK
            'specification': 0.50 * 0.20,
            'quantum_analysis': self.current_state['quantum_resistance'] * 0.15,
            'benchmarks': self.current_state['performance'] * 0.10,
            'side_channels': 0.20 * 0.10,
            'whitepaper': 0.00 * 0.05
        }
        
        readiness = sum(scores.values())
        
        gaps = [
            " Prova matemática formal incompleta",
            " Whitepaper acadêmico ausente",
            " Análise de side-channels superficial",
            " Especificação formal não finalizada"
        ]
        
        actions = [
            {
                'action': 'Contratar criptógrafo Ph.D.',
                'priority': 'CRÍTICA',
                'cost_usd': 25000,
                'weeks': 16
            },
            {
                'action': 'Desenvolver whitepaper',
                'priority': 'ALTA',
                'cost_usd': 8000,
                'weeks': 8
            },
            {
                'action': 'Análise de side-channels formal',
                'priority': 'ALTA',
                'cost_usd': 12000,
                'weeks': 6
            }
        ]
        
        return readiness, gaps, actions
    
    def generate_roadmap(self) -> Dict:
        """
        Gera roadmap completo de certificações
        
        Returns:
            Dict com timeline, custos e prioridades
        """
        roadmap = {
            'certifications': [],
            'total_cost_usd': 0,
            'total_weeks': 0,
            'priority_order': []
        }
        
        for key in self.CERTIFICATIONS.keys():
            report = self.assess_readiness(key)
            
            roadmap['certifications'].append({
                'name': report.certification_name,
                'readiness': f"{report.current_readiness:.1%}",
                'status': report.status,
                'effort_weeks': report.estimated_effort_weeks,
                'cost_usd': report.estimated_cost_usd
            })
            
            roadmap['total_cost_usd'] += report.estimated_cost_usd
            roadmap['total_weeks'] = max(roadmap['total_weeks'], 
                                         report.estimated_effort_weeks)
        
        # Ordenar por prioridade
        priority_list = sorted(
            self.CERTIFICATIONS.items(),
            key=lambda x: x[1].priority
        )
        roadmap['priority_order'] = [cert[1].name for cert in priority_list]
        
        return roadmap


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("RIB 6: CERTIFICATION TRACKER - DEMONSTRAÇÃO")
    print("=" * 70)
    
    tracker = CertificationTracker()
    
    # Avaliar cada certificação
    print("\n AVALIAÇÃO DE CERTIFICAÇÕES:")
    print("=" * 70)
    
    for cert_key, cert in tracker.CERTIFICATIONS.items():
        print(f"\n {cert.name}")
        print(f"   Custo: ${cert.cost_usd:,} | Timeline: {cert.timeline_months[0]}-{cert.timeline_months[1]} meses")
        
        report = tracker.assess_readiness(cert_key)
        print(f"   Prontidão: {report.current_readiness:.1%} {report.status}")
        print(f"   Esforço restante: {report.estimated_effort_weeks} semanas")
        print(f"   Custo estimado: ${report.estimated_cost_usd:,}")
        
        print(f"\n   Gaps identificados:")
        for gap in report.gaps[:3]:  # Top 3
            print(f"      {gap}")
    
    # Roadmap consolidado
    print("\n\n ROADMAP CONSOLIDADO:")
    print("=" * 70)
    
    roadmap = tracker.generate_roadmap()
    print(f"\n Custo total estimado: ${roadmap['total_cost_usd']:,}")
    print(f"⏱ Timeline máximo: {roadmap['total_weeks']} semanas (~{roadmap['total_weeks']//4} meses)")
    
    print(f"\n Ordem de prioridade:")
    for i, cert_name in enumerate(roadmap['priority_order'], 1):
        print(f"   {i}. {cert_name}")
    
    print("\n" + "=" * 70)
    print(" Tracker operacional! Use para planejar certificações.")
    print("=" * 70)
