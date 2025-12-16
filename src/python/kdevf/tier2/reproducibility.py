"""Reproducibility tests for KDEVF Tier 2."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import hashlib
from typing import Callable, Dict, List, Tuple


@dataclass
class ReproducibilityResult:
    """Outcome of a reproducibility test run."""

    test_id: str
    timestamp: datetime
    seed: bytes
    iterations: int
    match_rate: float
    passed: bool
    hash_original: str
    hash_reproduced: str
    evidence: List[str] = field(default_factory=list)


class ReproducibilityTest:
    """Validate that identical seeds always yield identical outputs."""

    def __init__(self, trng_callable: Callable[[bytes, int], bytes]) -> None:
        self.trng = trng_callable
        self.results: List[ReproducibilityResult] = []

    def execute(
        self,
        seed: bytes,
        output_length: int = 1024 * 1024,
        iterations: int = 100,
    ) -> ReproducibilityResult:
        evidence: List[str] = []
        print(f"Running reference stream for seed {seed.hex()[:16]}…")
        reference_output = self.trng(seed, output_length)
        reference_hash = hashlib.sha256(reference_output).hexdigest()
        evidence.append(f"Reference output length: {output_length} bytes")
        evidence.append(f"Reference SHA-256: {reference_hash}")

        matches = 0
        mismatches: List[Dict[str, object]] = []

        for i in range(iterations):
            reproduced_output = self.trng(seed, output_length)
            reproduced_hash = hashlib.sha256(reproduced_output).hexdigest()
            if reproduced_output == reference_output:
                matches += 1
            else:
                mismatches.append(
                    {
                        "iteration": i,
                        "hash": reproduced_hash,
                        "first_diff_byte": self._find_first_diff(reference_output, reproduced_output),
                    }
                )
            if (i + 1) % 10 == 0:
                print(f"  Iterations {i + 1}/{iterations}: {matches} matches")

        match_rate = matches / iterations
        passed = match_rate == 1.0
        evidence.append(f"Total iterations: {iterations}")
        evidence.append(f"Perfect matches: {matches}")
        evidence.append(f"Match rate: {match_rate * 100:.2f}%")

        if mismatches:
            evidence.append(f"WARNING: {len(mismatches)} mismatches detected")
            for mm in mismatches[:5]:
                evidence.append(
                    f"  - Iteration {mm['iteration']}: first diff at byte {mm['first_diff_byte']}"
                )

        result = ReproducibilityResult(
            test_id=f"REPRO-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            timestamp=datetime.now(),
            seed=seed,
            iterations=iterations,
            match_rate=match_rate,
            passed=passed,
            hash_original=reference_hash,
            hash_reproduced=reference_hash if passed else "MISMATCH",
            evidence=evidence,
        )
        self.results.append(result)
        return result

    def _find_first_diff(self, reference: bytes, candidate: bytes) -> int:
        for idx, (byte_a, byte_b) in enumerate(zip(reference, candidate)):
            if byte_a != byte_b:
                return idx
        return -1

    def execute_multi_seed(
        self,
        num_seeds: int = 10,
        output_length: int = 1024 * 1024,
        iterations_per_seed: int = 50,
    ) -> Dict[str, object]:
        print("\n" + "=" * 60)
        print("REPRODUCIBILITY TEST - MULTI-SEED")
        print("=" * 60)
        print(f"Seeds: {num_seeds}")
        print(f"Output per seed: {output_length / (1024 * 1024):.1f} MB")
        print(f"Iterations per seed: {iterations_per_seed}")
        print("=" * 60 + "\n")

        aggregate: List[ReproducibilityResult] = []

        for i in range(num_seeds):
            seed = hashlib.sha256(f"kayos-seed-{i}".encode()).digest()
            print(f"Seed {i + 1}/{num_seeds}: {seed.hex()[:16]}…")
            result = self.execute(seed, output_length, iterations_per_seed)
            aggregate.append(result)
            status = "PASS" if result.passed else "FAIL"
            print(f"   {status} - Match rate: {result.match_rate * 100:.2f}%")

        total_passed = sum(1 for res in aggregate if res.passed)
        overall_passed = total_passed == num_seeds

        print("\n" + "=" * 60)
        print("RESULT SUMMARY")
        print("=" * 60)
        print(f"Seeds tested: {num_seeds}")
        print(f"Seeds passed: {total_passed}")
        print(f"Overall: {'PASS' if overall_passed else 'FAIL'}")
        print("=" * 60 + "\n")

        return {
            "test_type": "reproducibility_multi_seed",
            "num_seeds": num_seeds,
            "seeds_passed": total_passed,
            "overall_passed": overall_passed,
            "results": aggregate,
        }
