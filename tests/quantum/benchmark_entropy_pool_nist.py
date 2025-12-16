#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Benchmark do GeometricEntropyPool contra NIST SP 800-22

Este script executa o validador NIST contra múltiplas amostras de dados
gerados pelo GeometricEntropyPool, fornecendo uma avaliação empírica
da qualidade da entropia.

Objetivo: Obter um benchmark inicial para identificar pontos fracos
antes de otimizações.
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from core.quantum.geometric_entropy_pool import GeometricEntropyPool
from nist_sp800_22_validator import NIST_SP800_22_Validator


def run_entropy_pool_benchmark(num_samples: int = 10, data_size: int = 128) -> dict:
    """
    Executa o benchmark do GeometricEntropyPool contra NIST.

    Args:
        num_samples (int): Número de amostras para testar.
        data_size (int): Tamanho de cada amostra em bytes.

    Retorna:
        dict: Resultados agregados dos testes.
    """
    print("=" * 70)
    print("BENCHMARK: GeometricEntropyPool contra NIST SP 800-22")
    print("=" * 70)
    print(f"Configuração:")
    print(f"  - Pool: GeometricEntropyPool (Rib 5)")
    print(f"  - Amostras: {num_samples}")
    print(f"  - Tamanho por amostra: {data_size} bytes ({data_size * 8} bits)")
    print(f"  - Alpha (significância): 0.01")
    print("=" * 70)

    pool = GeometricEntropyPool()
    results: dict[str, dict] = {'total_samples': num_samples}

    for i in range(num_samples):
        # Gerar dados do pool
        data = pool.generate_quantum_safe_key(data_size)

        # Validar com NIST
        validator = NIST_SP800_22_Validator(data, alpha=0.01)
        test_results = validator.run_all_tests()

        # Agregar resultados
        for test_name, test_result in test_results.items():
            if test_name not in results:
                results[test_name] = {'passed': 0, 'failed': 0, 'p_values': []}
            results[test_name]['p_values'].append(test_result['p_value'])
            if test_result['passed']:
                results[test_name]['passed'] += 1
            else:
                results[test_name]['failed'] += 1

        # Exibir progresso
        print(f"[{i+1}/{num_samples}] Amostra processada")

    print("\n" + "=" * 70)
    print("RESULTADOS DO BENCHMARK")
    print("=" * 70)

    test_names = [name for name in results.keys() if name != 'total_samples']

    for test_name in test_names:
        test_data = results[test_name]
        pass_rate = (test_data['passed'] / num_samples) * 100
        avg_p_value = sum(test_data['p_values']) / len(test_data['p_values']) if test_data['p_values'] else 0.0
        min_p_value = min(test_data['p_values']) if test_data['p_values'] else 0.0
        max_p_value = max(test_data['p_values']) if test_data['p_values'] else 0.0

        print(f"\n{test_name.upper().replace('_', ' ')}")
        print(f"  - Taxa de Sucesso: {pass_rate:.1f}% ({test_data['passed']}/{num_samples})")
        print(f"  - Média p-value: {avg_p_value:.6f}")
        print(f"  - Min p-value: {min_p_value:.6f}")
        print(f"  - Max p-value: {max_p_value:.6f}")

    print("\n" + "=" * 70)
    
    # Calcular score geral
    if test_names:
        overall_pass_rate = sum((results[name]['passed'] / num_samples) for name in test_names) / len(test_names)
    else:
        overall_pass_rate = 0.0
    
    print(f"SCORE GERAL")
    print(f"  - Taxa de Sucesso Agregada: {overall_pass_rate * 100:.1f}%")
    print("=" * 70)

    # Diagnóstico
    print(f"\nDIAGNÓSTICO:")
    if overall_pass_rate >= 0.95:
        print("   EXCELENTE: Pool passou em >95% dos testes NIST")
    elif overall_pass_rate >= 0.80:
        print("    ACEITÁVEL: Pool passou em 80-95% dos testes NIST (otimização recomendada)")
    elif overall_pass_rate >= 0.50:
        print("   FRACO: Pool passou em <80% dos testes NIST (refatoração necessária)")
    else:
        print("   CRÍTICO: Pool falhou na maioria dos testes NIST (redesenho urgente)")

    return results


if __name__ == '__main__':
    # Executar benchmark
    run_entropy_pool_benchmark(num_samples=10, data_size=128)
