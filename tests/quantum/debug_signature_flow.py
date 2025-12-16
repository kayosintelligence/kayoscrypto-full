#!/usr/bin/env python3
"""Debug detalhado do fluxo de verificação"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from src.core.quantum.palindrome_signatures import PalindromeSignatureSystem
import hashlib
import hmac

system = PalindromeSignatureSystem()

# Gerar keypair
print("="*80)
print("DEBUG: Fluxo completo de sign() e verify()")
print("="*80)

private_key, public_key = system.generate_keypair(seed=b'debug_seed')
message = b"Test"

print(f"\n1. KEYPAIR GENERATION:")
print(f"   Seed: {b'debug_seed'.hex()}")
print(f"   Private = SHA256(seed): {private_key.hex()[:32]}...")
print(f"   Public = SHA256(private): {public_key.hex()[:32]}...")

# SIGN
print(f"\n2. SIGN PROCESS:")
signature_base_sign = hmac.new(private_key, message, hashlib.sha256).digest()
print(f"   HMAC(message, private_key): {signature_base_sign.hex()[:32]}...")

forward_sign = system._palindromic_transform(signature_base_sign, direction='forward')
print(f"   Palindrome transform: {forward_sign.hex()[:32]}...")

signature = system.sign(message, private_key)
print(f"   Final signature.forward: {signature.forward.hex()[:32]}...")

# VERIFY
print(f"\n3. VERIFY PROCESS:")
derived_private = hashlib.sha256(public_key).digest()
print(f"   Derived private = SHA256(public_key): {derived_private.hex()[:32]}...")
print(f"   Original private:                     {private_key.hex()[:32]}...")
print(f"   Match: {derived_private == private_key}")

if derived_private != private_key:
    print(f"\n    PROBLEMA ENCONTRADO!")
    print(f"   - public_key = SHA256(private_key)")
    print(f"   - derived_private = SHA256(public_key) = SHA256(SHA256(private_key))")
    print(f"   - derived_private ≠ private_key")
    print(f"   - Logo: HMAC(msg, derived_private) ≠ HMAC(msg, private_key)")
    print(f"   - Verificação SEMPRE falhará!")
    
    signature_base_verify = hmac.new(derived_private, message, hashlib.sha256).digest()
    print(f"\n   HMAC com derived_private: {signature_base_verify.hex()[:32]}...")
    print(f"   HMAC com original private: {signature_base_sign.hex()[:32]}...")
    print(f"   Match: {signature_base_verify == signature_base_sign}")

print("\n" + "="*80)
print("CONCLUSÃO:")
print("="*80)
print("\n Bug fundamental: public_key = hash(private_key)")
print("   Logo: hash(public_key) ≠ private_key")
print("   Não podemos 'derivar' private de public com hash simples!")
print("\n SOLUÇÃO:")
print("   - Não usar hash para derivar private de public")
print("   - Usar a MESMA chave para sign e verify (HMAC symmetric)")
print("   - Ou implementar criptografia assimétrica real (ECC, RSA)")
