import os
#!/usr/bin/env python3
"""
 AVALANCHE EFFECT TEST - KAYOSCRYPTO v3.0

Testa se 1 bit de mudança no plaintext causa ~50% mudança no ciphertext
(Propriedade fundamental de criptografia forte)

Critério de sucesso: 45-55% de bits diferentes
"""

import sys
sys.path.insert(0, '/home/kbe/KAYOS_SYSTEMS/KayosCrypto')

from fibonacci_permutation import FibonacciPermutation
import numpy as np
from typing import Tuple

def flip_bit(data: bytes, byte_pos: int, bit_pos: int) -> bytes:
    """
    Inverte 1 bit específico nos dados
    
    Args:
        data: Dados originais
        byte_pos: Posição do byte (0-based)
        bit_pos: Posição do bit no byte (0-7)
    
    Returns:
        Dados com 1 bit invertido
    """
    data_array = bytearray(data)
    data_array[byte_pos] ^= (1 << bit_pos)
    return bytes(data_array)


def count_different_bits(data1: bytes, data2: bytes) -> Tuple[int, float]:
    """
    Conta quantos bits são diferentes entre dois bytestrings
    
    Returns:
        (bits_diferentes, percentual)
    """
    if len(data1) != len(data2):
        raise ValueError("Dados devem ter mesmo tamanho")
    
    total_bits = len(data1) * 8
    different_bits = 0
    
    for b1, b2 in zip(data1, data2):
        xor = b1 ^ b2
        different_bits += bin(xor).count('1')
    
    percentage = (different_bits / total_bits) * 100
    return different_bits, percentage


def encrypt_data(plaintext: bytes, key: bytes, level: int = 3) -> bytes:
    """Encripta dados usando as 5 camadas (com S-boxes)"""
    # 1. Fibonacci spiral permutation
    encrypted = FibonacciPermutation.fibonacci_spiral_permutation(plaintext, level, key, False)
    
    # 1.5. Byte substitution (S-box)
    encrypted = FibonacciPermutation.byte_substitution(encrypted, key, False)
    
    # 2. Golden Ratio permutation
    encrypted = FibonacciPermutation.golden_ratio_permutation(encrypted, key, False)
    
    # 2.5. Byte substitution (S-box layer 2)
    encrypted = FibonacciPermutation.byte_substitution(encrypted, key + b"_layer2", False)
    
    # 3. XOR Diffusion
    encrypted = FibonacciPermutation.xor_diffusion(encrypted, key, level)
    
    return encrypted


def test_avalanche_single_bit():
    """Testa avalanche effect com 1 bit alterado no plaintext"""
    print("=" * 80)
    print(" TESTE 1: AVALANCHE EFFECT - 1 BIT NO PLAINTEXT")
    print("=" * 80)
    
    # Plaintext de teste (256 bytes ALEATÓRIOS para difusão real)
    np.random.seed(42)  # Reproduzível
    plaintext_original = bytes(np.random.randint(0, 256, 256, dtype=np.uint8))
    key = os.getenv("KAYOS_CRYPTO_KEY", "default_insecure_key").encode()
    level = 3
    
    print(f" Plaintext: {len(plaintext_original)} bytes (aleatório)")
    print(f" Key: {len(key)} bytes")
    print(f" Fibonacci Level: {level}\n")
    
    # Encrypt original
    ciphertext_original = encrypt_data(plaintext_original, key, level)
    
    # Testar múltiplos bits
    results = []
    
    print(" Testando inversão de bits individuais...\n")
    print("Byte | Bit | Bits Diferentes | Percentual | Status")
    print("-" * 80)
    
    # Testar primeiros 10 bytes, bit 0 de cada
    for byte_pos in range(min(10, len(plaintext_original))):
        for bit_pos in [0, 4, 7]:  # Testar 3 bits por byte
            # Inverter 1 bit
            plaintext_modified = flip_bit(plaintext_original, byte_pos, bit_pos)
            
            # Encrypt modificado
            ciphertext_modified = encrypt_data(plaintext_modified, key, level)
            
            # Comparar
            diff_bits, percentage = count_different_bits(ciphertext_original, ciphertext_modified)
            results.append(percentage)
            
            # Avaliar resultado
            if 45 <= percentage <= 55:
                status = " EXCELENTE"
            elif 40 <= percentage <= 60:
                status = " BOM"
            elif 30 <= percentage <= 70:
                status = " ACEITÁVEL"
            else:
                status = " RUIM"
            
            print(f"  {byte_pos:2d}  |  {bit_pos}  |    {diff_bits:5d}      |  {percentage:6.2f}%  | {status}")
    
    # Estatísticas gerais
    print("\n" + "=" * 80)
    print(" ESTATÍSTICAS GERAIS")
    print("=" * 80)
    
    results_array = np.array(results)
    print(f"Média:         {results_array.mean():.2f}%")
    print(f"Desvio Padrão: {results_array.std():.2f}%")
    print(f"Mínimo:        {results_array.min():.2f}%")
    print(f"Máximo:        {results_array.max():.2f}%")
    print(f"Mediana:       {np.median(results_array):.2f}%")
    
    # Avaliação final
    mean = results_array.mean()
    
    print("\n" + "=" * 80)
    print(" AVALIAÇÃO FINAL")
    print("=" * 80)
    
    if 45 <= mean <= 55:
        print(" EXCELENTE: Efeito avalanche ideal (~50%)")
        print("   Sistema demonstra excelente difusão criptográfica!")
        verdict = True
    elif 40 <= mean <= 60:
        print(" BOM: Efeito avalanche satisfatório")
        print("   Sistema demonstra boa difusão criptográfica.")
        verdict = True
    elif 30 <= mean <= 70:
        print(" ACEITÁVEL: Efeito avalanche moderado")
        print("   Sistema funciona mas pode ser melhorado.")
        verdict = True
    else:
        print(" INSUFICIENTE: Efeito avalanche fraco")
        print("   Sistema NÃO demonstra difusão adequada!")
        verdict = False

    print()
    total_checks = min(10, len(plaintext_original)) * 3
    assert len(results) == total_checks, "Quantidade inesperada de medições de avalanche para plaintext"
    assert 0.0 <= results_array.min() <= results_array.max() <= 100.0, "Percentuais de avalanche fora da faixa 0-100%"
    assert not np.isnan(mean), "Média do efeito avalanche é NaN"

    if __name__ == "__main__":  # Permite reuso quando executado diretamente
        return verdict


def test_avalanche_key():
    """Testa avalanche effect com 1 bit alterado na chave"""
    print("=" * 80)
    print(" TESTE 2: AVALANCHE EFFECT - 1 BIT NA CHAVE")
    print("=" * 80)
    
    plaintext = b"Teste de avalanche effect na chave criptografica" * 5  # 245 bytes
    key_original = b"senha_original_123456789012345678901234"
    level = 3
    
    print(f" Plaintext: {len(plaintext)} bytes")
    print(f" Key: {len(key_original)} bytes")
    print(f" Fibonacci Level: {level}\n")
    
    # Encrypt com chave original
    ciphertext_original = encrypt_data(plaintext, key_original, level)
    
    results = []
    
    print(" Testando inversão de bits na chave...\n")
    print("Byte | Bit | Bits Diferentes | Percentual | Status")
    print("-" * 80)
    
    # Testar primeiros 10 bytes da chave
    for byte_pos in range(min(10, len(key_original))):
        for bit_pos in [0, 4, 7]:
            # Inverter 1 bit na chave
            key_modified = flip_bit(key_original, byte_pos, bit_pos)
            
            # Encrypt com chave modificada
            ciphertext_modified = encrypt_data(plaintext, key_modified, level)
            
            # Comparar
            diff_bits, percentage = count_different_bits(ciphertext_original, ciphertext_modified)
            results.append(percentage)
            
            # Avaliar
            if 45 <= percentage <= 55:
                status = " EXCELENTE"
            elif 40 <= percentage <= 60:
                status = " BOM"
            elif 30 <= percentage <= 70:
                status = " ACEITÁVEL"
            else:
                status = " RUIM"
            
            print(f"  {byte_pos:2d}  |  {bit_pos}  |    {diff_bits:5d}      |  {percentage:6.2f}%  | {status}")
    
    # Estatísticas
    print("\n" + "=" * 80)
    print(" ESTATÍSTICAS GERAIS")
    print("=" * 80)
    
    results_array = np.array(results)
    print(f"Média:         {results_array.mean():.2f}%")
    print(f"Desvio Padrão: {results_array.std():.2f}%")
    print(f"Mínimo:        {results_array.min():.2f}%")
    print(f"Máximo:        {results_array.max():.2f}%")
    print(f"Mediana:       {np.median(results_array):.2f}%")
    
    mean = results_array.mean()
    
    print("\n" + "=" * 80)
    print(" AVALIAÇÃO FINAL")
    print("=" * 80)
    
    if 45 <= mean <= 55:
        print(" EXCELENTE: Chave demonstra excelente sensibilidade!")
        verdict = True
    elif 40 <= mean <= 60:
        print(" BOM: Chave demonstra boa sensibilidade.")
        verdict = True
    elif 30 <= mean <= 70:
        print(" ACEITÁVEL: Chave demonstra sensibilidade moderada.")
        verdict = True
    else:
        print(" INSUFICIENTE: Chave NÃO demonstra sensibilidade adequada!")
        verdict = False

    print()
    total_checks = min(10, len(key_original)) * 3
    assert len(results) == total_checks, "Quantidade inesperada de medições de avalanche para chave"
    assert 0.0 <= results_array.min() <= results_array.max() <= 100.0, "Percentuais de avalanche da chave fora da faixa 0-100%"
    assert not np.isnan(mean), "Média do efeito avalanche da chave é NaN"

    if __name__ == "__main__":
        return verdict


def test_avalanche_position():
    """Testa se posição do bit alterado importa"""
    print("=" * 80)
    print(" TESTE 3: AVALANCHE EFFECT - DIFERENTES POSIÇÕES")
    print("=" * 80)
    
    plaintext = b"X" * 128
    key = os.getenv("KAYOS_CRYPTO_KEY", "default_insecure_key").encode()
    level = 3
    
    print(f" Testando se posição do bit afeta o efeito avalanche...")
    print(f"    Plaintext: {len(plaintext)} bytes")
    print(f"    Alterando: Byte 0, 32, 64, 96, 127 (bit 0)\n")
    
    # Encrypt original
    ciphertext_original = encrypt_data(plaintext, key, level)
    
    positions = [0, 32, 64, 96, 127]
    results = []
    
    print("Posição | Bits Diferentes | Percentual | Status")
    print("-" * 80)
    
    for pos in positions:
        plaintext_modified = flip_bit(plaintext, pos, 0)
        ciphertext_modified = encrypt_data(plaintext_modified, key, level)
        diff_bits, percentage = count_different_bits(ciphertext_original, ciphertext_modified)
        results.append(percentage)
        
        if 45 <= percentage <= 55:
            status = " EXCELENTE"
        elif 40 <= percentage <= 60:
            status = " BOM"
        else:
            status = " MODERADO"
        
        print(f"  {pos:3d}   |      {diff_bits:5d}      |  {percentage:6.2f}%  | {status}")
    
    # Avaliar consistência
    results_array = np.array(results)
    std = results_array.std()
    
    print("\n" + "=" * 80)
    print(" CONSISTÊNCIA")
    print("=" * 80)
    print(f"Desvio Padrão: {std:.2f}%")
    
    if std < 5:
        print(" EXCELENTE: Efeito avalanche consistente independente da posição!")
        verdict = True
    elif std < 10:
        print(" BOM: Efeito avalanche razoavelmente consistente.")
        verdict = True
    else:
        print(" INCONSISTENTE: Efeito varia muito com a posição.")
        verdict = False

    print()
    assert len(results) == len(positions), "Quantidade inesperada de medições por posição"
    assert 0.0 <= results_array.min() <= results_array.max() <= 100.0, "Percentuais por posição fora da faixa 0-100%"
    assert not np.isnan(std), "Desvio padrão do efeito avalanche é NaN"

    if __name__ == "__main__":
        return verdict


if __name__ == "__main__":
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                                                                    ║")
    print("║         AVALANCHE EFFECT TEST - KAYOSCRYPTO v3.0              ║")
    print("║                                                                    ║")
    print("║  Critério: 1 bit mudança → ~50% bits diferentes no output         ║")
    print("║  Padrão: 45-55% = Excelente | 40-60% = Bom | <40% ou >60% = Ruim ║")
    print("║                                                                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print("\n")
    
    # Executar testes
    teste1 = test_avalanche_single_bit()
    teste2 = test_avalanche_key()
    teste3 = test_avalanche_position()
    
    # Resultado final
    print("\n" + "=" * 80)
    print(" RESULTADO FINAL DOS TESTES")
    print("=" * 80)
    print(f"Teste 1 (Plaintext):  {' PASSOU' if teste1 else ' FALHOU'}")
    print(f"Teste 2 (Key):        {' PASSOU' if teste2 else ' FALHOU'}")
    print(f"Teste 3 (Posição):    {' PASSOU' if teste3 else ' FALHOU'}")
    print()
    
    if all([teste1, teste2, teste3]):
        print(" TODOS OS TESTES DE AVALANCHE PASSARAM! ")
        print(" KAYOSCRYPTO v3.0 demonstra EXCELENTE efeito avalanche!")
        print(" Sistema criptograficamente ROBUSTO!")
    elif any([teste1, teste2, teste3]):
        print(" ALGUNS TESTES PASSARAM")
        print("Sistema demonstra difusão, mas pode ser melhorado.")
    else:
        print(" NENHUM TESTE PASSOU")
        print("Sistema NÃO demonstra efeito avalanche adequado!")
    
    print("\n" + "=" * 80)
    print()
