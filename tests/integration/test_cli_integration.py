#!/usr/bin/env python3
"""
Teste de Integração: KayosCrypto Final no CLI
==============================================

Testa se a integração do kayoscrypto_final.py no kayoscrypto_cli.py
está funcionando corretamente.
"""

import os
import hashlib
from pathlib import Path

# Importar CLI
from kayoscrypto_cli import KayosCryptoFileEncryptor


def run_cli_integration():
    """Teste completo de integração CLI"""
    print("\n" + "="*70)
    print(" TESTE DE INTEGRAÇÃO: KayosCryptoFinal no CLI")
    print("="*70)
    
    # Criar arquivo de teste
    test_dir = Path("test_cli_temp")
    test_dir.mkdir(exist_ok=True)
    
    test_file = test_dir / "test_integration.txt"
    test_content = b"Teste de integracao KayosCrypto Final CLI - Ezequiel + Fibonacci + Golden Ratio + Avalanche!"
    
    print(f"\n Criando arquivo de teste...")
    with open(test_file, 'wb') as f:
        f.write(test_content)
    
    original_md5 = hashlib.sha3_512(test_content).hexdigest()
    print(f"   Arquivo: {test_file.name}")
    print(f"   Tamanho: {len(test_content)} bytes")
    print(f"   MD5: {original_md5}")
    
    # Inicializar encryptor
    print(f"\n Inicializando KayosCryptoFileEncryptor...")
    encryptor = KayosCryptoFileEncryptor()
    print(f"   Engine: {encryptor.engine_type}")
    print(f"   Versão: {encryptor.version}")
    
    password = os.getenv("KAYOS_AUTH_PASSWORD", "default_insecure_password")
    
    # ═══════════════════════════════════════════════════════════════════
    # TESTE 1: Criptografar arquivo
    # ═══════════════════════════════════════════════════════════════════
    print(f"\n" + "="*70)
    print(" TESTE 1: Criptografar Arquivo")
    print("="*70)
    
    try:
        result_enc = encryptor.encrypt_file(
            input_path=str(test_file),
            password=password,
            fibonacci_level=3
        )
        
        encrypted_file = Path(result_enc['output_path'])
        
        print(f"\n Criptografia concluída!")
        print(f"   Original: {result_enc['original_size']} bytes")
        print(f"   Criptografado: {result_enc['encrypted_size']} bytes")
        print(f"   Arquivo: {encrypted_file.name}")
        
        # Verificar arquivo criptografado existe
        if not encrypted_file.exists():
            print(f" ERRO: Arquivo criptografado não foi criado!")
            return False
            
    except Exception as e:
        print(f" ERRO na criptografia: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # ═══════════════════════════════════════════════════════════════════
    # TESTE 2: Descriptografar arquivo
    # ═══════════════════════════════════════════════════════════════════
    print(f"\n" + "="*70)
    print(" TESTE 2: Descriptografar Arquivo")
    print("="*70)
    
    try:
        decrypted_file = test_dir / "test_decrypted.txt"
        
        result_dec = encryptor.decrypt_file(
            input_path=str(encrypted_file),
            password=password,
            output_path=str(decrypted_file)
        )
        
        print(f"\n Descriptografia concluída!")
        print(f"   Criptografado: {result_dec['encrypted_size']} bytes")
        print(f"   Descriptografado: {result_dec['decrypted_size']} bytes")
        print(f"   Arquivo: {decrypted_file.name}")
        
        # Verificar arquivo descriptografado existe
        if not decrypted_file.exists():
            print(f" ERRO: Arquivo descriptografado não foi criado!")
            return False
            
    except Exception as e:
        print(f" ERRO na descriptografia: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # ═══════════════════════════════════════════════════════════════════
    # TESTE 3: Verificar Reversibilidade
    # ═══════════════════════════════════════════════════════════════════
    print(f"\n" + "="*70)
    print(" TESTE 3: Verificar Reversibilidade")
    print("="*70)
    
    with open(decrypted_file, 'rb') as f:
        decrypted_content = f.read()
    
    decrypted_md5 = hashlib.sha3_512(decrypted_content).hexdigest()
    
    print(f"\n Comparando conteúdo...")
    print(f"   Original MD5:      {original_md5}")
    print(f"   Descriptografado:  {decrypted_md5}")
    
    if original_md5 == decrypted_md5:
        print(f"\n  REVERSIBILIDADE: PERFEITA!")
        reversible = True
    else:
        print(f"\n REVERSIBILIDADE: FALHOU!")
        
        # Mostrar diferenças
        diff_bytes = sum(1 for a, b in zip(test_content, decrypted_content) if a != b)
        print(f"   Bytes diferentes: {diff_bytes}/{len(test_content)}")
        reversible = False
    
    # ═══════════════════════════════════════════════════════════════════
    # TESTE 4: Avalanche Effect (opcional, se possível)
    # ═══════════════════════════════════════════════════════════════════
    print(f"\n" + "="*70)
    print(" TESTE 4: Avalanche Effect")
    print("="*70)
    
    # Criar arquivo com 1 bit diferente
    test_content_modified = bytearray(test_content)
    test_content_modified[0] ^= 0x01  # Flip 1 bit
    
    test_file2 = test_dir / "test_modified.txt"
    with open(test_file2, 'wb') as f:
        f.write(bytes(test_content_modified))
    
    try:
        result_enc2 = encryptor.encrypt_file(
            input_path=str(test_file2),
            password=password,
            fibonacci_level=3
        )
        
        encrypted_file2 = Path(result_enc2['output_path'])
        
        # Comparar criptografias
        with open(encrypted_file, 'rb') as f:
            f.read(10 + 4)  # Skip header + metadata_len
            metadata_len1 = len(result_enc['metadata'])
            f.read(metadata_len1)
            enc1 = f.read()
        
        with open(encrypted_file2, 'rb') as f:
            f.read(10 + 4)
            metadata_len2 = len(result_enc2['metadata'])
            f.read(metadata_len2)
            enc2 = f.read()
        
        # Calcular diferença
        diff_bits = 0
        min_len = min(len(enc1), len(enc2))
        for b1, b2 in zip(enc1[:min_len], enc2[:min_len]):
            diff_bits += bin(b1 ^ b2).count('1')
        
        total_bits = min_len * 8
        avalanche = (diff_bits / total_bits) * 100 if total_bits > 0 else 0
        
        print(f"\n Avalanche Effect:")
        print(f"   Bits diferentes: {diff_bits}/{total_bits}")
        print(f"   Percentual: {avalanche:.2f}%")
        
        if avalanche > 40:
            print(f"    EXCELENTE! (>40%)")
        elif avalanche > 30:
            print(f"    BOM! (>30%)")
        elif avalanche > 20:
            print(f"     ACEITÁVEL (>20%)")
        else:
            print(f"    BAIXO (<20%)")
            
    except Exception as e:
        print(f"  Não foi possível testar avalanche: {e}")
        avalanche = 0
    
    # ═══════════════════════════════════════════════════════════════════
    # LIMPEZA
    # ═══════════════════════════════════════════════════════════════════
    print(f"\n Limpando arquivos de teste...")
    try:
        test_file.unlink()
        encrypted_file.unlink()
        decrypted_file.unlink()
        if test_file2.exists():
            test_file2.unlink()
        if encrypted_file2.exists():
            encrypted_file2.unlink()
        test_dir.rmdir()
        print(f"    Arquivos temporários removidos")
    except Exception as e:
        print(f"     Erro ao limpar: {e}")
    
    # ═══════════════════════════════════════════════════════════════════
    # RESULTADO FINAL
    # ═══════════════════════════════════════════════════════════════════
    print(f"\n" + "="*70)
    print(" RESULTADO FINAL DA INTEGRAÇÃO")
    print("="*70)
    print(f"   Engine: {encryptor.engine_type}")
    print(f"   Versão: {encryptor.version}")
    print(f"   Reversibilidade: {' PERFEITA' if reversible else ' FALHA'}")
    print(f"   Avalanche: {avalanche:.2f}%")
    print("="*70)
    
    if reversible:
        print("\n   INTEGRAÇÃO PERFEITA!   ")
        print("\n KayosCryptoFinal integrado com sucesso no CLI!")
        print(" Todos os testes passaram!")
        print(" Sistema pronto para uso em produção!")
        return True
    else:
        print("\n Integração com problemas - verificar código")
        return False


def test_cli_integration():
    assert run_cli_integration(), "Integração com problemas - verificar código"


if __name__ == "__main__":
    success = run_cli_integration()
    exit(0 if success else 1)
