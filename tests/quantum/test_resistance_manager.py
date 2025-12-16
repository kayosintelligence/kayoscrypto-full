#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes para QuantumResistanceManager (Rib 4)

Casos de teste:
1. Teste de scores por fase (0.0-1.0)
2. Teste de semáforo ()
3. Teste de recomendações
4. Teste de ações concretas
5. Teste de serialização de relatório
"""

import pytest
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from core.quantum.resistance_manager import (
    QuantumResistanceManager,
    ResistanceLevel,
    ResistanceScorecard,
)


class TestQuantumResistanceManager:
    """Testes para QuantumResistanceManager"""
    
    @pytest.fixture
    def manager(self):
        """Fixture que retorna manager configurado"""
        return QuantumResistanceManager()
    
    def test_scores_por_fase(self, manager):
        """Teste 1: Validar scores por fase estão em 0.0-1.0"""
        report = manager.assess_vulnerability()
        
        assert 0.0 <= report.phase1_fibonacci_resistance <= 1.0
        assert 0.0 <= report.phase2_ezekiel_resistance <= 1.0
        assert 0.0 <= report.phase3_core_resistance <= 1.0
        assert 0.0 <= report.overall_score <= 1.0
        assert isinstance(report.scorecard, ResistanceScorecard)
        assert 0.0 <= report.scorecard.composite_score <= 1.0
        assert set(report.threat_scores.keys()) >= {'shor', 'grover', 'entropy'}
    
    def test_semaforo_correto(self, manager):
        """Teste 2: Semáforo deve corresponder ao score geral"""
        report = manager.assess_vulnerability()
        
        # Validar lógica de semáforo
        if report.overall_score >= 0.85:
            assert report.semaphore == ResistanceLevel.GREEN.value
        elif report.overall_score >= 0.65:
            assert report.semaphore == ResistanceLevel.YELLOW.value
        else:
            assert report.semaphore == ResistanceLevel.RED.value
        
        # Validar que semáforo é um dos 3 valores
        assert report.semaphore in {
            ResistanceLevel.RED.value,
            ResistanceLevel.YELLOW.value,
            ResistanceLevel.GREEN.value,
        }
        assert report.scorecard.semaphore == report.semaphore
    
    def test_recomendacoes_nao_vazias(self, manager):
        """Teste 3: Deve gerar pelo menos uma recomendação"""
        report = manager.assess_vulnerability()
        
        assert len(report.recommendations) > 0
        assert isinstance(report.recommendations, list)
        assert isinstance(report.findings, list)
        assert len(report.findings) > 0

        # Validar que recomendações são strings não vazias
        for rec in report.recommendations:
            assert isinstance(rec, str)
            assert len(rec) > 0
    
    def test_acoes_concretas(self, manager):
        """Teste 4: Ações devem ter estrutura completa"""
        report = manager.assess_vulnerability()
        actions = manager.recommend_improvements(report)
        
        assert len(actions) > 0
        assert isinstance(actions, list)
        
        # Validar estrutura de cada ação
        for action in actions:
            assert 'action' in action
            assert 'priority' in action
            assert 'estimated_impact' in action
            assert 'timeline' in action
            
            # Validar tipos
            assert isinstance(action['action'], str)
            assert isinstance(action['priority'], str)
            assert isinstance(action['estimated_impact'], str)
            assert isinstance(action['timeline'], str)
            
            # Validar prioridades válidas
            assert action['priority'] in ['CRÍTICA', 'ALTA', 'MÉDIA', 'BAIXA']
    
    def test_serializacao_relatorio(self, manager):
        """Teste 5: Relatório deve ser serializável para dict"""
        report = manager.assess_vulnerability()
        
        # Testar to_dict()
        report_dict = report.to_dict()
        
        assert isinstance(report_dict, dict)
        assert 'phase1_fibonacci' in report_dict
        assert 'phase2_ezekiel' in report_dict
        assert 'phase3_core' in report_dict
        assert 'overall_score' in report_dict
        assert 'semaphore' in report_dict
        assert 'recommendations' in report_dict
        assert 'scorecard' in report_dict
        assert 'threat_scores' in report_dict
        assert 'findings' in report_dict
        
        # Validar que valores são serializáveis
        assert isinstance(report_dict['phase1_fibonacci'], float)
        assert isinstance(report_dict['phase2_ezekiel'], float)
        assert isinstance(report_dict['phase3_core'], float)
        assert isinstance(report_dict['overall_score'], float)
        assert isinstance(report_dict['semaphore'], str)
        assert isinstance(report_dict['recommendations'], list)
        assert isinstance(report_dict['scorecard'], dict)
        assert isinstance(report_dict['threat_scores'], dict)
        assert isinstance(report_dict['findings'], list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
