import os
#!/usr/bin/env python3
"""
 BENCHMARKS DE PERFORMANCE - ASSINATURAS DIGITAIS
Compara v6.0.3 (HMAC) vs v6.1 (Ed25519) no pipeline completo

Autor: KAYOS SYSTEMS
Data: Janeiro 2025
Versão: 1.0.0 (Phase 3.7 - Task 4)
"""

import pytest
import time
import statistics
from pathlib import Path
import sys

# Adicionar path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.core.kayoscrypto_ultimate import KayosCryptoUltimate


class TestSignaturePerformance:
    """Benchmarks de performance para assinaturas v6.0.3 vs v6.1"""
    
    @pytest.fixture
    def data_1kb(self):
        """1 KB de dados"""
        return b"A" * 1024
    
    @pytest.fixture
    def data_10kb(self):
        """10 KB de dados"""
        return b"B" * (10 * 1024)
    
    @pytest.fixture
    def data_100kb(self):
        """100 KB de dados"""
        return b"C" * (100 * 1024)
    
    @pytest.fixture
    def data_1mb(self):
        """1 MB de dados"""
        return b"D" * (1024 * 1024)
    
    @pytest.fixture
    def cipher_hmac(self):
        """Cipher com HMAC (v6.0.3)"""
        return KayosCryptoUltimate(use_quantum=True, use_ed25519=False, use_direction=False)
    
    @pytest.fixture
    def cipher_ed25519(self):
        """Cipher com Ed25519 (v6.1)"""
        return KayosCryptoUltimate(use_quantum=True, use_ed25519=True, use_direction=False)
    
    def benchmark_operation(self, func, *args, iterations=100):
        """
        Executa benchmark de uma operação
        
        Returns:
            dict: {
                'mean': média (ms),
                'median': mediana (ms),
                'std': desvio padrão (ms),
                'min': mínimo (ms),
                'max': máximo (ms),
                'throughput_mb_s': throughput (MB/s) - se aplicável
            }
        """
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            func(*args)
            end = time.perf_counter()
            times.append((end - start) * 1000)  # ms
        
        return {
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'std': statistics.stdev(times) if len(times) > 1 else 0,
            'min': min(times),
            'max': max(times)
        }
    
    def test_sign_performance_1kb(self, cipher_hmac, cipher_ed25519, data_1kb):
        """
        Benchmark: Sign (1 KB)
        
        Expected:
        - HMAC: ~0.008 ms (126k ops/s)
        - Ed25519: ~0.026 ms (38k ops/s)
        """
        # HMAC
        private_hmac, _ = cipher_hmac.generate_keypair()
        result_hmac = self.benchmark_operation(
            cipher_hmac.sign_message, data_1kb, private_hmac, iterations=1000
        )
        
        # Ed25519
        private_ed, _ = cipher_ed25519.generate_keypair()
        result_ed = self.benchmark_operation(
            cipher_ed25519.sign_message, data_1kb, private_ed, iterations=1000
        )
        
        # Exibir resultados
        print(f"\n{'='*80}")
        print(f"BENCHMARK: Sign (1 KB)")
        print(f"{'='*80}")
        print(f"HMAC (v6.0.3):     {result_hmac['mean']:.3f} ms ± {result_hmac['std']:.3f} ms")
        print(f"Ed25519 (v6.1):    {result_ed['mean']:.3f} ms ± {result_ed['std']:.3f} ms")
        print(f"Overhead Ed25519:  {(result_ed['mean'] / result_hmac['mean'] - 1) * 100:.1f}% slower")
        print(f"{'='*80}")
        
        # Validações
        assert result_hmac['mean'] < 1.0, "HMAC sign should be < 1 ms"
        assert result_ed['mean'] < 5.0, "Ed25519 sign should be < 5 ms"
    
    def test_verify_performance_1kb(self, cipher_hmac, cipher_ed25519, data_1kb):
        """
        Benchmark: Verify (1 KB)
        
        Expected:
        - HMAC: ~0.007 ms (130k ops/s)
        - Ed25519: ~0.038 ms (26k ops/s)
        """
        # HMAC
        private_hmac, public_hmac = cipher_hmac.generate_keypair()
        sig_hmac = cipher_hmac.sign_message(data_1kb, private_hmac)
        result_hmac = self.benchmark_operation(
            cipher_hmac.verify_signature, data_1kb, sig_hmac, public_hmac, iterations=1000
        )
        
        # Ed25519
        private_ed, public_ed = cipher_ed25519.generate_keypair()
        sig_ed = cipher_ed25519.sign_message(data_1kb, private_ed)
        result_ed = self.benchmark_operation(
            cipher_ed25519.verify_signature, data_1kb, sig_ed, public_ed, iterations=1000
        )
        
        # Exibir resultados
        print(f"\n{'='*80}")
        print(f"BENCHMARK: Verify (1 KB)")
        print(f"{'='*80}")
        print(f"HMAC (v6.0.3):     {result_hmac['mean']:.3f} ms ± {result_hmac['std']:.3f} ms")
        print(f"Ed25519 (v6.1):    {result_ed['mean']:.3f} ms ± {result_ed['std']:.3f} ms")
        print(f"Overhead Ed25519:  {(result_ed['mean'] / result_hmac['mean'] - 1) * 100:.1f}% slower")
        print(f"{'='*80}")
        
        # Validações
        assert result_hmac['mean'] < 1.0, "HMAC verify should be < 1 ms"
        assert result_ed['mean'] < 10.0, "Ed25519 verify should be < 10 ms"
    
    def test_signature_overhead_1mb(self, cipher_hmac, cipher_ed25519, data_1mb):
        """
        Benchmark: Overhead de Assinatura (1 MB)
        Sign + Verify (sem encrypt/decrypt)
        
        Expected overhead:
        - HMAC: ~2-3 ms
        - Ed25519: ~6-8 ms
        """
        password = os.getenv("KAYOS_AUTH_PASSWORD", "default_insecure_password")
        
        # Simular ciphertext (1 MB)
        ciphertext = data_1mb
        
        # HMAC: Sign + Verify
        private_hmac, public_hmac = cipher_hmac.generate_keypair()
        
        times_hmac = []
        for _ in range(100):
            start = time.perf_counter()
            
            sig = cipher_hmac.sign_message(ciphertext, private_hmac)
            is_valid = cipher_hmac.verify_signature(ciphertext, sig, public_hmac)
            assert is_valid
            
            end = time.perf_counter()
            times_hmac.append((end - start) * 1000)
        
        result_hmac = {
            'mean': statistics.mean(times_hmac),
            'std': statistics.stdev(times_hmac)
        }
        
        # Ed25519: Sign + Verify
        private_ed, public_ed = cipher_ed25519.generate_keypair()
        
        times_ed = []
        for _ in range(100):
            start = time.perf_counter()
            
            sig = cipher_ed25519.sign_message(ciphertext, private_ed)
            is_valid = cipher_ed25519.verify_signature(ciphertext, sig, public_ed)
            assert is_valid
            
            end = time.perf_counter()
            times_ed.append((end - start) * 1000)
        
        result_ed = {
            'mean': statistics.mean(times_ed),
            'std': statistics.stdev(times_ed)
        }
        
        # Exibir resultados
        print(f"\n{'='*80}")
        print(f"BENCHMARK: Signature Overhead (Sign + Verify, 1 MB)")
        print(f"{'='*80}")
        print(f"HMAC (v6.0.3):     {result_hmac['mean']:.2f} ms ± {result_hmac['std']:.2f} ms")
        print(f"Ed25519 (v6.1):    {result_ed['mean']:.2f} ms ± {result_ed['std']:.2f} ms")
        print(f"Overhead Ed25519:  +{result_ed['mean'] - result_hmac['mean']:.2f} ms ({(result_ed['mean'] / result_hmac['mean'] - 1) * 100:.1f}% slower)")
        print(f"{'='*80}")
        print(f"Throughput (sign + verify):")
        print(f"  HMAC (v6.0.3):   {1024 / result_hmac['mean']:.1f} MB/s")
        print(f"  Ed25519 (v6.1):  {1024 / result_ed['mean']:.1f} MB/s")
        print(f"{'='*80}")
        
        # Validações
        assert result_hmac['mean'] < 10, "HMAC sign+verify should be < 10 ms"
        assert result_ed['mean'] < 20, "Ed25519 sign+verify should be < 20 ms"
    
    def test_scalability_comparison(self, cipher_hmac, cipher_ed25519, 
                                   data_1kb, data_10kb, data_100kb, data_1mb):
        """
        Benchmark: Escalabilidade (1 KB → 1 MB)
        
        Testa como performance escala com tamanho do input
        """
        datasets = [
            ("1 KB", data_1kb),
            ("10 KB", data_10kb),
            ("100 KB", data_100kb),
            ("1 MB", data_1mb)
        ]
        
        print(f"\n{'='*80}")
        print(f"BENCHMARK: Escalabilidade (Sign + Verify)")
        print(f"{'='*80}")
        print(f"{'Size':<10} {'HMAC (ms)':<15} {'Ed25519 (ms)':<15} {'Overhead':<10}")
        print(f"{'-'*80}")
        
        for size_name, data in datasets:
            # HMAC
            private_hmac, public_hmac = cipher_hmac.generate_keypair()
            result_hmac = self.benchmark_operation(
                lambda: cipher_hmac.verify_signature(
                    data, 
                    cipher_hmac.sign_message(data, private_hmac), 
                    public_hmac
                ),
                iterations=100
            )
            
            # Ed25519
            private_ed, public_ed = cipher_ed25519.generate_keypair()
            result_ed = self.benchmark_operation(
                lambda: cipher_ed25519.verify_signature(
                    data,
                    cipher_ed25519.sign_message(data, private_ed),
                    public_ed
                ),
                iterations=100
            )
            
            overhead = (result_ed['mean'] / result_hmac['mean'] - 1) * 100
            print(f"{size_name:<10} {result_hmac['mean']:<15.3f} {result_ed['mean']:<15.3f} +{overhead:<9.1f}%")
        
        print(f"{'='*80}")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])  # -s para mostrar prints
