#!/usr/bin/env python3
"""
 TESTES REAIS DE SEGURANÇA - Sem Falsos Positivos
"""

import os
import sys
import time
import statistics

# Adicionar path para módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from src.core.kayoscrypto_ultimate import KayosCryptoUltimate

class RealSecurityTests:
    """Testes que validam comportamentos REAIS do sistema"""
    
    def test_deterministic_encryption(self):
        """ TESTE REAL: Mesma entrada + mesma chave = mesma saída"""
        print("\n TESTE 1: Determinismo Criptográfico")
        crypto = KayosCryptoUltimate()
        
        test_data = b"Teste de dados deterministicos para validacao"
        password = os.getenv("KAYOS_AUTH_PASSWORD", "default_insecure_password")
        
        # Executar múltiplas vezes
        results = []
        for i in range(10):
            encrypted = crypto.encrypt(test_data, password)
            results.append(encrypted)
        
        # VERIFICAÇÃO REAL: Todos devem ser IDÊNTICOS
        all_identical = all(r == results[0] for r in results)
        
        if all_identical:
            print("    PASSOU: Encrypt é determinístico")
            return True
        else:
            print("    FALHOU: Encrypt não é determinístico")
            return False
    
    def test_avalanche_effect_real(self):
        """ TESTE REAL: 1 bit muda → ~50% da saída muda"""
        print("\n TESTE 2: Efeito Avalanche Real")
        crypto = KayosCryptoUltimate()
        
        # Criar dados estruturados (não aleatórios)
        original = bytes([i % 256 for i in range(512)])  # Padrão previsível
        
        # Modificar 1 bit específico
        modified = bytearray(original)
        bit_pos = 137  # Posição arbitrária
        modified[bit_pos // 8] ^= (1 << (bit_pos % 8))
        
        password = os.getenv("KAYOS_AUTH_PASSWORD", "default_insecure_password")
        
        # Criptografar ambos
        enc_original = crypto.encrypt(original, password)
        enc_modified = crypto.encrypt(bytes(modified), password)
        
        # Calcular diferenças REAIS
        diff_bits = 0
        diff_bytes = 0
        
        for i, (b1, b2) in enumerate(zip(enc_original, enc_modified)):
            if b1 != b2:
                diff_bytes += 1
            diff_bits += bin(b1 ^ b2).count('1')
        
        total_bits = len(enc_original) * 8
        avalanche_percent = (diff_bits / total_bits) * 100
        byte_diff_percent = (diff_bytes / len(enc_original)) * 100
        
        print(f"   Bits diferentes: {diff_bits}/{total_bits} ({avalanche_percent:.2f}%)")
        print(f"   Bytes diferentes: {diff_bytes}/{len(enc_original)} ({byte_diff_percent:.2f}%)")
        
        # CRITÉRIO REAL: Pelo menos 35% dos bits devem mudar
        if avalanche_percent > 35.0:
            print("    PASSOU: Bom efeito avalanche")
            return True
        else:
            print(f"    FALHOU: Avalanche muito baixo ({avalanche_percent:.2f}%)")
            return False
    
    def test_reversibility_large_files(self):
        """ TESTE REAL: Arquivos grandes são recuperados perfeitamente"""
        print("\n TESTE 3: Reversibilidade com Dados Grandes")
        crypto = KayosCryptoUltimate()
        
        # Criar arquivo de 1MB com padrão conhecido
        large_data = bytes([(i * 7 + i // 13) % 256 for i in range(1024 * 1024)])
        
        password = os.getenv("KAYOS_AUTH_PASSWORD", "default_insecure_password")
        
        # Medir tempo real
        start_time = time.time()
        encrypted = crypto.encrypt(large_data, password)
        encrypt_time = time.time() - start_time
        
        start_time = time.time()
        decrypted = crypto.decrypt(encrypted, password)
        decrypt_time = time.time() - start_time
        
        # VERIFICAÇÃO REAL: Dados devem ser IDÊNTICOS byte-a-byte
        identical = large_data == decrypted
        speed = len(large_data) / encrypt_time / 1024 / 1024  # MB/s
        
        print(f"   Tamanho: {len(large_data) / 1024 / 1024:.1f} MB")
        print(f"   Velocidade: {speed:.2f} MB/s")
        print(f"   Tempo encrypt: {encrypt_time:.2f}s")
        print(f"   Tempo decrypt: {decrypt_time:.2f}s")
        
        if identical:
            print("    PASSOU: Reversibilidade 100% com arquivos grandes")
            return True
        else:
            # Contar diferenças reais
            diff_count = sum(1 for a, b in zip(large_data, decrypted) if a != b)
            print(f"    FALHOU: {diff_count} bytes diferentes")
            return False
    
    def test_key_sensitivity_real(self):
        """ TESTE REAL: Chaves diferentes → saídas completamente diferentes"""
        print("\n TESTE 4: Sensibilidade à Chave")
        crypto = KayosCryptoUltimate()
        
        test_data = b"Dados de teste para sensibilidade de chave"
        
        # Chaves ligeiramente diferentes
        passwords = [
            "senha_correta_123",
            "senha_correta_124",  # 1 caractere diferente
            "Senha_correta_123",  # Case sensitive
            "senha_correta_123 ",  # Espaço no final
        ]
        
        results = {}
        for pwd in passwords:
            results[pwd] = crypto.encrypt(test_data, pwd)
        
        # VERIFICAÇÃO REAL: Todas as saídas devem ser DIFERENTES
        all_different = len(set(results.values())) == len(passwords)
        
        if all_different:
            print("    PASSOU: Chaves diferentes produzem saídas diferentes")
            return True
        else:
            print("    FALHOU: Algumas chaves produzem mesma saída")
            return False
    
    def test_consistency_across_instances(self):
        """ TESTE REAL: Múltiplas instâncias produzem mesmo resultado"""
        print("\n TESTE 5: Consistência entre Instâncias")
        
        test_data = b"Dados consistentes entre instancias"
        password = os.getenv("KAYOS_AUTH_PASSWORD", "default_insecure_password")
        
        # Criar múltiplas instâncias independentes
        instances = [KayosCryptoUltimate() for _ in range(5)]
        
        results = []
        for i, crypto in enumerate(instances):
            encrypted = crypto.encrypt(test_data, password)
            results.append(encrypted)
            
            # Verificar que cada um pode reverter seu próprio encrypt
            decrypted = crypto.decrypt(encrypted, password)
            if decrypted != test_data:
                print(f"    FALHOU: Instância {i} não reverteu corretamente")
                return False
        
        # VERIFICAÇÃO REAL: Todas as instâncias devem produzir MESMO resultado
        first_result = results[0]
        all_identical = all(r == first_result for r in results)
        
        if all_identical:
            print("    PASSOU: Todas as instâncias produzem mesma saída")
            return True
        else:
            print("    FALHOU: Instâncias produzem saídas diferentes")
            return False

def run_all_real_tests():
    """Executa todos os testes REAIS"""
    print(" TESTES REAIS DE SEGURANÇA - KAYOSCRYPTO ULTIMATE")
    print("=" * 60)
    
    tester = RealSecurityTests()
    
    tests = [
        ("Determinismo", tester.test_deterministic_encryption),
        ("Efeito Avalanche", tester.test_avalanche_effect_real),
        ("Reversibilidade Grande", tester.test_reversibility_large_files),
        ("Sensibilidade Chave", tester.test_key_sensitivity_real),
        ("Consistência Instâncias", tester.test_consistency_across_instances),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"    ERRO em {test_name}: {e}")
            results.append((test_name, False))
    
    # RELATÓRIO FINAL
    print("\n" + "=" * 60)
    print(" RELATÓRIO FINAL - TESTES REAIS")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = " PASSOU" if result else " FALHOU"
        print(f"   {test_name:25} : {status}")
        if result:
            passed += 1
    
    print(f"\n   Total: {passed}/{len(tests)} testes passaram")
    
    if passed == len(tests):
        print("\n SISTEMA APROVADO PARA PRODUÇÃO!")
        return True
    else:
        print(f"\n  {len(tests) - passed} testes precisam de correção")
        return False

if __name__ == "__main__":
    success = run_all_real_tests()
    exit(0 if success else 1)
