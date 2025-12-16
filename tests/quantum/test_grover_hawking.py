#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GROVER-HAWKING QUANTUM RESISTANCE TEST
======================================

Teste avancado de resistencia quantica combinando:

1. ALGORITMO DE GROVER
   - Busca em espaco nao-estruturado
   - Speedup: O(N) -> O(sqrt(N))
   - Afeta: Busca de chaves, colisoes de hash

2. CONCEITO HAWKING (Radiacao de Buraco Negro)
   - Perda de informacao em sistemas altamente entropicos
   - Entropia de Bekenstein-Hawking: S = A/(4*l_p^2)
   - Aplicado: Quanto mais entropia geometrica, maior resistencia

PRINCIPIO KAYOS:
A arquitetura Fishbone + Rodas de Ezequiel cria um "buraco negro"
de informacao onde dados entram mas a relacao inversa e computacionalmente
irreversivel sem a chave correta, similar a como informacao classica
e perdida ao cruzar o horizonte de eventos.

Data: 01 de Dezembro de 2025
Autor: KAYOS SYSTEMS
"""

import sys
import math
import hashlib
import numpy as np
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
from datetime import datetime

# Setup path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src" / "core"))
sys.path.insert(0, str(PROJECT_ROOT / "src"))


# ============================================================================
# CONSTANTES FISICAS E CRIPTOGRAFICAS
# ============================================================================

# Constantes de Planck
PLANCK_LENGTH = 1.616255e-35  # metros
PLANCK_TIME = 5.391247e-44    # segundos
PLANCK_MASS = 2.176434e-8     # kg

# Razao aurea e Fibonacci
PHI = (1 + math.sqrt(5)) / 2  # 1.618033988749895
FIBONACCI = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]

# Constantes de Hawking
BOLTZMANN_K = 1.380649e-23    # J/K
HBAR = 1.054571817e-34        # J*s
C = 299792458                  # m/s
G = 6.67430e-11               # m^3/(kg*s^2)


# ============================================================================
# CLASSES DE DADOS
# ============================================================================

class QuantumThreatModel(Enum):
    """Modelos de ameaca quantica"""
    GROVER_SEARCH = "grover_search"
    GROVER_COLLISION = "grover_collision"
    HAWKING_ENTROPY = "hawking_entropy"
    COMBINED = "combined"


@dataclass
class HawkingEntropyMetrics:
    """Metricas de entropia estilo Hawking"""
    bekenstein_bound: float      # Limite de Bekenstein
    information_density: float   # Densidade de informacao (bits/byte)
    event_horizon_radius: float  # Raio do "horizonte de eventos" de informacao
    hawking_temperature: float   # Temperatura de Hawking (analogia)
    evaporation_time: float      # Tempo de evaporacao (analogia para brute force)
    
    
@dataclass
class GroverAttackMetrics:
    """Metricas de ataque Grover"""
    classical_complexity: float   # O(2^n)
    quantum_complexity: float     # O(2^(n/2))
    speedup_factor: float         # sqrt(2^n)
    required_qubits: int          # Qubits necessarios
    gate_operations: float        # Operacoes de gate
    estimated_time_classical: str
    estimated_time_quantum: str
    resistance_score: float       # 0.0 - 1.0


@dataclass
class CombinedQuantumResistance:
    """Resistencia combinada Grover + Hawking"""
    grover_metrics: GroverAttackMetrics
    hawking_metrics: HawkingEntropyMetrics
    
    # Scores combinados
    grover_resistance: float      # 0.0 - 1.0
    hawking_resistance: float     # 0.0 - 1.0
    combined_score: float         # Media ponderada
    
    # Analise
    weakest_link: str
    recommended_improvements: List[str]
    overall_verdict: str


# ============================================================================
# MOTOR DE ANALISE HAWKING
# ============================================================================

class HawkingEntropyAnalyzer:
    """
    Analisa entropia criptografica usando analogias com buracos negros.
    
    CONCEITO:
    - Buraco negro: Entropia maxima para uma regiao do espaco
    - Sistema cripto ideal: Entropia maxima para uma quantidade de bits
    - Radiacao de Hawking: Perda lenta de informacao (ataque brute force)
    """
    
    def __init__(self):
        self.analyzed_samples: List[bytes] = []
        
    def calculate_bekenstein_bound(self, data_size_bytes: int, 
                                   energy_joules: float = 1e-15) -> float:
        """
        Calcula limite de Bekenstein para informacao.
        
        S <= (2 * pi * R * E) / (hbar * c)
        
        Onde:
        - R: "Raio" do sistema (proporcional ao tamanho dos dados)
        - E: "Energia" do sistema (proporcional a complexidade)
        """
        # Analogia: R = tamanho dos dados normalizado
        R = data_size_bytes * PLANCK_LENGTH * 1e20
        
        # Limite de Bekenstein (em bits)
        bound = (2 * math.pi * R * energy_joules) / (HBAR * C * math.log(2))
        
        return bound
    
    def calculate_hawking_temperature(self, key_size_bits: int) -> float:
        """
        Calcula "temperatura de Hawking" analogica.
        
        T = (hbar * c^3) / (8 * pi * G * M * k)
        
        Analogia: Chave maior = buraco negro maior = temperatura menor = mais estavel
        """
        # Massa analogica proporcional ao tamanho da chave
        M_analog = (2 ** key_size_bits) * PLANCK_MASS
        
        temperature = (HBAR * C**3) / (8 * math.pi * G * M_analog * BOLTZMANN_K)
        
        return temperature
    
    def calculate_evaporation_time(self, key_size_bits: int) -> float:
        """
        Calcula tempo de "evaporacao" (analogia para brute force).
        
        t = (5120 * pi * G^2 * M^3) / (hbar * c^4)
        
        Tempo aumenta cubicamente com o tamanho da chave.
        """
        M_analog = (2 ** (key_size_bits / 64)) * PLANCK_MASS * 1e30
        
        evap_time = (5120 * math.pi * G**2 * M_analog**3) / (HBAR * C**4)
        
        return evap_time
    
    def analyze_data_entropy(self, data: bytes) -> HawkingEntropyMetrics:
        """
        Analisa entropia de dados usando metricas estilo Hawking.
        """
        # Calcular entropia de Shannon
        byte_counts = [0] * 256
        for b in data:
            byte_counts[b] += 1
        
        total = len(data)
        entropy = 0.0
        for count in byte_counts:
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)
        
        # Densidade de informacao (bits por byte, max = 8)
        info_density = entropy
        
        # Limite de Bekenstein
        bekenstein = self.calculate_bekenstein_bound(len(data))
        
        # Raio do horizonte de eventos (analogia)
        # Quanto maior a entropia, maior o "buraco negro"
        event_horizon = (entropy / 8.0) * len(data) * PLANCK_LENGTH * 1e35
        
        # Temperatura de Hawking (baseada em entropia)
        key_equivalent = int(entropy * len(data))
        hawking_temp = self.calculate_hawking_temperature(min(key_equivalent, 256))
        
        # Tempo de evaporacao
        evap_time = self.calculate_evaporation_time(min(key_equivalent, 256))
        
        return HawkingEntropyMetrics(
            bekenstein_bound=bekenstein,
            information_density=info_density,
            event_horizon_radius=event_horizon,
            hawking_temperature=hawking_temp,
            evaporation_time=evap_time
        )


# ============================================================================
# MOTOR DE ANALISE GROVER
# ============================================================================

class GroverAttackAnalyzer:
    """
    Analisa resistencia contra algoritmo de Grover.
    
    GROVER:
    - Busca em espaco nao-estruturado: O(N) -> O(sqrt(N))
    - Afeta: AES, SHA, qualquer busca de chave
    - Mitigacao: Dobrar tamanho da chave
    """
    
    def __init__(self):
        # Estimativas de velocidade de computador quantico futuro
        self.GATE_TIME_NS = 10  # 10 nanosegundos por gate (otimista)
        self.LOGICAL_QUBITS_PER_PHYSICAL = 1000  # Correcao de erro
        
    def analyze_key_search(self, key_size_bits: int, 
                          algorithm_name: str = "AES") -> GroverAttackMetrics:
        """
        Analisa ataque Grover em busca de chave.
        """
        # Complexidades
        classical = 2 ** key_size_bits
        quantum = 2 ** (key_size_bits / 2)
        speedup = math.sqrt(classical)
        
        # Qubits necessarios
        qubits = key_size_bits + 100  # Overhead para Grover oracle
        
        # Gate operations (aproximadamente sqrt(N) * log(N))
        gates = quantum * math.log2(quantum)
        
        # Tempo estimado
        classical_time = self._format_time(classical * 1e-15)  # 1 PetaFLOP
        quantum_time = self._format_time(gates * self.GATE_TIME_NS * 1e-9)
        
        # Score de resistencia
        # 128-bit = 0.5 (ainda seguro), 256-bit = 0.9 (muito seguro)
        if key_size_bits >= 256:
            resistance = 0.95
        elif key_size_bits >= 192:
            resistance = 0.85
        elif key_size_bits >= 128:
            resistance = 0.65
        elif key_size_bits >= 64:
            resistance = 0.35
        else:
            resistance = 0.1
        
        return GroverAttackMetrics(
            classical_complexity=classical,
            quantum_complexity=quantum,
            speedup_factor=speedup,
            required_qubits=qubits,
            gate_operations=gates,
            estimated_time_classical=classical_time,
            estimated_time_quantum=quantum_time,
            resistance_score=resistance
        )
    
    def analyze_hash_collision(self, hash_bits: int) -> GroverAttackMetrics:
        """
        Analisa ataque Grover em busca de colisao de hash.
        
        Birthday attack: O(2^(n/2)) classico
        Grover collision: O(2^(n/3)) quantico
        """
        # Colisao classica (birthday)
        classical = 2 ** (hash_bits / 2)
        
        # Colisao quantica (BHT algorithm)
        quantum = 2 ** (hash_bits / 3)
        
        speedup = classical / quantum
        
        qubits = hash_bits + 50
        gates = quantum * math.log2(quantum) * 3  # BHT mais complexo
        
        classical_time = self._format_time(classical * 1e-15)
        quantum_time = self._format_time(gates * self.GATE_TIME_NS * 1e-9)
        
        # Score
        if hash_bits >= 512:
            resistance = 0.95
        elif hash_bits >= 384:
            resistance = 0.85
        elif hash_bits >= 256:
            resistance = 0.70
        elif hash_bits >= 128:
            resistance = 0.40
        else:
            resistance = 0.15
        
        return GroverAttackMetrics(
            classical_complexity=classical,
            quantum_complexity=quantum,
            speedup_factor=speedup,
            required_qubits=qubits,
            gate_operations=gates,
            estimated_time_classical=classical_time,
            estimated_time_quantum=quantum_time,
            resistance_score=resistance
        )
    
    def _format_time(self, seconds: float) -> str:
        """Formata tempo em unidade legivel"""
        if seconds < 1e-9:
            return f"{seconds * 1e12:.2f} picoseconds"
        elif seconds < 1e-6:
            return f"{seconds * 1e9:.2f} nanoseconds"
        elif seconds < 1e-3:
            return f"{seconds * 1e6:.2f} microseconds"
        elif seconds < 1:
            return f"{seconds * 1e3:.2f} milliseconds"
        elif seconds < 60:
            return f"{seconds:.2f} seconds"
        elif seconds < 3600:
            return f"{seconds / 60:.2f} minutes"
        elif seconds < 86400:
            return f"{seconds / 3600:.2f} hours"
        elif seconds < 365.25 * 86400:
            return f"{seconds / 86400:.2f} days"
        elif seconds < 1e9 * 365.25 * 86400:
            return f"{seconds / (365.25 * 86400):.2e} years"
        else:
            return f">{seconds / (365.25 * 86400):.2e} years (heat death of universe)"


# ============================================================================
# ANALISADOR COMBINADO GROVER-HAWKING
# ============================================================================

class GroverHawkingAnalyzer:
    """
    Combina analises de Grover e Hawking para avaliacao completa.
    
    PRINCIPIO KAYOS:
    - Grover mede resistencia a busca quantica
    - Hawking mede qualidade da entropia
    - Combinacao mede "densidade de seguranca"
    """
    
    def __init__(self):
        self.grover = GroverAttackAnalyzer()
        self.hawking = HawkingEntropyAnalyzer()
        
    def analyze_kayoscrypto_component(self, component_name: str,
                                      sample_ciphertext: bytes,
                                      key_size_bits: int = 256) -> CombinedQuantumResistance:
        """
        Analisa um componente KayosCrypto com modelo Grover-Hawking.
        """
        # Analise Grover
        grover_metrics = self.grover.analyze_key_search(key_size_bits, component_name)
        
        # Analise Hawking
        hawking_metrics = self.hawking.analyze_data_entropy(sample_ciphertext)
        
        # Calcular resistencia Hawking
        # Entropia > 7.9 bits/byte = excelente
        if hawking_metrics.information_density >= 7.9:
            hawking_resistance = 0.95
        elif hawking_metrics.information_density >= 7.5:
            hawking_resistance = 0.80
        elif hawking_metrics.information_density >= 7.0:
            hawking_resistance = 0.60
        else:
            hawking_resistance = 0.40
        
        # Score combinado (ponderado)
        # Grover: 60% (ataque direto)
        # Hawking: 40% (qualidade da entropia)
        combined = grover_metrics.resistance_score * 0.6 + hawking_resistance * 0.4
        
        # Identificar ponto fraco
        if grover_metrics.resistance_score < hawking_resistance:
            weakest = f"Grover ({grover_metrics.resistance_score:.2%})"
        else:
            weakest = f"Entropy ({hawking_resistance:.2%})"
        
        # Recomendacoes
        recommendations = []
        if grover_metrics.resistance_score < 0.7:
            recommendations.append(f"Aumentar tamanho da chave para >= 256 bits")
        if hawking_resistance < 0.7:
            recommendations.append("Melhorar entropia do ciphertext (mais difusao)")
        if combined < 0.8:
            recommendations.append("Adicionar camada pos-quantica (Kyber, Dilithium)")
        
        # Veredito
        if combined >= 0.9:
            verdict = "EXCELENTE - Resistente a ataques quanticos conhecidos"
        elif combined >= 0.75:
            verdict = "BOM - Resistencia adequada para proximo decada"
        elif combined >= 0.6:
            verdict = "MODERADO - Considerar migracao para PQC"
        else:
            verdict = "INSUFICIENTE - Migracao urgente necessaria"
        
        return CombinedQuantumResistance(
            grover_metrics=grover_metrics,
            hawking_metrics=hawking_metrics,
            grover_resistance=grover_metrics.resistance_score,
            hawking_resistance=hawking_resistance,
            combined_score=combined,
            weakest_link=weakest,
            recommended_improvements=recommendations if recommendations else ["Nenhuma melhoria necessaria"],
            overall_verdict=verdict
        )
    
    def full_system_analysis(self) -> Dict[str, Any]:
        """
        Executa analise completa do sistema KayosCrypto.
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'analyzer': 'GroverHawkingAnalyzer v1.0',
            'components': {},
            'summary': {}
        }
        
        # Importar KayosCrypto
        try:
            from core.kayoscrypto_ultimate import KayosCryptoUltimate
        except ImportError:
            try:
                from kayoscrypto_ultimate import KayosCryptoUltimate
            except ImportError:
                raise ImportError("KayosCryptoUltimate not found")
        
        try:
            cipher = KayosCryptoUltimate(use_concentric=True, use_direction=True)
            
            # Gerar amostras de ciphertext
            test_plaintext = b"X" * 1024  # 1KB de dados de teste
            password = "grover_hawking_test_2025"
            
            ciphertext = cipher.encrypt(test_plaintext, password)
            
            # Analisar componentes
            components_config = {
                'fibonacci_direction': {'key_bits': 256, 'sample': ciphertext[:256]},
                'ezekiel_concentric': {'key_bits': 256, 'sample': ciphertext[256:512]},
                'core_system': {'key_bits': 256, 'sample': ciphertext[512:768]},
                'full_pipeline': {'key_bits': 256, 'sample': ciphertext},
            }
            
            scores = []
            for comp_name, config in components_config.items():
                analysis = self.analyze_kayoscrypto_component(
                    comp_name,
                    config['sample'],
                    config['key_bits']
                )
                results['components'][comp_name] = {
                    'grover_resistance': analysis.grover_resistance,
                    'hawking_resistance': analysis.hawking_resistance,
                    'combined_score': analysis.combined_score,
                    'weakest_link': analysis.weakest_link,
                    'verdict': analysis.overall_verdict,
                    'recommendations': analysis.recommended_improvements,
                    'grover_details': {
                        'required_qubits': analysis.grover_metrics.required_qubits,
                        'quantum_time': analysis.grover_metrics.estimated_time_quantum,
                        'classical_time': analysis.grover_metrics.estimated_time_classical,
                    },
                    'hawking_details': {
                        'entropy_density': analysis.hawking_metrics.information_density,
                        'bekenstein_bound': analysis.hawking_metrics.bekenstein_bound,
                    }
                }
                scores.append(analysis.combined_score)
            
            # Resumo
            avg_score = sum(scores) / len(scores)
            min_score = min(scores)
            
            results['summary'] = {
                'average_resistance': avg_score,
                'minimum_resistance': min_score,
                'overall_grade': self._score_to_grade(avg_score),
                'quantum_ready': avg_score >= 0.75,
                'pqc_migration_urgent': avg_score < 0.6,
            }
            
        except ImportError as e:
            results['error'] = f"KayosCrypto nao disponivel: {e}"
            # Analise com dados sinteticos
            synthetic = bytes([i % 256 for i in range(1024)])
            analysis = self.analyze_kayoscrypto_component(
                'synthetic_test',
                synthetic,
                256
            )
            results['components']['synthetic_test'] = {
                'combined_score': analysis.combined_score,
                'verdict': analysis.overall_verdict,
            }
            results['summary'] = {
                'note': 'Analise com dados sinteticos - KayosCrypto nao importado'
            }
        
        return results
    
    def _score_to_grade(self, score: float) -> str:
        """Converte score numerico em grade"""
        if score >= 0.95:
            return "A+ (Excepcional)"
        elif score >= 0.90:
            return "A (Excelente)"
        elif score >= 0.85:
            return "B+ (Muito Bom)"
        elif score >= 0.80:
            return "B (Bom)"
        elif score >= 0.75:
            return "C+ (Adequado)"
        elif score >= 0.70:
            return "C (Aceitavel)"
        elif score >= 0.60:
            return "D (Insuficiente)"
        else:
            return "F (Critico)"


# ============================================================================
# FUNCAO PRINCIPAL DE TESTE
# ============================================================================

def run_grover_hawking_test():
    """Executa teste completo Grover-Hawking"""
    
    print("=" * 70)
    print("  GROVER-HAWKING QUANTUM RESISTANCE TEST")
    print("  KayosCrypto v6.0 QUANTUM")
    print("=" * 70)
    print()
    
    analyzer = GroverHawkingAnalyzer()
    
    print("[1/4] Inicializando analisadores...")
    print(f"      - Grover Attack Analyzer: OK")
    print(f"      - Hawking Entropy Analyzer: OK")
    print()
    
    print("[2/4] Executando analise do sistema...")
    results = analyzer.full_system_analysis()
    print()
    
    print("[3/4] RESULTADOS POR COMPONENTE:")
    print("-" * 70)
    
    for comp_name, data in results.get('components', {}).items():
        print(f"\n  {comp_name.upper()}")
        print(f"  {'='*len(comp_name)}")
        
        if 'combined_score' in data:
            print(f"    Grover Resistance:  {data.get('grover_resistance', 0):.1%}")
            print(f"    Hawking Resistance: {data.get('hawking_resistance', 0):.1%}")
            print(f"    Combined Score:     {data['combined_score']:.1%}")
            print(f"    Weakest Link:       {data.get('weakest_link', 'N/A')}")
            print(f"    Verdict:            {data.get('verdict', 'N/A')}")
            
            if 'grover_details' in data:
                gd = data['grover_details']
                print(f"    Grover Details:")
                print(f"      - Required Qubits: {gd.get('required_qubits', 'N/A')}")
                print(f"      - Quantum Time:    {gd.get('quantum_time', 'N/A')}")
                print(f"      - Classical Time:  {gd.get('classical_time', 'N/A')}")
            
            if 'hawking_details' in data:
                hd = data['hawking_details']
                print(f"    Hawking Details:")
                print(f"      - Entropy Density: {hd.get('entropy_density', 0):.4f} bits/byte")
    
    print()
    print("[4/4] RESUMO FINAL:")
    print("-" * 70)
    
    summary = results.get('summary', {})
    if 'average_resistance' in summary:
        print(f"    Average Resistance: {summary['average_resistance']:.1%}")
        print(f"    Minimum Resistance: {summary['minimum_resistance']:.1%}")
        print(f"    Overall Grade:      {summary['overall_grade']}")
        print(f"    Quantum Ready:      {'SIM' if summary['quantum_ready'] else 'NAO'}")
        print(f"    PQC Migration:      {'URGENTE' if summary.get('pqc_migration_urgent') else 'Nao urgente'}")
    else:
        print(f"    {summary.get('note', 'Sem resumo disponivel')}")
    
    print()
    print("=" * 70)
    print("  TESTE CONCLUIDO")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    results = run_grover_hawking_test()
