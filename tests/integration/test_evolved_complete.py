#!/usr/bin/env python3
"""
 TESTE COMPLETO - KAYOSCRYPTO EVOLVED
========================================

Testa todas as evoluções juntas:
- Rodas Concêntricas de Ezequiel
- Direcionamento Fibonacci (Verso/Anverso)
- Compatibilidade com sistema original
- Reversibilidade total
- Avalanche effect
"""

import os
from ezekiel_concentric import KayosCryptoEvolved
from fibonacci_direction import KayosCryptoWithDirection

def _run_reversibility_comprehensive() -> bool:
    """Executa o cenário completo de reversibilidade e retorna o status."""

    print("\n TESTE REVERSIBILIDADE ABRANGENTE")
    print("=" * 70)
    
    # Sistemas a testar
    systems = [
        ("KayosCrypto Evolved (Concentric)", KayosCryptoEvolved(use_concentric=True)),
        ("KayosCrypto with Direction", KayosCryptoWithDirection(use_direction=True)),
    ]
    
    # Dados de teste variados
    test_cases = [
        (b"Hello World! 123", "simple"),
        (b"A" * 100, "repetitive"),
        (os.urandom(256), "random"),
        (b"The quick brown fox jumps over the lazy dog " * 5, "text"),
    ]
    
    password = os.getenv("KAYOS_AUTH_PASSWORD", "default_insecure_password")
    all_passed = True
    
    for system_name, crypto in systems:
        print(f"\n Sistema: {system_name}")
        print("-" * 70)
        
        for test_data, test_type in test_cases:
            # Encrypt
            encrypted = crypto.encrypt(test_data, password)
            
            # Decrypt
            decrypted = crypto.decrypt(encrypted, password)
            
            # Verificar
            if decrypted == test_data:
                status = " PASSOU"
            else:
                status = " FALHOU"
                all_passed = False
            
            print(f"   {test_type:12s} ({len(test_data):3d} bytes): {status}")
    
    print("\n" + "=" * 70)
    if all_passed:
        print(" RESULTADO: TODOS OS TESTES PASSARAM!")
    else:
        print("  RESULTADO: ALGUNS TESTES FALHARAM")

    return all_passed


def test_reversibility_comprehensive():
    """Teste abrangente de reversibilidade."""
    all_passed = _run_reversibility_comprehensive()
    assert all_passed, "Reversibilidade falhou para pelo menos um cenário evolutivo"


def _run_avalanche_comparison():
    """Executa a comparação de avalanche e retorna a lista de resultados."""

    print("\n COMPARAÇÃO DE AVALANCHE EFFECT")
    print("=" * 70)
    
    from kayoscrypto_final import KayosCryptoFinal
    
    systems = [
        ("Original (v3.0)", KayosCryptoFinal()),
        ("Evolved Concentric", KayosCryptoEvolved(use_concentric=True)),
        ("With Direction", KayosCryptoWithDirection(use_direction=True)),
    ]
    
    password = os.getenv("KAYOS_AUTH_PASSWORD", "default_insecure_password")
    
    # Dados de teste
    original = bytearray(200)
    for i in range(200):
        original[i] = (i * 13) % 256
    
    modified = bytearray(original)
    modified[100] ^= 0x01  # 1 bit diferente no meio
    
    results = []
    
    for system_name, crypto in systems:
        enc_orig = crypto.encrypt(bytes(original), password)
        enc_mod = crypto.encrypt(bytes(modified), password)
        
        diff_bits = sum(bin(a ^ b).count('1') for a, b in zip(enc_orig, enc_mod))
        total_bits = len(enc_orig) * 8
        avalanche = (diff_bits / total_bits) * 100
        
        results.append((system_name, avalanche))
        
        # Status
        if avalanche >= 45:
            status = " EXCELENTE"
        elif avalanche >= 35:
            status = " BOM"
        elif avalanche >= 25:
            status = "  ACEITAVEL"
        else:
            status = " BAIXO"
        
        print(f"{system_name:20s}: {avalanche:5.2f}% {status}")
    
    # Encontrar melhor
    best = max(results, key=lambda x: x[1])
    print("\n" + "=" * 70)
    print(f" MELHOR AVALANCHE: {best[0]} ({best[1]:.2f}%)")

    return results


def test_avalanche_comparison():
    """Compara avalanche entre sistemas."""
    results = _run_avalanche_comparison()
    assert results, "Nenhum resultado de avalanche foi calculado"
    assert all(avalanche >= 25.0 for _, avalanche in results), "Avalanche inferior a 25% detectada em algum sistema"


def test_performance_comparison():
    """Compara performance entre sistemas."""
    
    print("\n COMPARAÇÃO DE PERFORMANCE")
    print("=" * 70)
    
    import time
    from kayoscrypto_final import KayosCryptoFinal
    
    systems = [
        ("Original (v3.0)", KayosCryptoFinal()),
        ("Evolved Concentric", KayosCryptoEvolved(use_concentric=True)),
        ("With Direction", KayosCryptoWithDirection(use_direction=True)),
    ]
    
    password = os.getenv("KAYOS_AUTH_PASSWORD", "default_insecure_password")
    test_data = os.urandom(10000)  # 10 KB
    iterations = 50
    
    for system_name, crypto in systems:
        # Encrypt
        start = time.time()
        for _ in range(iterations):
            encrypted = crypto.encrypt(test_data, password)
        encrypt_time = time.time() - start
        
        # Decrypt
        start = time.time()
        for _ in range(iterations):
            decrypted = crypto.decrypt(encrypted, password)
        decrypt_time = time.time() - start
        
        # Cálculos
        total_bytes = len(test_data) * iterations
        encrypt_speed = total_bytes / encrypt_time / 1024  # KB/s
        decrypt_speed = total_bytes / decrypt_time / 1024  # KB/s
        
        print(f"\n{system_name}:")
        print(f"   Encrypt: {encrypt_speed:6.2f} KB/s ({encrypt_time:.3f}s)")
        print(f"   Decrypt: {decrypt_speed:6.2f} KB/s ({decrypt_time:.3f}s)")


def generate_evolution_report():
    """Gera relatório final da evolução."""
    
    print("\n" + "=" * 70)
    print(" RELATÓRIO FINAL - KAYOSCRYPTO EVOLVED")
    print("=" * 70)
    
    # Executar todos os testes
    reversibility_ok = _run_reversibility_comprehensive()
    avalanche_results = _run_avalanche_comparison()
    test_performance_comparison()
    
    # Resumo
    print("\n" + "=" * 70)
    print(" RESUMO EXECUTIVO:")
    print("=" * 70)
    
    print(f" Reversibilidade: {'PERFEITA' if reversibility_ok else 'PROBLEMAS'}")
    
    # Melhor avalanche
    best_avalanche = max(avalanche_results, key=lambda x: x[1])
    print(f" Melhor Avalanche: {best_avalanche[0]} ({best_avalanche[1]:.2f}%)")
    
    # Recomendação
    print("\n RECOMENDAÇÃO:")
    if reversibility_ok and best_avalanche[1] >= 45:
        print("    Sistema pronto para uso!")
        print("    Evolução bem-sucedida")
        print("    Todas as features funcionando corretamente")
    elif reversibility_ok and best_avalanche[1] >= 35:
        print("     Sistema funcional mas pode melhorar")
        print("    Reversibilidade perfeita")
        print("     Avalanche pode ser otimizado")
    else:
        print("    Sistema requer ajustes")
        print("    Verificar problemas identificados acima")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    print("\n KAYOSCRYPTO EVOLVED - SUITE DE TESTES COMPLETA")
    print("=" * 70)
    print("Testando todas as evoluções...")
    print()
    
    generate_evolution_report()
