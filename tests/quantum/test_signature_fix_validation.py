#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste: Verificação da Correção do Bug de Signature
===================================================

Valida se correção v6.0.1 funciona corretamente

Author: KAYOS Systems
Date: 15 de Novembro de 2025
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from src.core.quantum.palindrome_signatures import PalindromeSignatureSystem


def test_fixed_verification():
    """Testa se verificação agora funciona"""
    print("=" * 80)
    print("TESTE: Correção v6.0.1 - Verificação de Assinatura")
    print("=" * 80)
    
    system = PalindromeSignatureSystem()
    
    # Teste 1: Caso básico
    print("\n[TEST 1] Caso básico - mensagem simples\n")
    
    private_key, public_key = system.generate_keypair(seed=b'test_seed_1')
    message = b"Hello, KayosCrypto!"
    
    print(f"   Private Key: {private_key.hex()[:32]}...")
    print(f"   Public Key:  {public_key.hex()[:32]}...")
    print(f"   Message:     {message.decode()}")
    
    # Assinar
    signature = system.sign(message, private_key)
    print(f"\n     Signature created:")
    print(f"      Forward:  {signature.forward.hex()[:32]}...")
    print(f"      Backward: {signature.backward.hex()[:32]}...")
    print(f"      Palindrome: {signature.is_valid()}")
    
    # Verificar
    is_valid = system.verify(message, signature, public_key)
    print(f"\n    Verification: {is_valid}")
    
    if is_valid:
        print(f"       PASSOU: Assinatura válida!")
    else:
        print(f"       FALHOU: Assinatura inválida")
    assert is_valid, "Assinatura legítima deve validar"
    
    # Teste 2: Mensagem adulterada
    print("\n[TEST 2] Mensagem adulterada (deve falhar)\n")
    
    fake_message = b"Hello, Fake Message!"
    is_fake_valid = system.verify(fake_message, signature, public_key)
    
    print(f"   Original message:  {message.decode()}")
    print(f"   Fake message:      {fake_message.decode()}")
    print(f"   Verification:      {is_fake_valid}")
    
    if not is_fake_valid:
        print(f"    PASSOU: Sistema detecta adulteração!")
    else:
        print(f"    FALHOU: Sistema não detecta adulteração")
    assert not is_fake_valid, "Sistema deve rejeitar mensagem adulterada"
    
    # Teste 3: Assinatura adulterada
    print("\n[TEST 3] Assinatura adulterada (deve falhar)\n")
    
    from src.core.quantum.palindrome_signatures import Signature
    
    fake_signature = Signature(
        forward=signature.forward[:16] + b'\x00' * 16,  # Corromper forward
        backward=signature.backward,
        checksum=signature.checksum
    )
    
    is_fake_sig_valid = system.verify(message, fake_signature, public_key)
    
    print(f"   Original forward:  {signature.forward.hex()[:32]}...")
    print(f"   Fake forward:      {fake_signature.forward.hex()[:32]}...")
    print(f"   Verification:      {is_fake_sig_valid}")
    
    if not is_fake_sig_valid:
        print(f"    PASSOU: Sistema detecta assinatura adulterada!")
    else:
        print(f"    FALHOU: Sistema não detecta assinatura adulterada")
    assert not is_fake_sig_valid, "Sistema deve rejeitar assinatura adulterada"
    
    # Teste 4: Chave pública errada
    print("\n[TEST 4] Chave pública errada (deve falhar)\n")
    
    _, wrong_public_key = system.generate_keypair(seed=b'wrong_seed')
    is_wrong_key_valid = system.verify(message, signature, wrong_public_key)
    
    print(f"   Correct public key: {public_key.hex()[:32]}...")
    print(f"   Wrong public key:   {wrong_public_key.hex()[:32]}...")
    print(f"   Verification:       {is_wrong_key_valid}")
    
    if not is_wrong_key_valid:
        print(f"    PASSOU: Sistema detecta chave errada!")
    else:
        print(f"    FALHOU: Sistema não detecta chave errada")
    assert not is_wrong_key_valid, "Sistema deve rejeitar chave pública incorreta"
    
    # Teste 5: Múltiplas mensagens com mesma keypair
    print("\n[TEST 5] Múltiplas mensagens com mesma keypair\n")
    
    messages = [
        b"Message 1",
        b"Message 2",
        b"Message 3: Longer message with special chars !@#$%"
    ]
    
    for i, msg in enumerate(messages, 1):
        sig = system.sign(msg, private_key)
        valid = system.verify(msg, sig, public_key)
        print(f"   Message {i}: {valid}")
        assert valid, f"Mensagem {i} não validou com a mesma keypair"
    
    print(f"    PASSOU: Todas as mensagens verificadas!")
    
    # Resumo
    print("\n" + "=" * 80)
    print("RESUMO DOS TESTES")
    print("=" * 80)
    
    print(f"\n   Passou: 5/5 testes")
    print(f"    SUCESSO: Correção v6.0.1 funcionando perfeitamente!")


if __name__ == "__main__":
    success = test_fixed_verification()
    exit(0 if success else 1)
