#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes para CertificationTracker (Rib 6)

Casos de teste:
1. Teste de catálogo completo (4 certificações)
2. Teste de readiness por certificação
3. Teste de roadmap consolidado
4. Teste de priorização
5. Teste de custos e timelines
"""

import pytest
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from core.quantum.certification_tracker import (
    CertificationTracker,
    Certification,
    ReadinessReport,
    CertificationStatus
)


class TestCertificationTracker:
    """Testes para CertificationTracker"""
    
    @pytest.fixture
    def tracker(self):
        """Fixture que retorna tracker configurado"""
        return CertificationTracker()
    
    def test_catalogo_completo(self, tracker):
        """Teste 1: Validar que todas as 4 certificações existem"""
        assert 'FIPS1403' in tracker.CERTIFICATIONS
        assert 'ISO27001' in tracker.CERTIFICATIONS
        assert 'COMMONCRITERIA' in tracker.CERTIFICATIONS
        assert 'NISTPQC' in tracker.CERTIFICATIONS
        
        # Validar estrutura de cada certificação
        for cert_key, cert in tracker.CERTIFICATIONS.items():
            assert isinstance(cert, Certification)
            assert hasattr(cert, 'name')
            assert hasattr(cert, 'cost_usd')
            assert hasattr(cert, 'timeline_months')
            assert hasattr(cert, 'priority')
            assert hasattr(cert, 'requirements')
            
            # Validar tipos
            assert isinstance(cert.name, str)
            assert isinstance(cert.cost_usd, int)
            assert isinstance(cert.timeline_months, tuple)
            assert isinstance(cert.priority, int)
            assert isinstance(cert.requirements, list)
            
            # Validar valores razoáveis
            assert cert.cost_usd >= 0
            assert len(cert.timeline_months) == 2
            assert cert.timeline_months[0] <= cert.timeline_months[1]
            assert cert.priority in [1, 2, 3]
            assert len(cert.requirements) > 0
    
    def test_readiness_por_certificacao(self, tracker):
        """Teste 2: Readiness deve ter estrutura completa"""
        for cert_key in tracker.CERTIFICATIONS.keys():
            report = tracker.assess_readiness(cert_key)
            
            assert isinstance(report, ReadinessReport)
            
            # Validar campos
            assert hasattr(report, 'certification_name')
            assert hasattr(report, 'current_readiness')
            assert hasattr(report, 'status')
            assert hasattr(report, 'gaps')
            assert hasattr(report, 'actions_required')
            assert hasattr(report, 'estimated_effort_weeks')
            assert hasattr(report, 'estimated_cost_usd')
            
            # Validar tipos e valores
            assert isinstance(report.certification_name, str)
            assert 0.0 <= report.current_readiness <= 1.0
            assert isinstance(report.status, str)
            assert isinstance(report.gaps, list)
            assert isinstance(report.actions_required, list)
            assert isinstance(report.estimated_effort_weeks, int)
            assert isinstance(report.estimated_cost_usd, int)
            
            # Validar que gaps e ações não estão vazias
            assert len(report.gaps) > 0
            assert len(report.actions_required) > 0
    
    def test_roadmap_consolidado(self, tracker):
        """Teste 3: Roadmap deve consolidar todas as certificações"""
        roadmap = tracker.generate_roadmap()
        
        assert isinstance(roadmap, dict)
        assert 'certifications' in roadmap
        assert 'total_cost_usd' in roadmap
        assert 'total_weeks' in roadmap
        assert 'priority_order' in roadmap
        
        # Validar certifications
        assert len(roadmap['certifications']) == 4
        
        for cert in roadmap['certifications']:
            assert 'name' in cert
            assert 'readiness' in cert
            assert 'status' in cert
            assert 'effort_weeks' in cert
            assert 'cost_usd' in cert
        
        # Validar totais
        assert isinstance(roadmap['total_cost_usd'], int)
        assert isinstance(roadmap['total_weeks'], int)
        assert roadmap['total_cost_usd'] >= 0
        assert roadmap['total_weeks'] >= 0
    
    def test_priorizacao(self, tracker):
        """Teste 4: Ordem de prioridade deve estar correta"""
        roadmap = tracker.generate_roadmap()
        priority_order = roadmap['priority_order']
        
        # Validar que existem 4 certificações na ordem
        assert len(priority_order) == 4
        
        # FIPS e NIST devem ter prioridade 1 (aparecer primeiro)
        # ISO deve ter prioridade 2
        # Common Criteria deve ter prioridade 3 (último)
        assert 'Common Criteria EAL4+' == priority_order[-1]
        
        # Validar que FIPS e NIST estão no top 2
        top2 = priority_order[:2]
        assert 'FIPS 140-3' in top2
        assert 'NIST PQC Submission' in top2
    
    def test_custos_timelines_realistas(self, tracker):
        """Teste 5: Custos e timelines devem ser realistas"""
        # Validar catálogo
        for cert_key, cert in tracker.CERTIFICATIONS.items():
            # FIPS: $50k, 12-18 meses
            if cert_key == 'FIPS1403':
                assert cert.cost_usd == 50000
                assert cert.timeline_months == (12, 18)
            
            # ISO: $30k, 6-12 meses
            elif cert_key == 'ISO27001':
                assert cert.cost_usd == 30000
                assert cert.timeline_months == (6, 12)
            
            # Common Criteria: $80k, 18-24 meses
            elif cert_key == 'COMMONCRITERIA':
                assert cert.cost_usd == 80000
                assert cert.timeline_months == (18, 24)
            
            # NIST PQC: $0 (submissão gratuita), 24-36 meses
            elif cert_key == 'NISTPQC':
                assert cert.cost_usd == 0
                assert cert.timeline_months == (24, 36)
        
        # Validar que readiness impacta custos
        for cert_key in tracker.CERTIFICATIONS.keys():
            report = tracker.assess_readiness(cert_key)
            cert = tracker.CERTIFICATIONS[cert_key]
            
            # Custo estimado deve ser <= custo total
            assert report.estimated_cost_usd <= cert.cost_usd
            
            # Se readiness é alta, custo estimado deve ser baixo
            if report.current_readiness > 0.8:
                assert report.estimated_cost_usd < cert.cost_usd * 0.3


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
