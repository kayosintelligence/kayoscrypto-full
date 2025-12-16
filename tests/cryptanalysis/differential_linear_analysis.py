#!/usr/bin/env python3
"""
KayosCrypto - Cryptanalysis Test Suite
Level 4 Security Validation

Tests:
1. Differential Cryptanalysis Resistance
2. Linear Cryptanalysis Resistance  
3. Timing Attack Resistance
4. Known Answer Tests (KAT)
5. Key Schedule Analysis

Author: KAYOS Intelligence LLC
Date: 2025-12-03
"""

import sys
import os
import time
import numpy as np
from typing import Dict, List, Tuple, Any
from collections import Counter
import hashlib
import json
from datetime import datetime

# Add path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'core'))

try:
    from kayoscrypto_ultimate import KayosCryptoUltimate
except ImportError:
    from kayoscrypto_final import KayosCryptoFinal as KayosCryptoUltimate


class DifferentialCryptanalysis:
    """
    Differential Cryptanalysis Resistance Test
    
    Measures resistance to attacks that exploit differences between plaintexts.
    A secure cipher should have no exploitable differential characteristics.
    """
    
    def __init__(self, cipher):
        self.cipher = cipher
        self.results = {}
    
    def hamming_distance(self, a: bytes, b: bytes) -> int:
        """Calculate Hamming distance between two byte sequences"""
        return sum(bin(x ^ y).count('1') for x, y in zip(a, b))
    
    def run_differential_test(self, num_samples: int = 10000) -> Dict:
        """
        Run differential cryptanalysis test.
        
        For each input difference Δx, measure output difference Δy.
        A secure cipher should have uniform distribution of Δy.
        """
        print("\n" + "="*60)
        print("DIFFERENTIAL CRYPTANALYSIS TEST")
        print("="*60)
        
        password = "TestKey-Differential-2025"
        block_size = 16  # 128 bits
        
        # Test different input differences
        input_differences = [
            bytes([0x01] + [0x00]*15),  # 1-bit difference
            bytes([0x80] + [0x00]*15),  # MSB difference
            bytes([0xFF] + [0x00]*15),  # Full byte difference
            bytes([0x01]*16),            # All bytes differ by 1
            bytes([0x55]*16),            # Alternating pattern
        ]
        
        results = {}
        
        for diff_idx, input_diff in enumerate(input_differences):
            diff_name = f"Δ{diff_idx+1}: {input_diff[:4].hex()}..."
            print(f"\nTesting {diff_name}")
            
            output_differences = []
            hamming_distances = []
            
            for _ in range(num_samples):
                # Generate random plaintext
                p1 = os.urandom(block_size)
                # Create P2 = P1 XOR Δx
                p2 = bytes(a ^ b for a, b in zip(p1, input_diff))
                
                # Encrypt both
                c1 = self.cipher.encrypt(p1, password, level=3)
                c2 = self.cipher.encrypt(p2, password, level=3)
                
                # Calculate output difference
                min_len = min(len(c1), len(c2))
                output_diff = bytes(a ^ b for a, b in zip(c1[:min_len], c2[:min_len]))
                
                # Track Hamming distance
                hd = self.hamming_distance(c1[:min_len], c2[:min_len])
                hamming_distances.append(hd)
                
                # Track output difference pattern
                output_differences.append(output_diff[:8].hex())
            
            # Analyze results
            unique_outputs = len(set(output_differences))
            avg_hamming = np.mean(hamming_distances)
            std_hamming = np.std(hamming_distances)
            
            # Expected Hamming for random: ~50% of bits
            expected_hamming = min_len * 8 * 0.5
            
            # Differential probability (should be very low for secure cipher)
            diff_counter = Counter(output_differences)
            max_prob = diff_counter.most_common(1)[0][1] / num_samples
            
            results[diff_name] = {
                "unique_outputs": unique_outputs,
                "max_probability": max_prob,
                "avg_hamming_distance": avg_hamming,
                "std_hamming": std_hamming,
                "expected_hamming": expected_hamming,
                "hamming_deviation": abs(avg_hamming - expected_hamming) / expected_hamming * 100
            }
            
            # Security criterion: max probability should be close to 1/2^n
            # For 64-bit output prefix, random would be ~1/num_samples
            expected_prob = 1 / num_samples
            is_secure = max_prob < 0.01  # Less than 1% concentration
            
            print(f"  Unique outputs: {unique_outputs}/{num_samples}")
            print(f"  Max differential probability: {max_prob:.6f}")
            print(f"  Avg Hamming distance: {avg_hamming:.2f} (expected: {expected_hamming:.2f})")
            print(f"  Status: {'✅ SECURE' if is_secure else '⚠️ WEAK'}")
            
            results[diff_name]["secure"] = is_secure
        
        # Overall assessment
        all_secure = all(r["secure"] for r in results.values())
        avg_max_prob = np.mean([r["max_probability"] for r in results.values()])
        
        self.results = {
            "test": "Differential Cryptanalysis",
            "samples_per_difference": num_samples,
            "total_samples": num_samples * len(input_differences),
            "differences_tested": len(input_differences),
            "detailed_results": results,
            "overall_max_probability": avg_max_prob,
            "all_secure": all_secure,
            "status": "PASSED" if all_secure else "FAILED"
        }
        
        print(f"\n{'='*60}")
        print(f"DIFFERENTIAL CRYPTANALYSIS: {self.results['status']}")
        print(f"Overall max differential probability: {avg_max_prob:.6f}")
        print(f"{'='*60}")
        
        return self.results


class LinearCryptanalysis:
    """
    Linear Cryptanalysis Resistance Test
    
    Measures resistance to attacks that exploit linear approximations.
    A secure cipher should have no significant linear biases.
    """
    
    def __init__(self, cipher):
        self.cipher = cipher
        self.results = {}
    
    def parity(self, data: bytes, mask: bytes) -> int:
        """Calculate parity of masked bits"""
        result = 0
        for d, m in zip(data, mask):
            result ^= bin(d & m).count('1') % 2
        return result
    
    def run_linear_test(self, num_samples: int = 50000) -> Dict:
        """
        Run linear cryptanalysis test.
        
        For linear masks α (input) and β (output), measure:
        bias = |Pr[α·P ⊕ β·C = 0] - 0.5|
        
        A secure cipher should have bias close to 0.
        """
        print("\n" + "="*60)
        print("LINEAR CRYPTANALYSIS TEST")
        print("="*60)
        
        password = "TestKey-Linear-2025"
        block_size = 16
        
        # Test different linear masks
        linear_masks = [
            (bytes([0x01] + [0x00]*15), bytes([0x01] + [0x00]*15)),  # Single bit
            (bytes([0x80] + [0x00]*15), bytes([0x80] + [0x00]*15)),  # MSB
            (bytes([0xFF] + [0x00]*15), bytes([0xFF] + [0x00]*15)),  # Full byte
            (bytes([0x55]*16), bytes([0x55]*16)),                    # Alternating
            (bytes([0xAA]*16), bytes([0xAA]*16)),                    # Alternating inverse
            (bytes([0x0F]*16), bytes([0xF0]*16)),                    # Cross-nibble
        ]
        
        results = {}
        
        for mask_idx, (alpha, beta) in enumerate(linear_masks):
            mask_name = f"Mask{mask_idx+1}: α={alpha[:2].hex()}, β={beta[:2].hex()}"
            print(f"\nTesting {mask_name}")
            
            matches = 0
            
            for _ in range(num_samples):
                # Generate random plaintext
                plaintext = os.urandom(block_size)
                
                # Encrypt
                ciphertext = self.cipher.encrypt(plaintext, password, level=3)
                
                # Calculate parities
                input_parity = self.parity(plaintext, alpha)
                output_parity = self.parity(ciphertext[:block_size], beta)
                
                # Check if linear relation holds
                if input_parity == output_parity:
                    matches += 1
            
            # Calculate bias
            probability = matches / num_samples
            bias = abs(probability - 0.5)
            
            # Security criterion: bias should be < 2^-(n/2) for n-bit block
            # For 128-bit block, max acceptable bias ≈ 2^-64 ≈ 5.4e-20
            # Practical threshold: bias < 0.01 (1%)
            is_secure = bias < 0.01
            
            results[mask_name] = {
                "probability": probability,
                "bias": bias,
                "matches": matches,
                "samples": num_samples,
                "secure": is_secure
            }
            
            print(f"  Pr[α·P ⊕ β·C = 0] = {probability:.6f}")
            print(f"  Bias: {bias:.6f}")
            print(f"  Status: {'✅ SECURE' if is_secure else '⚠️ WEAK'}")
        
        # Overall assessment
        all_secure = all(r["secure"] for r in results.values())
        max_bias = max(r["bias"] for r in results.values())
        avg_bias = np.mean([r["bias"] for r in results.values()])
        
        self.results = {
            "test": "Linear Cryptanalysis",
            "samples_per_mask": num_samples,
            "total_samples": num_samples * len(linear_masks),
            "masks_tested": len(linear_masks),
            "detailed_results": results,
            "max_bias": max_bias,
            "avg_bias": avg_bias,
            "all_secure": all_secure,
            "status": "PASSED" if all_secure else "FAILED"
        }
        
        print(f"\n{'='*60}")
        print(f"LINEAR CRYPTANALYSIS: {self.results['status']}")
        print(f"Maximum bias: {max_bias:.6f}")
        print(f"Average bias: {avg_bias:.6f}")
        print(f"{'='*60}")
        
        return self.results


class TimingAttackResistance:
    """
    Timing Attack Resistance Test
    
    Measures if encryption time varies based on input data.
    A secure implementation should have constant-time operations.
    """
    
    def __init__(self, cipher):
        self.cipher = cipher
        self.results = {}
    
    def run_timing_test(self, num_samples: int = 1000) -> Dict:
        """
        Run timing attack resistance test.
        
        Measure encryption time for different input patterns.
        Variation should be minimal and not correlated with input.
        """
        print("\n" + "="*60)
        print("TIMING ATTACK RESISTANCE TEST")
        print("="*60)
        
        password = "TestKey-Timing-2025"
        block_size = 64  # Larger block for measurable timing
        
        # Different input patterns that might trigger timing variations
        test_patterns = {
            "zeros": bytes([0x00] * block_size),
            "ones": bytes([0xFF] * block_size),
            "alternating": bytes([0x55] * block_size),
            "random1": os.urandom(block_size),
            "random2": os.urandom(block_size),
            "sparse": bytes([0x01] + [0x00] * (block_size-1)),
            "dense": bytes([0xFE] + [0xFF] * (block_size-1)),
        }
        
        timing_results = {}
        
        for pattern_name, data in test_patterns.items():
            times = []
            
            for _ in range(num_samples):
                start = time.perf_counter_ns()
                _ = self.cipher.encrypt(data, password, level=3)
                end = time.perf_counter_ns()
                times.append(end - start)
            
            timing_results[pattern_name] = {
                "mean_ns": np.mean(times),
                "std_ns": np.std(times),
                "min_ns": np.min(times),
                "max_ns": np.max(times),
                "cv": np.std(times) / np.mean(times) * 100  # Coefficient of variation
            }
            
            print(f"  {pattern_name}: {np.mean(times)/1e6:.3f}ms ± {np.std(times)/1e6:.3f}ms")
        
        # Analyze timing consistency
        all_means = [r["mean_ns"] for r in timing_results.values()]
        overall_mean = np.mean(all_means)
        max_deviation = max(abs(m - overall_mean) for m in all_means)
        max_deviation_pct = max_deviation / overall_mean * 100
        
        # Security criterion: max deviation < 5%
        is_secure = max_deviation_pct < 5.0
        
        # Check for correlation with Hamming weight
        hamming_weights = [sum(bin(b).count('1') for b in data) for data in test_patterns.values()]
        correlation = np.corrcoef(hamming_weights, all_means)[0, 1]
        
        self.results = {
            "test": "Timing Attack Resistance",
            "samples_per_pattern": num_samples,
            "patterns_tested": len(test_patterns),
            "detailed_results": timing_results,
            "overall_mean_ns": overall_mean,
            "max_deviation_pct": max_deviation_pct,
            "hamming_correlation": correlation if not np.isnan(correlation) else 0,
            "is_constant_time": is_secure,
            "status": "PASSED" if is_secure else "FAILED"
        }
        
        print(f"\n{'='*60}")
        print(f"TIMING ATTACK RESISTANCE: {self.results['status']}")
        print(f"Max timing deviation: {max_deviation_pct:.2f}%")
        print(f"Hamming weight correlation: {self.results['hamming_correlation']:.4f}")
        print(f"{'='*60}")
        
        return self.results


class KeyScheduleAnalysis:
    """
    Key Schedule Analysis
    
    Analyzes the key derivation function for weaknesses.
    Tests for related-key attacks and key sensitivity.
    """
    
    def __init__(self, cipher):
        self.cipher = cipher
        self.results = {}
    
    def run_key_schedule_test(self, num_samples: int = 1000) -> Dict:
        """
        Run key schedule analysis.
        
        Tests:
        1. Related key sensitivity
        2. Key bit sensitivity
        3. Key collision resistance
        """
        print("\n" + "="*60)
        print("KEY SCHEDULE ANALYSIS")
        print("="*60)
        
        block_size = 32
        plaintext = b"KayosCrypto Key Schedule Test!!"  # Fixed plaintext
        
        # Test 1: Related Key Sensitivity
        print("\n1. Related Key Sensitivity Test")
        base_key = "BaseKey-2025-Secure"
        related_keys = [
            "BaseKey-2025-Secure",   # Same key
            "BaseKey-2025-Securf",   # 1-bit difference
            "BaseKey-2025-Secvre",   # 1-bit difference elsewhere
            "basekey-2025-secure",   # Case change
            "BaseKey-2025-Secure ",  # Trailing space
        ]
        
        ciphertexts = []
        for key in related_keys:
            ct = self.cipher.encrypt(plaintext, key, level=3)
            ciphertexts.append(ct)
        
        # Calculate distances between related key outputs
        related_key_distances = []
        for i in range(1, len(ciphertexts)):
            min_len = min(len(ciphertexts[0]), len(ciphertexts[i]))
            dist = sum(bin(a ^ b).count('1') for a, b in zip(ciphertexts[0][:min_len], ciphertexts[i][:min_len]))
            dist_pct = dist / (min_len * 8) * 100
            related_key_distances.append(dist_pct)
            print(f"  Key variation {i}: {dist_pct:.2f}% bit difference in output")
        
        # Test 2: Key Bit Sensitivity
        print("\n2. Key Bit Sensitivity Test")
        base_key_bytes = b"0123456789ABCDEF"
        bit_sensitivities = []
        
        base_ct = self.cipher.encrypt(plaintext, base_key_bytes.decode(), level=3)
        
        for byte_idx in range(min(8, len(base_key_bytes))):
            for bit_idx in range(8):
                # Flip single bit
                modified_key = bytearray(base_key_bytes)
                modified_key[byte_idx] ^= (1 << bit_idx)
                
                mod_ct = self.cipher.encrypt(plaintext, bytes(modified_key).decode(errors='replace'), level=3)
                
                min_len = min(len(base_ct), len(mod_ct))
                dist = sum(bin(a ^ b).count('1') for a, b in zip(base_ct[:min_len], mod_ct[:min_len]))
                dist_pct = dist / (min_len * 8) * 100
                bit_sensitivities.append(dist_pct)
        
        avg_bit_sensitivity = np.mean(bit_sensitivities)
        min_bit_sensitivity = np.min(bit_sensitivities)
        print(f"  Average bit sensitivity: {avg_bit_sensitivity:.2f}%")
        print(f"  Minimum bit sensitivity: {min_bit_sensitivity:.2f}%")
        
        # Test 3: Key Collision Resistance
        print("\n3. Key Collision Resistance Test")
        random_keys = [os.urandom(16).hex() for _ in range(num_samples)]
        ciphertext_hashes = set()
        
        for key in random_keys:
            ct = self.cipher.encrypt(plaintext, key, level=3)
            ct_hash = hashlib.sha256(ct).hexdigest()
            ciphertext_hashes.add(ct_hash)
        
        collision_rate = 1 - len(ciphertext_hashes) / num_samples
        print(f"  Unique ciphertexts: {len(ciphertext_hashes)}/{num_samples}")
        print(f"  Collision rate: {collision_rate:.6f}")
        
        # Security assessment
        related_key_secure = all(d > 40 for d in related_key_distances[1:])  # >40% for different keys
        bit_sensitivity_secure = min_bit_sensitivity > 30  # >30% for single bit flip
        collision_secure = collision_rate < 0.001  # <0.1% collision rate
        
        all_secure = related_key_secure and bit_sensitivity_secure and collision_secure
        
        self.results = {
            "test": "Key Schedule Analysis",
            "related_key_distances": related_key_distances,
            "avg_bit_sensitivity": avg_bit_sensitivity,
            "min_bit_sensitivity": min_bit_sensitivity,
            "collision_rate": collision_rate,
            "unique_ciphertexts": len(ciphertext_hashes),
            "samples": num_samples,
            "related_key_secure": related_key_secure,
            "bit_sensitivity_secure": bit_sensitivity_secure,
            "collision_secure": collision_secure,
            "status": "PASSED" if all_secure else "FAILED"
        }
        
        print(f"\n{'='*60}")
        print(f"KEY SCHEDULE ANALYSIS: {self.results['status']}")
        print(f"{'='*60}")
        
        return self.results


class KnownAnswerTests:
    """
    Known Answer Tests (KAT)
    
    Creates reproducible test vectors for validation.
    """
    
    def __init__(self, cipher):
        self.cipher = cipher
        self.results = {}
    
    def run_kat(self) -> Dict:
        """
        Run Known Answer Tests.
        
        Generates test vectors and verifies reproducibility.
        """
        print("\n" + "="*60)
        print("KNOWN ANSWER TESTS (KAT)")
        print("="*60)
        
        test_vectors = [
            {
                "name": "KAT-1: Empty input",
                "plaintext": b"",
                "password": "TestPassword123",
                "level": 3
            },
            {
                "name": "KAT-2: Single byte",
                "plaintext": b"A",
                "password": "TestPassword123",
                "level": 3
            },
            {
                "name": "KAT-3: 16 bytes",
                "plaintext": b"0123456789ABCDEF",
                "password": "TestPassword123",
                "level": 3
            },
            {
                "name": "KAT-4: 64 bytes",
                "plaintext": b"0123456789ABCDEF" * 4,
                "password": "TestPassword123",
                "level": 3
            },
            {
                "name": "KAT-5: Special characters",
                "plaintext": "Olá Mundo! 你好世界! مرحبا بالعالم".encode('utf-8'),
                "password": "Spëcïàl_Kéy_2025!",
                "level": 3
            },
            {
                "name": "KAT-6: Binary data",
                "plaintext": bytes(range(256)),
                "password": "BinaryKey",
                "level": 3
            },
        ]
        
        kat_results = []
        all_reproducible = True
        
        for tv in test_vectors:
            print(f"\n{tv['name']}")
            
            # Encrypt multiple times
            ciphertexts = []
            for _ in range(5):
                ct = self.cipher.encrypt(tv['plaintext'], tv['password'], tv['level'])
                ciphertexts.append(ct)
            
            # Check reproducibility (deterministic encryption)
            reproducible = len(set(ct.hex() for ct in ciphertexts)) == 1
            
            # Verify decryption
            decrypted = self.cipher.decrypt(ciphertexts[0], tv['password'], tv['level'])
            reversible = decrypted == tv['plaintext']
            
            result = {
                "name": tv['name'],
                "plaintext_len": len(tv['plaintext']),
                "ciphertext_len": len(ciphertexts[0]),
                "ciphertext_hex": ciphertexts[0][:32].hex() + ("..." if len(ciphertexts[0]) > 32 else ""),
                "reproducible": reproducible,
                "reversible": reversible,
                "passed": reproducible and reversible
            }
            
            kat_results.append(result)
            all_reproducible = all_reproducible and result["passed"]
            
            print(f"  Plaintext: {len(tv['plaintext'])} bytes")
            print(f"  Ciphertext: {len(ciphertexts[0])} bytes")
            print(f"  Reproducible: {'✅' if reproducible else '❌'}")
            print(f"  Reversible: {'✅' if reversible else '❌'}")
        
        self.results = {
            "test": "Known Answer Tests",
            "vectors": kat_results,
            "all_passed": all_reproducible,
            "status": "PASSED" if all_reproducible else "FAILED"
        }
        
        print(f"\n{'='*60}")
        print(f"KNOWN ANSWER TESTS: {self.results['status']}")
        print(f"{'='*60}")
        
        return self.results


def run_full_cryptanalysis_suite():
    """Run complete cryptanalysis test suite"""
    
    print("\n" + "="*70)
    print("   KAYOSCRYPTO LEVEL 4 CRYPTANALYSIS TEST SUITE")
    print("   Date: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*70)
    
    # Initialize cipher
    cipher = KayosCryptoUltimate(use_concentric=True, use_direction=True)
    
    # Run all tests
    results = {}
    
    # 1. Differential Cryptanalysis
    diff_test = DifferentialCryptanalysis(cipher)
    results["differential"] = diff_test.run_differential_test(num_samples=5000)
    
    # 2. Linear Cryptanalysis
    linear_test = LinearCryptanalysis(cipher)
    results["linear"] = linear_test.run_linear_test(num_samples=20000)
    
    # 3. Timing Attack Resistance
    timing_test = TimingAttackResistance(cipher)
    results["timing"] = timing_test.run_timing_test(num_samples=500)
    
    # 4. Key Schedule Analysis
    key_test = KeyScheduleAnalysis(cipher)
    results["key_schedule"] = key_test.run_key_schedule_test(num_samples=500)
    
    # 5. Known Answer Tests
    kat_test = KnownAnswerTests(cipher)
    results["kat"] = kat_test.run_kat()
    
    # Final Summary
    print("\n" + "="*70)
    print("   FINAL SUMMARY - LEVEL 4 CRYPTANALYSIS")
    print("="*70)
    
    all_passed = True
    summary_table = []
    
    for test_name, result in results.items():
        status = result.get("status", "UNKNOWN")
        passed = status == "PASSED"
        all_passed = all_passed and passed
        summary_table.append((test_name.upper(), status, "✅" if passed else "❌"))
    
    print(f"\n{'Test':<25} {'Status':<12} {'Result':<8}")
    print("-" * 45)
    for name, status, icon in summary_table:
        print(f"{name:<25} {status:<12} {icon:<8}")
    
    print("-" * 45)
    overall = "PASSED" if all_passed else "FAILED"
    print(f"{'OVERALL':<25} {overall:<12} {'✅' if all_passed else '❌':<8}")
    
    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "version": "v5.0.1 ULTIMATE",
        "tests": results,
        "overall_status": overall,
        "all_passed": all_passed
    }
    
    output_path = os.path.join(os.path.dirname(__file__), '..', '..', 
                               'kayosid_storage', 'cryptanalysis_results_20251203.json')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\n📄 Results saved to: {output_path}")
    
    return output


if __name__ == "__main__":
    results = run_full_cryptanalysis_suite()
    
    # Exit code based on results
    sys.exit(0 if results["all_passed"] else 1)
