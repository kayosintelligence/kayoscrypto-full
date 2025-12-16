#!/usr/bin/env python3
"""
Teste de Importações Individuais
Diagnóstico preciso dos problemas de importação
"""

import sys
import os

def testar_importacao(modulo, descricao):
    """Testa uma importação específica e retorna o resultado"""
    try:
        __import__(modulo)
        print(f" {descricao}: OK")
        return True
    except ImportError as e:
        print(f" {descricao}: {e}")
        return False
    except Exception as e:
        print(f"  {descricao}: ERRO GERAL - {e}")
        return False

def main():
    print(" DIAGNÓSTICO DE IMPORTAÇÕES")
    print("=" * 50)

    # Configurar caminhos
    sys.path.insert(0, '/home/kbe/KAYOS_SYSTEMS/KayosCrypto/src')
    sys.path.insert(0, '/home/kbe/KAYOS_SYSTEMS/KayosSanitizador/src')

    print("\n Caminhos configurados:")
    for i, path in enumerate(sys.path[:5]):
        print(f"  {i+1}. {path}")

    print("\n Testando importações do KayosSanitizador:")

    testes_sanitizador = [
        ('core.quantum_monitor', 'Quantum Monitor'),
        ('core.sanitizador_quantico', 'Sanitizador Quântico'),
        ('core.gatekeeper_pie', 'Gatekeeper PIE'),
        ('core.sanitizador_kayosql', 'Sanitizador KayosQL'),
        ('processors.sanitizador_pie', 'PIE Processor'),
    ]

    resultados_sanitizador = []
    for modulo, desc in testes_sanitizador:
        resultado = testar_importacao(modulo, desc)
        resultados_sanitizador.append(resultado)

    print("\n Testando importações do KayosCrypto:")

    testes_crypto = [
        ('core.kayoscrypto_ultimate', 'KayosCrypto Ultimate'),
        ('core.fibonacci_direction', 'Fibonacci Direction'),
        ('core.ezekiel_concentric', 'Ezekiel Concentric'),
        ('core.kayoscrypto_final', 'KayosCrypto Final'),
    ]

    resultados_crypto = []
    for modulo, desc in testes_crypto:
        resultado = testar_importacao(modulo, desc)
        resultados_crypto.append(resultado)

    print("\n RESULTADOS FINAIS:")
    print(f"  KayosSanitizador: {sum(resultados_sanitizador)}/{len(resultados_sanitizador)} OK")
    print(f"  KayosCrypto: {sum(resultados_crypto)}/{len(resultados_crypto)} OK")
    print(f"  Total: {sum(resultados_sanitizador + resultados_crypto)}/{len(resultados_sanitizador + resultados_crypto)} OK")

    if all(resultados_sanitizador + resultados_crypto):
        print("\n TODAS AS IMPORTAÇÕES FUNCIONANDO!")
    else:
        print("\n  PROBLEMAS DETECTADOS - REVISAR DEPENDÊNCIAS")

if __name__ == "__main__":
    main()