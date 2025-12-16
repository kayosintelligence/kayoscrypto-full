#!/usr/bin/env python3
"""
KayosCrypto - Fault Simulation Tests
Simulates software-level fault injection attacks

IMPORTANT: These are SOFTWARE SIMULATIONS, not real hardware attacks.
Real fault injection requires specialized hardware (laser, voltage glitch).

Tests:
1. Bit Flip Fault Simulation
2. Byte Skip Fault Simulation  
3. Instruction Skip Simulation
4. Random Fault Injection
5. Differential Fault Analysis (DFA) Simulation

Author: KAYOS Intelligence LLC
Date: 2025-12-03
"""

import sys
import os
import numpy as np
from typing import Dict, List, Tuple, Any
import hashlib
import json
from datetime import datetime
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'core'))

try:
    from kayoscrypto_ultimate import KayosCryptoUltimate
except ImportError:
    from kayoscrypto_final import KayosCryptoFinal as KayosCryptoUltimate


class FaultSimulator:
    """
    Simulates various fault injection attacks in software.
    
    NOTE: Real fault injection attacks require hardware.
    This simulates the EFFECT of faults to test cipher resilience.
    """
    
    def __init__(self, cipher):
        self.cipher = cipher
        self.results = {}
    
    def inject_bit_flip(self, data: bytes, position: int, bit: int) -> bytes:
        """Simulate single bit flip fault"""
        data = bytearray(data)
        if position < len(data):
            data[position] ^= (1 << bit)
        return bytes(data)
    
    def inject_byte_zero(self, data: bytes, position: int) -> bytes:
        """Simulate byte zeroing fault"""
        data = bytearray(data)
        if position < len(data):
            data[position] = 0x00
        return bytes(data)
    
    def inject_random_faults(self, data: bytes, num_faults: int) -> bytes:
        """Inject multiple random faults"""
        data = bytearray(data)
        for _ in range(num_faults):
            if len(data) > 0:
                pos = random.randint(0, len(data) - 1)
                data[pos] ^= random.randint(1, 255)
        return bytes(data)


class BitFlipFaultTest:
    """
    Test 1: Bit Flip Fault Simulation
    
    Simulates what happens when an attacker flips bits during encryption.
    A secure cipher should either:
    - Detect the fault and fail safely, OR
    - Produce completely different output (no partial information leak)
    """
    
    def __init__(self, cipher):
        self.cipher = cipher
        self.simulator = FaultSimulator(cipher)
    
    def run_test(self, num_samples: int = 100) -> Dict:
        print("\n" + "="*60)
        print("BIT FLIP FAULT SIMULATION TEST")
        print("="*60)
        
        password = "FaultTest-Key-2025"
        plaintext = b"KayosCrypto Fault Injection Test Data - 32 bytes!!"[:32]
        
        # Get correct ciphertext
        correct_ct = self.cipher.encrypt(plaintext, password, level=3)
        
        fault_results = []
        information_leaks = 0
        
        for byte_pos in range(min(16, len(plaintext))):
            for bit_pos in range(8):
                # Inject fault into plaintext
                faulted_pt = self.simulator.inject_bit_flip(plaintext, byte_pos, bit_pos)
                
                # Encrypt faulted plaintext
                faulted_ct = self.cipher.encrypt(faulted_pt, password, level=3)
                
                # Analyze difference
                min_len = min(len(correct_ct), len(faulted_ct))
                diff_bits = sum(bin(a ^ b).count('1') for a, b in zip(correct_ct[:min_len], faulted_ct[:min_len]))
                diff_pct = diff_bits / (min_len * 8) * 100
                
                # Check for information leak (low diffusion = potential leak)
                if diff_pct < 30:  # Less than 30% difference is suspicious
                    information_leaks += 1
                
                fault_results.append({
                    "byte": byte_pos,
                    "bit": bit_pos,
                    "diff_pct": diff_pct
                })
        
        avg_diff = np.mean([r["diff_pct"] for r in fault_results])
        min_diff = np.min([r["diff_pct"] for r in fault_results])
        
        # Security criterion: average diffusion should be ~50%, minimum > 30%
        is_secure = min_diff > 30 and avg_diff > 45
        
        result = {
            "test": "Bit Flip Fault Simulation",
            "faults_injected": len(fault_results),
            "avg_diffusion": avg_diff,
            "min_diffusion": min_diff,
            "information_leaks": information_leaks,
            "secure": is_secure,
            "status": "PASSED" if is_secure else "FAILED"
        }
        
        print(f"  Faults injected: {len(fault_results)}")
        print(f"  Average diffusion: {avg_diff:.2f}%")
        print(f"  Minimum diffusion: {min_diff:.2f}%")
        print(f"  Information leaks detected: {information_leaks}")
        print(f"  Status: {'✅ SECURE' if is_secure else '⚠️ VULNERABLE'}")
        
        return result


class DifferentialFaultAnalysis:
    """
    Test 2: Differential Fault Analysis (DFA) Simulation
    
    DFA compares correct and faulted ciphertexts to extract key information.
    A secure cipher should not leak key bits through fault comparison.
    """
    
    def __init__(self, cipher):
        self.cipher = cipher
        self.simulator = FaultSimulator(cipher)
    
    def run_test(self, num_samples: int = 500) -> Dict:
        print("\n" + "="*60)
        print("DIFFERENTIAL FAULT ANALYSIS (DFA) SIMULATION")
        print("="*60)
        
        password = "DFA-Test-Key-2025"
        
        dfa_results = []
        key_bits_leaked = 0
        
        for _ in range(num_samples):
            plaintext = os.urandom(32)
            
            # Correct encryption
            correct_ct = self.cipher.encrypt(plaintext, password, level=3)
            
            # Inject fault at random position
            fault_pos = random.randint(0, len(plaintext) - 1)
            fault_bit = random.randint(0, 7)
            faulted_pt = self.simulator.inject_bit_flip(plaintext, fault_pos, fault_bit)
            
            # Faulted encryption
            faulted_ct = self.cipher.encrypt(faulted_pt, password, level=3)
            
            # DFA analysis: XOR of correct and faulted ciphertext
            min_len = min(len(correct_ct), len(faulted_ct))
            xor_diff = bytes(a ^ b for a, b in zip(correct_ct[:min_len], faulted_ct[:min_len]))
            
            # Check for patterns that might leak key information
            # In a secure cipher, XOR should be random-looking
            zero_bytes = xor_diff.count(0)
            
            # If many bytes are zero, fault didn't propagate well (potential leak)
            if zero_bytes > min_len * 0.1:  # More than 10% zeros
                key_bits_leaked += 1
            
            dfa_results.append({
                "zero_bytes": zero_bytes,
                "total_bytes": min_len
            })
        
        avg_zero_ratio = np.mean([r["zero_bytes"] / r["total_bytes"] for r in dfa_results])
        leak_rate = key_bits_leaked / num_samples
        
        # Security criterion: leak rate should be very low
        is_secure = leak_rate < 0.05  # Less than 5% potential leaks
        
        result = {
            "test": "Differential Fault Analysis Simulation",
            "samples": num_samples,
            "avg_zero_ratio": avg_zero_ratio,
            "potential_leaks": key_bits_leaked,
            "leak_rate": leak_rate,
            "secure": is_secure,
            "status": "PASSED" if is_secure else "FAILED"
        }
        
        print(f"  Samples analyzed: {num_samples}")
        print(f"  Average zero ratio: {avg_zero_ratio:.4f}")
        print(f"  Potential key leaks: {key_bits_leaked} ({leak_rate*100:.2f}%)")
        print(f"  Status: {'✅ SECURE' if is_secure else '⚠️ VULNERABLE'}")
        
        return result


class FaultPropagationTest:
    """
    Test 3: Fault Propagation Analysis
    
    Tests how faults propagate through the cipher.
    Good ciphers have complete fault propagation (avalanche under faults).
    """
    
    def __init__(self, cipher):
        self.cipher = cipher
        self.simulator = FaultSimulator(cipher)
    
    def run_test(self, num_samples: int = 200) -> Dict:
        print("\n" + "="*60)
        print("FAULT PROPAGATION ANALYSIS")
        print("="*60)
        
        password = "Propagation-Test-2025"
        
        propagation_scores = []
        
        for _ in range(num_samples):
            plaintext = os.urandom(64)
            
            # Normal encryption
            normal_ct = self.cipher.encrypt(plaintext, password, level=3)
            
            # Inject progressive number of faults
            for num_faults in [1, 2, 4, 8]:
                faulted_pt = self.simulator.inject_random_faults(plaintext, num_faults)
                faulted_ct = self.cipher.encrypt(faulted_pt, password, level=3)
                
                # Measure propagation
                min_len = min(len(normal_ct), len(faulted_ct))
                diff_bits = sum(bin(a ^ b).count('1') for a, b in zip(normal_ct[:min_len], faulted_ct[:min_len]))
                propagation = diff_bits / (min_len * 8) * 100
                
                propagation_scores.append({
                    "num_faults": num_faults,
                    "propagation": propagation
                })
        
        # Analyze by fault count
        by_fault_count = {}
        for score in propagation_scores:
            nf = score["num_faults"]
            if nf not in by_fault_count:
                by_fault_count[nf] = []
            by_fault_count[nf].append(score["propagation"])
        
        print("\n  Propagation by fault count:")
        all_good = True
        for nf in sorted(by_fault_count.keys()):
            avg = np.mean(by_fault_count[nf])
            print(f"    {nf} fault(s): {avg:.2f}% average propagation")
            if avg < 40:  # Should be at least 40% propagation
                all_good = False
        
        overall_avg = np.mean([s["propagation"] for s in propagation_scores])
        is_secure = overall_avg > 45 and all_good
        
        result = {
            "test": "Fault Propagation Analysis",
            "samples": num_samples * 4,  # 4 fault levels
            "overall_propagation": overall_avg,
            "by_fault_count": {k: np.mean(v) for k, v in by_fault_count.items()},
            "secure": is_secure,
            "status": "PASSED" if is_secure else "FAILED"
        }
        
        print(f"\n  Overall propagation: {overall_avg:.2f}%")
        print(f"  Status: {'✅ SECURE' if is_secure else '⚠️ VULNERABLE'}")
        
        return result


class SafeFailureTest:
    """
    Test 4: Safe Failure Behavior
    
    Tests if the cipher fails safely when given corrupted/faulted data.
    Should either decrypt to garbage OR raise an error (no partial reveal).
    """
    
    def __init__(self, cipher):
        self.cipher = cipher
        self.simulator = FaultSimulator(cipher)
    
    def run_test(self, num_samples: int = 100) -> Dict:
        print("\n" + "="*60)
        print("SAFE FAILURE BEHAVIOR TEST")
        print("="*60)
        
        password = "SafeFail-Test-2025"
        
        safe_failures = 0
        partial_reveals = 0
        total_tests = 0
        
        for _ in range(num_samples):
            plaintext = os.urandom(64)
            
            # Normal encrypt
            ciphertext = self.cipher.encrypt(plaintext, password, level=3)
            
            # Inject faults into ciphertext
            for num_faults in [1, 4, 16]:
                faulted_ct = self.simulator.inject_random_faults(ciphertext, num_faults)
                
                try:
                    # Try to decrypt faulted ciphertext
                    decrypted = self.cipher.decrypt(faulted_ct, password, level=3)
                    
                    # Check if decryption reveals partial plaintext
                    if decrypted == plaintext:
                        # Shouldn't happen with faults
                        partial_reveals += 1
                    else:
                        # Different output = safe (garbage out)
                        # Check similarity
                        min_len = min(len(plaintext), len(decrypted))
                        if min_len > 0:
                            similarity = sum(1 for a, b in zip(plaintext[:min_len], decrypted[:min_len]) if a == b) / min_len
                            if similarity > 0.5:  # More than 50% similar = potential leak
                                partial_reveals += 1
                            else:
                                safe_failures += 1
                        else:
                            safe_failures += 1
                
                except Exception as e:
                    # Exception on faulted data = safe failure
                    safe_failures += 1
                
                total_tests += 1
        
        safe_rate = safe_failures / total_tests
        is_secure = safe_rate > 0.95  # 95%+ should fail safely
        
        result = {
            "test": "Safe Failure Behavior",
            "total_tests": total_tests,
            "safe_failures": safe_failures,
            "partial_reveals": partial_reveals,
            "safe_rate": safe_rate,
            "secure": is_secure,
            "status": "PASSED" if is_secure else "FAILED"
        }
        
        print(f"  Total tests: {total_tests}")
        print(f"  Safe failures: {safe_failures} ({safe_rate*100:.2f}%)")
        print(f"  Partial reveals: {partial_reveals}")
        print(f"  Status: {'✅ SECURE' if is_secure else '⚠️ VULNERABLE'}")
        
        return result


class PowerAnalysisSimulation:
    """
    Test 5: Power Analysis Simulation (Hamming Weight Model)
    
    NOTE: Real power analysis requires hardware!
    This simulates using Hamming weight as a proxy for power consumption.
    """
    
    def __init__(self, cipher):
        self.cipher = cipher
    
    def hamming_weight(self, data: bytes) -> int:
        """Calculate Hamming weight (number of 1 bits)"""
        return sum(bin(b).count('1') for b in data)
    
    def run_test(self, num_samples: int = 1000) -> Dict:
        print("\n" + "="*60)
        print("POWER ANALYSIS SIMULATION (Hamming Weight Model)")
        print("="*60)
        print("  ⚠️  NOTE: This is a SOFTWARE SIMULATION")
        print("  ⚠️  Real power analysis requires oscilloscope + current probe")
        
        password = "PowerSim-Test-2025"
        
        # Collect Hamming weight correlation data
        correlations = []
        
        for _ in range(num_samples):
            plaintext = os.urandom(16)
            ciphertext = self.cipher.encrypt(plaintext, password, level=3)
            
            pt_hw = self.hamming_weight(plaintext)
            ct_hw = self.hamming_weight(ciphertext[:16])
            
            correlations.append((pt_hw, ct_hw))
        
        # Calculate correlation coefficient
        pt_weights = [c[0] for c in correlations]
        ct_weights = [c[1] for c in correlations]
        
        correlation = np.corrcoef(pt_weights, ct_weights)[0, 1]
        
        # In a secure cipher, there should be NO correlation
        # between input Hamming weight and output Hamming weight
        is_secure = abs(correlation) < 0.1  # Less than 10% correlation
        
        result = {
            "test": "Power Analysis Simulation (Hamming Weight)",
            "samples": num_samples,
            "hw_correlation": correlation,
            "correlation_threshold": 0.1,
            "note": "SOFTWARE SIMULATION - not real power analysis",
            "secure": is_secure,
            "status": "PASSED" if is_secure else "FAILED"
        }
        
        print(f"\n  Samples: {num_samples}")
        print(f"  Hamming weight correlation: {correlation:.4f}")
        print(f"  Threshold: < 0.1 (no correlation)")
        print(f"  Status: {'✅ SECURE (simulated)' if is_secure else '⚠️ POTENTIAL LEAK'}")
        
        return result


def run_fault_simulation_suite():
    """Run complete fault simulation test suite"""
    
    print("\n" + "="*70)
    print("   KAYOSCRYPTO FAULT SIMULATION TEST SUITE")
    print("   Date: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*70)
    print("\n⚠️  IMPORTANT: These are SOFTWARE SIMULATIONS")
    print("⚠️  Real fault injection attacks require specialized hardware:")
    print("    - Laser fault injection: $10,000-100,000")
    print("    - Voltage glitcher: $500-5,000")
    print("    - Power analysis: oscilloscope + current probe")
    print("="*70)
    
    # Initialize cipher
    cipher = KayosCryptoUltimate(use_concentric=True, use_direction=True)
    
    results = {}
    
    # Run all fault simulation tests
    tests = [
        ("bit_flip", BitFlipFaultTest(cipher)),
        ("dfa", DifferentialFaultAnalysis(cipher)),
        ("propagation", FaultPropagationTest(cipher)),
        ("safe_failure", SafeFailureTest(cipher)),
        ("power_simulation", PowerAnalysisSimulation(cipher)),
    ]
    
    for name, test in tests:
        results[name] = test.run_test()
    
    # Final Summary
    print("\n" + "="*70)
    print("   FAULT SIMULATION SUMMARY")
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
    print(f"{'OVERALL (Simulated)':<25} {overall:<12} {'✅' if all_passed else '❌':<8}")
    
    print("\n" + "="*70)
    print("REMINDER: Real hardware testing still recommended for certification")
    print("="*70)
    
    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "version": "v5.0.1 ULTIMATE",
        "type": "SIMULATION (not hardware)",
        "tests": results,
        "overall_status": overall,
        "all_passed": all_passed,
        "disclaimer": "These are software simulations. Real fault injection requires specialized hardware."
    }
    
    output_path = os.path.join(os.path.dirname(__file__), '..', '..', 
                               'kayosid_storage', 'fault_simulation_results_20251203.json')
    
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\n📄 Results saved to: {output_path}")
    
    return output


if __name__ == "__main__":
    results = run_fault_simulation_suite()
    sys.exit(0 if results["all_passed"] else 1)
