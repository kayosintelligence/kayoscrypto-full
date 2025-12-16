#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KAYOSCRYPTO + KAYOSQL INTEGRATION EXAMPLE
==========================================

Demonstração da integração entre KayosCrypto Ultimate e KayosQL.
"""

import os
import sys
import time

# Adicionar paths
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def demo_kayosql_integration():
    """Demonstração da integração KayosCrypto + KayosQL"""

    print("=" * 80)
    print("KAYOSCRYPTO + KAYOSQL INTEGRATION DEMO")
    print("=" * 80)

    try:
        from core.kayoscrypto_ultimate import KayosCryptoUltimate
    except ImportError as e:
        print(f"Erro: KayosCrypto Ultimate não encontrado - {e}")
        return

    # Inicializar sistema
    print("\nInicializando KayosCrypto Ultimate...")
    crypto = KayosCryptoUltimate()

    # Verificar KayosQL
    kayosql_available = crypto.kayosql_integration is not None
    print(f"KayosQL Status: {'Ativo' if kayosql_available else 'Compatibilidade (SQLite)'}")

    # Dados de teste
    test_data = b"Este e um teste de integracao KayosCrypto + KayosQL"
    password = os.getenv("KAYOS_AUTH_PASSWORD", "default_insecure_password")

    print("\nTestando criptografia...")
    encrypted = crypto.encrypt(test_data, password)
    decrypted = crypto.decrypt(encrypted, password)

    success = test_data == decrypted
    print(f"Criptografia: {'OK' if success else 'FALHA'}")

    if kayosql_available:
        print("\nTestando armazenamento KayosQL...")

        # Armazenar
        stored = crypto.store_crypto_data("test_key", encrypted)
        print(f"Armazenamento: {'OK' if stored else 'FALHA'}")

        if stored:
            # Recuperar
            retrieved = crypto.retrieve_crypto_data("test_key")
            if retrieved and retrieved == encrypted:
                print("Recuperação: OK")
            else:
                print("Recuperação: FALHA")

    print("\nDemo concluída!")

if __name__ == "__main__":
    demo_kayosql_integration()