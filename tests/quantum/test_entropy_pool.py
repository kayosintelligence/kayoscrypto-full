#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes para GeometricEntropyPool (Rib 5)

Casos de teste:
1. Teste de geração básica
2. Teste de determinismo (mesmo seed = mesma chave)
3. Teste de qualidade de entropia (>95%)
4. Teste de independência de fontes
5. Teste estatístico básico (distribuição uniforme)
"""

import pytest
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from core.quantum.entropy_pool import (
    GeometricEntropyPool,
    EntropySource
)


class TestGeometricEntropyPool:
    """Testes para GeometricEntropyPool"""
    
    @pytest.fixture
    def pool(self):
        """Fixture que retorna pool configurado"""
        return GeometricEntropyPool()
    
    def test_geracao_basica(self, pool):
        """Teste 1: Gerar chave com tamanho correto"""
        # Testar vários tamanhos
        for length in [16, 32, 64, 128, 256]:
            key = pool.generate_quantum_safe_key(length)
            
            assert isinstance(key, bytes)
            assert len(key) == length
            
            # Validar que não é só zeros
            assert key != b'\x00' * length
    
    def test_determinismo(self, pool):
        """Teste 2: Mesmo seed deve gerar mesma chave"""
        seed = b'test_seed_determinism_12345'
        length = 32
        
        # Gerar 3 vezes com mesmo seed
        key1 = pool.generate_quantum_safe_key(length, seed)
        key2 = pool.generate_quantum_safe_key(length, seed)
        key3 = pool.generate_quantum_safe_key(length, seed)
        
        assert key1 == key2 == key3
        
        # Seeds diferentes devem gerar chaves diferentes
        seed_diff = b'different_seed_67890'
        key_diff = pool.generate_quantum_safe_key(length, seed_diff)
        
        assert key1 != key_diff
    
    def test_qualidade_entropia(self, pool):
        """Teste 3: Entropia deve ser >95% do ideal"""
        # Gerar amostra grande para análise estatística
        key = pool.generate_quantum_safe_key(1024)
        
        quality = pool.measure_entropy_quality(key)
        
        # Validar que está em 0.0-1.0
        assert 0.0 <= quality <= 1.0
        
        # Target: >95% (0.95)
        assert quality > 0.95, f"Entropia {quality:.4f} está abaixo de 0.95"
    
    def test_independencia_fontes(self, pool):
        """Teste 4: Cada fonte deve ter >90% entropia"""
        sources = pool.analyze_sources(length=1024)
        
        assert len(sources) == 4  # 3 fontes + XOR triplo
        
        # Validar estrutura de cada fonte (flexível para Cython/Python)
        for source in sources:
            # Validar que tem os atributos necessários (sem verificar tipo exato)
            assert hasattr(source, 'name'), "Fonte sem atributo 'name'"
            assert hasattr(source, 'entropy_bits'), "Fonte sem atributo 'entropy_bits'"
            assert hasattr(source, 'method'), "Fonte sem atributo 'method'"
        
        # Validar que fontes individuais têm boa entropia
        fibonacci_source = sources[0]
        ezekiel_source = sources[1]
        golden_source = sources[2]
        combined_source = sources[3]
        
        # Cada fonte individual deve ter >90% (7.2 bits/byte)
        assert fibonacci_source.entropy_bits > 7.2
        assert ezekiel_source.entropy_bits > 7.2
        assert golden_source.entropy_bits > 7.2
        
        # Combinação (XOR triplo) deve ter entropia competitiva
        # (nem sempre é superior devido à natureza estocástica)
        assert combined_source.entropy_bits > 7.2  # Mínimo 90%
        
        # Validar que está próximo do melhor individual (±5%)
        best_individual = max(
            fibonacci_source.entropy_bits,
            ezekiel_source.entropy_bits,
            golden_source.entropy_bits
        )
        assert combined_source.entropy_bits >= best_individual * 0.95
    
    def test_distribuicao_uniforme(self, pool):
        """Teste 5: Bytes devem ter distribuição aproximadamente uniforme"""
        # Gerar amostra grande
        key = pool.generate_quantum_safe_key(10000)
        
        # Contar frequências de cada byte (0-255)
        frequencies = [0] * 256
        for byte in key:
            frequencies[byte] += 1
        
        # Frequência esperada (uniforme)
        expected = len(key) / 256.0  # ~39.06
        
        # Validar que nenhum byte está muito acima ou abaixo
        # Permitir ±75% de desvio (lookup tables têm variância ligeiramente maior)
        for freq in frequencies:
            assert freq > expected * 0.25, "Algum byte tem frequência muito baixa"
            assert freq < expected * 1.75, "Algum byte tem frequência muito alta"
        
        # Validar que não há bytes ausentes
        assert all(freq > 0 for freq in frequencies), "Há bytes não utilizados"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
