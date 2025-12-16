#!/usr/bin/env python3
"""
 DIAGNÓSTICO DA API OQS
"""

import oqs

print(" DIAGNÓSTICO DA INSTALAÇÃO OQS")
print("=" * 40)

# Listar todos os atributos disponíveis
print(" Atributos disponíveis no módulo oqs:")
attrs = [attr for attr in dir(oqs) if not attr.startswith('_')]
for attr in sorted(attrs):
 print(f" - {attr}")

print("\n Testando funcionalidades disponíveis...")

# Testar diferentes versões da API
try:
 # Tentar versão mais nova
 print("\n1. Tentando oqs.Mechanism...")
 mechanisms = oqs.Mechanism
 print(" oqs.Mechanism disponível")
 print(f" Algoritmos: {[m for m in dir(mechanisms) if not m.startswith('_')][:5]}...")
except AttributeError as e:
 print(f" oqs.Mechanism não disponível: {e}")

try:
 # Tentar versão alternativa
 print("\n2. Tentando oqs.get_supported_kem_mechanisms...")
 kems = oqs.get_supported_kem_mechanisms()
 print(f" KEMs suportados: {kems[:3]}...")
except AttributeError as e:
 print(f" get_supported_kem_mechanisms não disponível: {e}")

try:
 # Tentar criação direta
 print("\n3. Tentando criar objeto de encapsulação...")
 kem = oqs.KeyEncapsulation('Kyber1024')
 print(" KeyEncapsulation funcionando!")
 kem.release()
except Exception as e:
 print(f" KeyEncapsulation falhou: {e}")

print("\n Informações da versão:")
try:
 print(f" Versão OQS: {oqs.oqs_version()}")
except:
 print(" Versão: Não disponível")

print("\n" + "=" * 40)
print(" Use as funções disponíveis acima para a implementação")
