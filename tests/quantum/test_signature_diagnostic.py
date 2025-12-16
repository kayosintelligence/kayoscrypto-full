#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico Detalhado: PalindromeSignatureSystem.verify()
==========================================================

Objetivo: Identificar exatamente onde a verificação falha

Author: KAYOS Systems
Date: 15 de Novembro de 2025
"""

import sys
import os
import hmac
import pytest

# Adicionar paths necessários
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from src.core.quantum.palindrome_signatures import PalindromeSignatureSystem, Signature
import hashlib


def test_step_by_step():
    """Testa cada etapa da verificação isoladamente"""
    print("=" * 80)
    print("DIAGNÓSTICO: PalindromeSignatureSystem.verify()")
    print("=" * 80)
    
    system = PalindromeSignatureSystem()
    
    # Gerar keypair
    print("\n[1] Gerando keypair...\n")
    private_key, public_key = system.generate_keypair(seed=b'diagnostic_test')
    print(f" Private Key: {private_key.hex()[:32]}...")
    print(f" Public Key:  {public_key.hex()[:32]}...")
    
    # Assinar mensagem
    message = b"Test message for diagnostic"
    print(f"\n[2] Assinando mensagem: {message}\n")
    signature = system.sign(message, private_key)
    
    print(f" Signature created:")
    print(f"   Forward:  {signature.forward.hex()[:32]}...")
    print(f"   Backward: {signature.backward.hex()[:32]}...")
    print(f"   Checksum: {signature.checksum.hex()[:32]}...")
    
    # Verificação manual passo a passo
    print("\n[3] VERIFICAÇÃO MANUAL (Replicando verify() internamente):\n")
    
    # Passo 1: Propriedade palindrômica
    print("   [3.1] Verificando propriedade palindrômica...")
    is_palindromic = signature.is_valid()
    print(f"         forward == backward[::-1]: {is_palindromic}")
    
    if is_palindromic:
        print(f"          PASSOU: Assinatura é palindrômica")
    else:
        print(f"          FALHOU: Assinatura não é palindrômica")
        print(f"         Forward:  {signature.forward.hex()}")
        print(f"         Backward: {signature.backward.hex()}")
        print(f"         Backward[::-1]: {signature.backward[::-1].hex()}")
        pytest.fail("Assinatura não preserva propriedade palindrômica")
    
    # Passo 2: Checksum
    print("\n   [3.2] Verificando checksum...")
    message_hash = hashlib.sha256(message).digest()
    expected_checksum = hashlib.sha256(
        signature.forward + signature.backward + message_hash
    ).digest()
    checksum_valid = (signature.checksum == expected_checksum)
    
    print(f"         Expected: {expected_checksum.hex()[:32]}...")
    print(f"         Got:      {signature.checksum.hex()[:32]}...")
    print(f"         Match: {checksum_valid}")
    
    if checksum_valid:
        print(f"          PASSOU: Checksum correto")
    else:
        print(f"          FALHOU: Checksum incorreto")
        pytest.fail("Checksum da assinatura divergente")
    
    # Passo 3: Verificação com chave pública
    print("\n   [3.3] Verificando com chave pública...")
    
    # 3.3.1: HMAC da mensagem com chave pública (== privada)
    expected_digest = hmac.new(
        key=public_key,
        msg=message,
        digestmod=hashlib.sha256
    ).digest()
    
    print(f"         Expected digest: {expected_digest.hex()[:32]}...")
    
    # 3.3.2: Transformar digest esperado
    expected_forward = system._palindromic_transform(
        expected_digest,
        direction='forward'
    )
    
    print(f"         Expected forward: {expected_forward.hex()[:32]}...")
    print(f"         Actual forward:   {signature.forward.hex()[:32]}...")
    
    # 3.3.3: Comparar
    forward_match = (signature.forward == expected_forward)
    print(f"         Match: {forward_match}")
    
    if forward_match:
        print(f"          PASSOU: Forward signature matches")
    else:
        print(f"          FALHOU: Forward signature does NOT match")
        print("\n         ANÁLISE DETALHADA:")
        print(f"         Length expected: {len(expected_forward)}")
        print(f"         Length actual:   {len(signature.forward)}")
        
        # Comparar byte a byte
        for i in range(min(len(expected_forward), len(signature.forward))):
            if expected_forward[i] != signature.forward[i]:
                print(f"         Mismatch at byte {i}: {expected_forward[i]} != {signature.forward[i]}")
                if i > 5:  # Mostrar apenas primeiras divergências
                    print(f"         ... (more mismatches)")
                    break
        
        pytest.fail("Forward palindrômico diverge do esperado")
    
    # Verificação final usando método verify()
    print("\n[4] Verificando com método verify() oficial:\n")
    is_valid = system.verify(message, signature, public_key)
    print(f"   Result: {is_valid}")
    
    if is_valid:
        print(f"    PASSOU: verify() retorna True")
    else:
        print(f"    FALHOU: verify() retorna False")
    
    assert is_valid, "verify() deveria retornar True para assinatura emitida"


def test_sign_verify_with_different_keys():
    """Testa se o problema está na geração de keypairs"""
    print("\n" + "=" * 80)
    print("DIAGNÓSTICO: Relação Private Key → Public Key")
    print("=" * 80)
    
    system = PalindromeSignatureSystem()
    message = b"Test message"
    
    print("\n[TEST A] Sign com private_key, verify com public_key (normal):\n")
    
    private_key, public_key = system.generate_keypair(seed=b'seed_a')
    signature = system.sign(message, private_key)
    is_valid = system.verify(message, signature, public_key)
    
    print(f"   Private: {private_key.hex()[:32]}...")
    print(f"   Public:  {public_key.hex()[:32]}...")
    print(f"   Valid:   {is_valid}")
    
    # Investigar a transformação public key
    print("\n[TEST B] Investigando transformação private → public:\n")
    
    # Public key é gerada como: _palindromic_transform(private_key, 'forward')
    expected_public = system._palindromic_transform(private_key, 'forward')
    
    print(f"   Public key gerada:   {public_key.hex()[:32]}...")
    print(f"   Public esperada:     {expected_public.hex()[:32]}...")
    print(f"   Match: {public_key == expected_public}")
    
    # O problema pode estar aqui: verificação usa public_key, mas sign usa private_key
    print("\n[TEST C] Verificando lógica sign() vs verify():\n")
    
    # Sign: HMAC(message, private_key)
    digest_sign = hmac.new(
        key=private_key,
        msg=message,
        digestmod=hashlib.sha256
    ).digest()
    forward_from_sign = system._palindromic_transform(digest_sign, 'forward')
    
    # Verify: HMAC(message, public_key) → devido a simetria HMAC
    digest_verify = hmac.new(
        key=public_key,
        msg=message,
        digestmod=hashlib.sha256
    ).digest()
    forward_from_verify = system._palindromic_transform(digest_verify, 'forward')
    
    print(f"   Digest (sign):   {digest_sign.hex()[:32]}...")
    print(f"   Digest (verify): {digest_verify.hex()[:32]}...")
    print(f"   Digests match: {digest_sign == digest_verify}")
    print()
    print(f"   Forward (sign):   {forward_from_sign.hex()[:32]}...")
    print(f"   Forward (verify): {forward_from_verify.hex()[:32]}...")
    print(f"   Forwards match: {forward_from_sign == forward_from_verify}")
    
    if digest_sign != digest_verify:
        print("\n    CAUSA RAIZ IDENTIFICADA:")
        print("    Sign usa hash(message + private_key)")
        print("    Verify usa hash(message + public_key)")
        print("    Digests diferentes → forwards diferentes → verificação SEMPRE falha!")
        print("\n    SOLUÇÃO:")
        print("   - Opção 1: verify() deve usar private_key (mas isso quebra conceito de assinatura digital)")
        print("   - Opção 2: sign() deve usar public_key (mas isso não faz sentido)")
        print("   - Opção 3: Redesenhar algoritmo para ter relação matemática private ↔ public")
        pytest.fail("Digest entre sign/verify diverge; algoritmo palindrômico inconsistente")
    
    assert forward_from_sign == forward_from_verify, "Forward transform deve coincidir entre sign e verify"


def test_expected_behavior():
    """Testa como um sistema de assinatura deveria funcionar"""
    print("\n" + "=" * 80)
    print("REFERÊNCIA: Como assinatura digital deveria funcionar")
    print("=" * 80)
    
    print("\n[TEORIA]")
    print("   1. Sign: usa PRIVATE key para criar assinatura")
    print("   2. Verify: usa PUBLIC key para validar assinatura")
    print("   3. Relação matemática: public_key = f(private_key) ← função trapdoor")
    print("   4. Assinatura válida IFF foi criada com private_key correspondente ao public_key")
    
    print("\n[IMPLEMENTAÇÃO ATUAL]")
    print("   Sign:   HMAC_SHA256(message, private_key) → transform → signature")
    print("   Verify: HMAC_SHA256(message, public_key) → transform → expected_signature")
    print("   Observação: esquema é simétrico (public_key = private_key) – MAC autenticado")
    
    print("\n[CONCLUSÃO]")
    print("    Sistema simétrico baseado em HMAC garante verificação consistente (public=private)"
        " – requer troca segura de chaves")


if __name__ == "__main__":
    print("\n INICIANDO DIAGNÓSTICO COMPLETO\n")
    
    # Teste 1: Verificação passo a passo
    result1 = test_step_by_step()
    
    # Teste 2: Análise de keypairs
    result2 = test_sign_verify_with_different_keys()
    
    # Teste 3: Comportamento esperado
    test_expected_behavior()
    
    print("\n" + "=" * 80)
    print("RESUMO DO DIAGNÓSTICO")
    print("=" * 80)
    
    if not result1 or not result2:
        print("\n BUG CONFIRMADO: verify() falha devido a lógica incorreta")
        print("\nPróximas ações:")
        print("   1. Redesenhar algoritmo com relação matemática private ↔ public")
        print("   2. Ou usar criptografia assimétrica tradicional (RSA/ECDSA) como base")
        print("   3. Manter propriedade palindrômica como camada adicional")
    else:
        print("\n Sistema funcionando corretamente")
    
    print("\n" + "=" * 80)
