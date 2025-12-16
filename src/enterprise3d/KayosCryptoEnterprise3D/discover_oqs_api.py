#!/usr/bin/env python3
"""
 DESCOBRINDO API DA VERSÃO OQS 0.14.1
"""

import oqs

print(" DESCOBRINDO API OQS 0.14.1")
print("=" * 45)

# Testar criação de KEM
print("1. Testando KeyEncapsulation...")
try:
 # Testar diferentes algoritmos
 test_algos = ['Kyber512', 'Kyber768', 'Kyber1024', 'Classic-McEliece-348864']
 
 for algo in test_algos:
 try:
 with oqs.KeyEncapsulation(algo) as kem:
 print(f" {algo}: Suportado")
 print(f" - Tamanho chave pública: {kem.details['length_public_key']} bytes")
 print(f" - Tamanho segredo compartilhado: {kem.details['length_shared_secret']} bytes")
 except Exception as e:
 print(f" {algo}: {e}")
 
except Exception as e:
 print(f" KeyEncapsulation geral: {e}")

# Explorar métodos disponíveis
print("\n2. Explorando métodos KeyEncapsulation...")
try:
 with oqs.KeyEncapsulation('Kyber512') as kem:
 methods = [method for method in dir(kem) if not method.startswith('_')]
 print(f" Métodos disponíveis: {', '.join(methods)}")
 
 # Testar operações básicas
 print("\n3. Teste completo Kyber512...")
 public_key = kem.generate_keypair()
 secret_key = kem.export_secret_key()
 
 # Encapsular
 ciphertext, shared_secret_server = kem.encap_secret(public_key)
 print(f" Encapsulação: {len(ciphertext)} bytes ciphertext")
 
 # Decapsular (com nova instância)
 with oqs.KeyEncapsulation('Kyber512') as kem_client:
 kem_client.import_secret_key(secret_key)
 shared_secret_client = kem_client.decap_secret(ciphertext)
 
 if shared_secret_server == shared_secret_client:
 print(" Segredos combinam! KEM funcionando!")
 else:
 print(" Segredos não combinam!")
 
except Exception as e:
 print(f" Exploração falhou: {e}")

print("\n" + "=" * 45)
print(" API descoberta - Pronto para implementação!")
