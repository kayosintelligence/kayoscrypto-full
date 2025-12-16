#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NIST SP 800-22 Statistical Test Suite (Implementação Parcial Expandida)

Este módulo fornece uma implementação parcial do conjunto de testes estatísticos
do NIST para geradores de números aleatórios, conforme descrito na publicação
especial 800-22.

Testes atualmente implementados:
1. Teste de Frequência (Monobit)
2. Teste de Runs
3. Teste de Frequência por Blocos
4. Teste de Maior Sequência de Uns em um Bloco

Referência: https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-22r1a.pdf
"""

import math
from typing import Sequence
from scipy.special import erfc, gammaincc

class NIST_SP800_22_Validator:
    """
    Validador que implementa um subconjunto dos testes estatísticos do NIST.
    """

    def __init__(self, data: bytes, alpha: float = 0.01):
        """
        Inicializa o validador com os dados a serem testados.

        Args:
            data (bytes): A sequência de bytes a ser testada.
            alpha (float): O nível de significância para os testes (padrão: 0.01).
        """
        self.bit_sequence = self._bytes_to_bit_array(data)
        self.n = len(self.bit_sequence)
        self.alpha = alpha
        self.results = {}

    @staticmethod
    def _bytes_to_bit_array(data: bytes) -> list[int]:
        """Converte uma sequência de bytes em uma lista de bits (0s e 1s)."""
        bit_array = []
        for byte in data:
            for i in range(8):
                bit_array.append((byte >> (7 - i)) & 1)
        return bit_array

    def run_all_tests(self) -> dict:
        """
        Executa todos os testes implementados e retorna os resultados.
        """
        self.frequency_monobit_test()
        self.runs_test()
        self.block_frequency_test()
        self.longest_run_of_ones_test()
        return self.results

    def frequency_monobit_test(self) -> tuple[float, bool]:
        """
        Teste 1: Teste de Frequência (Monobit)

        O foco deste teste é determinar se o número de 0s e 1s na sequência
        é aproximadamente o mesmo, como seria esperado para uma sequência
        verdadeiramente aleatória.

        Retorna:
            tuple[float, bool]: O valor-p e se o teste passou.
        """
        if self.n < 100:
            # NIST recomenda n >= 100
            return 0.0, False

        # Mapear 0s para -1 e 1s para +1
        s_n = [2 * b - 1 for b in self.bit_sequence]
        
        # Soma absoluta
        s_obs = abs(sum(s_n))
        
        # Estatística de teste
        test_statistic = s_obs / math.sqrt(self.n)
        
        # Valor-p
        p_value = erfc(test_statistic / math.sqrt(2))
        
        passed = p_value >= self.alpha
        
        self.results['frequency_monobit'] = {
            'p_value': p_value,
            'passed': passed,
            'details': f'n={self.n}, S_obs={s_obs:.2f}, statistic={test_statistic:.4f}'
        }
        return p_value, passed

    def runs_test(self) -> tuple[float, bool]:
        """
        Teste 2: Teste de Runs

        O foco deste teste é determinar se o número total de "runs" (sequências
        ininterruptas de bits idênticos) é o esperado para uma sequência aleatória.
        Um número excessivo ou insuficiente de runs indica que a amostra pode
        não ser aleatória.

        Retorna:
            tuple[float, bool]: O valor-p e se o teste passou.
        """
        if self.n < 100:
            return 0.0, False

        # Proporção de 1s
        pi = self.bit_sequence.count(1) / self.n
        
        # Condição pré-teste: a proporção deve estar dentro de um intervalo
        tau = 2 / math.sqrt(self.n)
        if abs(pi - 0.5) >= tau:
            self.results['runs'] = {
                'p_value': 0.0,
                'passed': False,
                'details': f'Pre-test failed: |pi - 0.5| = {abs(pi - 0.5):.4f} >= {tau:.4f}'
            }
            return 0.0, False

        # Contar o número de runs (V_n)
        v_n = 1
        for i in range(self.n - 1):
            if self.bit_sequence[i] != self.bit_sequence[i+1]:
                v_n += 1
        
        # Valor-p
        numerator = abs(v_n - 2 * self.n * pi * (1 - pi))
        denominator = 2 * math.sqrt(2 * self.n) * pi * (1 - pi)
        p_value = erfc(numerator / denominator)
        
        passed = p_value >= self.alpha
        
        self.results['runs'] = {
            'p_value': p_value,
            'passed': passed,
            'details': f'n={self.n}, pi={pi:.4f}, V_n={v_n}'
        }
        return p_value, passed

    def block_frequency_test(self, block_size: int = 128) -> tuple[float, bool]:
        """Teste 3: Frequência por Blocos."""
        if self.n < block_size:
            self.results['block_frequency'] = {
                'p_value': 0.0,
                'passed': False,
                'details': f'n={self.n} insuficiente para block_size={block_size}'
            }
            return 0.0, False

        num_blocks = self.n // block_size
        if num_blocks == 0:
            self.results['block_frequency'] = {
                'p_value': 0.0,
                'passed': False,
                'details': 'Número de blocos é zero'
            }
            return 0.0, False

        chi_squared = 0.0
        for block_index in range(num_blocks):
            start = block_index * block_size
            end = start + block_size
            block = self.bit_sequence[start:end]
            pi = sum(block) / block_size
            chi_squared += (pi - 0.5) ** 2

        chi_squared *= 4.0 * block_size
        p_value = gammaincc(num_blocks / 2.0, chi_squared / 2.0)
        passed = p_value >= self.alpha
        self.results['block_frequency'] = {
            'p_value': p_value,
            'passed': passed,
            'details': f'n={self.n}, M={block_size}, N={num_blocks}, chi2={chi_squared:.4f}'
        }
        return p_value, passed

    def longest_run_of_ones_test(self) -> tuple[float, bool]:
        """Teste 4: Maior sequência de uns em blocos."""
        if self.n < 128:
            self.results['longest_run'] = {
                'p_value': 0.0,
                'passed': False,
                'details': f'n={self.n} insuficiente (mínimo 128)'
            }
            return 0.0, False

        if self.n < 6272:
            block_size = 8
            v_values = [1, 2, 3, 4]
            pi = [0.21484375, 0.3671875, 0.23046875, 0.1875]
        elif self.n < 750000:
            block_size = 128
            v_values = [4, 5, 6, 7, 8, 9]
            pi = [0.1174035788, 0.242955959, 0.249363483, 0.17517706, 0.102701071, 0.112398847]
        else:
            block_size = 10000
            v_values = [10, 11, 12, 13, 14, 15]
            pi = [0.0882, 0.2092, 0.2483, 0.1933, 0.1208, 0.1402]

        num_blocks = self.n // block_size
        if num_blocks == 0:
            self.results['longest_run'] = {
                'p_value': 0.0,
                'passed': False,
                'details': 'Número de blocos é zero'
            }
            return 0.0, False

        counts = [0] * len(pi)
        for block_index in range(num_blocks):
            start = block_index * block_size
            end = start + block_size
            block_bits = self.bit_sequence[start:end]
            longest_run = self._longest_run_of_ones(block_bits)
            category_index = self._categorize_longest_run(longest_run, v_values)
            counts[category_index] += 1

        chi_squared = 0.0
        for count, probability in zip(counts, pi):
            expected = probability * num_blocks
            chi_squared += ((count - expected) ** 2) / expected

        degrees_of_freedom = len(pi) - 1
        p_value = gammaincc(degrees_of_freedom / 2.0, chi_squared / 2.0)
        passed = p_value >= self.alpha
        self.results['longest_run'] = {
            'p_value': p_value,
            'passed': passed,
            'details': f'n={self.n}, M={block_size}, N={num_blocks}, chi2={chi_squared:.4f}, counts={counts}'
        }
        return p_value, passed

    @staticmethod
    def _longest_run_of_ones(block_bits: Sequence[int]) -> int:
        longest = 0
        current = 0
        for bit in block_bits:
            if bit == 1:
                current += 1
                if current > longest:
                    longest = current
            else:
                current = 0
        return longest

    @staticmethod
    def _categorize_longest_run(longest: int, v_values: Sequence[int]) -> int:
        if longest <= v_values[0]:
            return 0
        for index in range(1, len(v_values) - 1):
            if longest == v_values[index]:
                return index
        if longest >= v_values[-1]:
            return len(v_values) - 1
        return len(v_values) - 2

if __name__ == '__main__':
    # Exemplo de uso e teste rápido
    import os

    # Gerar dados pseudo-aleatórios para teste
    random_data = os.urandom(128) # 1024 bits
    validator = NIST_SP800_22_Validator(random_data)
    results = validator.run_all_tests()

    print("--- Resultados do Teste NIST SP 800-22 (Parcial) ---")
    for test_name, result in results.items():
        status = "PASSOU" if result['passed'] else "FALHOU"
        print(f"Teste: {test_name}")
        print(f"  - Status: {status}")
        print(f"  - Valor-p: {result['p_value']:.6f} (alpha = {validator.alpha})")
        print(f"  - Detalhes: {result['details']}")
        print("-" * 20)

    # Teste com dados não aleatórios (deve falhar)
    print("\n--- Testando com dados não aleatórios (deve falhar) ---")
    non_random_data = b'\x0f\x0f\x0f\x0f' * 32 # Padrão 00001111 repetido
    validator_fail = NIST_SP800_22_Validator(non_random_data)
    results_fail = validator_fail.run_all_tests()
    
    for test_name, result in results_fail.items():
        status = "PASSOU" if result['passed'] else "FALHOU"
        print(f"Teste: {test_name}")
        print(f"  - Status: {status}")
        print(f"  - Valor-p: {result['p_value']:.6f} (alpha = {validator_fail.alpha})")
        print(f"  - Detalhes: {result['details']}")
        print("-" * 20)
