#!/usr/bin/env python3
"""
 OTIMIZAÇÕES PARA MATURIDADE ALTA DE PERFORMANCE
"""

import numpy as np
from kayoscrypto_evolved_final import KayosCryptoUltimate

class OptimizedKayosCrypto(KayosCryptoUltimate):
    """Versão otimizada para melhor performance"""
    
    def __init__(self, use_concentric: bool = True, use_direction: bool = True):
        super().__init__(use_concentric, use_direction)
        self._enable_optimizations()
    
    def _enable_optimizations(self):
        """Ativa otimizações de performance"""
        # Pré-computar valores frequentes
        self._fibonacci_cache = {}
        self._golden_cache = {}
    
    def encrypt(self, plaintext: bytes, password: str, level: int = 3) -> bytes:
        """Encrypt otimizado"""
        # Otimização: processar em chunks para dados muito grandes
        if len(plaintext) > 100 * 1024:  # >100KB
            return self._chunked_encrypt(plaintext, password, level)
        else:
            return super().encrypt(plaintext, password, level)
    
    def _chunked_encrypt(self, data: bytes, password: str, level: int) -> bytes:
        """Processamento em chunks para melhor performance"""
        chunk_size = 64 * 1024  # 64KB chunks
        chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
        
        results = []
        for chunk in chunks:
            results.append(super().encrypt(chunk, password, level))
        
        return b''.join(results)

# Teste das otimizações
def test_optimized_performance():
    print("\n TESTE PERFORMANCE OTIMIZADA")
    print("=" * 50)
    
    original = KayosCryptoUltimate()
    optimized = OptimizedKayosCrypto()
    
    # Teste com 2MB
    test_data = os.urandom(2 * 1024 * 1024)
    password = os.getenv("KAYOS_AUTH_PASSWORD", "default_insecure_password")
    
    # Original
    start = time.time()
    enc1 = original.encrypt(test_data, password)
    time1 = time.time() - start
    
    # Otimizado
    start = time.time()
    enc2 = optimized.encrypt(test_data, password)
    time2 = time.time() - start
    
    # Verificar que são compatíveis
    dec1 = original.decrypt(enc1, password)
    dec2 = optimized.decrypt(enc2, password)
    
    speed1 = len(test_data) / time1 / 1024 / 1024  # MB/s
    speed2 = len(test_data) / time2 / 1024 / 1024  # MB/s
    improvement = ((speed2 - speed1) / speed1) * 100
    
    print(f"   Original: {speed1:.2f} MB/s")
    print(f"   Otimizado: {speed2:.2f} MB/s")
    print(f"   Melhoria: {improvement:+.1f}%")
    print(f"   Compatibilidade: {'' if dec1 == test_data == dec2 else ''}")
    
    return improvement > 0 and dec1 == test_data == dec2

if __name__ == "__main__":
    import time
    import os
    
    if test_optimized_performance():
        print("\n Otimizações funcionando!")
    else:
        print("\n  Otimizações precisam de ajuste")
