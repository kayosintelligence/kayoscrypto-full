"""Multidimensional entropy distribution tests (Tier 2)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, List

import numpy as np
from scipy.spatial.distance import pdist
from scipy.stats import kstest


@dataclass
class MultiDimEntropyResult:
    """Holds summary metrics for a multidimensional entropy test."""

    test_id: str
    timestamp: datetime
    dimensions: int
    samples: int
    uniformity_score: float
    clustering_score: float
    ks_statistic: float
    passed: bool
    evidence: List[str] = field(default_factory=list)


class MultiDimEntropyTest:
    """Validates entropy distribution in multi-dimensional space."""

    def __init__(self, trng_callable: Callable[[bytes, int], bytes]) -> None:
        self.trng = trng_callable
        self.results: List[MultiDimEntropyResult] = []

    def execute(
        self,
        seed: bytes,
        dimensions: int = 6,
        samples: int = 10000,
    ) -> MultiDimEntropyResult:
        print("\n" + "=" * 60)
        print("MULTIDIMENSIONAL ENTROPY DISTRIBUTION TEST")
        print("=" * 60)
        print(f"Dimensions: {dimensions}")
        print(f"Samples: {samples}")
        print("=" * 60 + "\n")

        evidence: List[str] = []
        points = np.zeros((samples, dimensions), dtype=float)

        for idx in range(samples):
            derived_seed = seed + idx.to_bytes(4, "big")
            sample = self.trng(derived_seed, dimensions)
            points[idx] = np.frombuffer(sample, dtype=np.uint8) / 255.0
            if (idx + 1) % 1000 == 0:
                print(f"  Generated {idx + 1}/{samples} samples")

        ks_stats: List[float] = []
        for dim in range(dimensions):
            stat, pvalue = kstest(points[:, dim], "uniform")
            ks_stats.append(stat)
            evidence.append(f"Dim {dim}: KS stat={stat:.6f}, p-value={pvalue:.4f}")

        avg_ks = float(np.mean(ks_stats))
        max_ks = float(np.max(ks_stats))
        evidence.append(f"Average KS: {avg_ks:.6f}")
        evidence.append(f"Max KS: {max_ks:.6f}")
        evidence.append("ks threshold: avg < 0.05, max < 0.10")

        subset = points[::10]
        distances = pdist(subset)
        min_dist = float(np.min(distances))
        avg_dist = float(np.mean(distances))
        clustering_score = min_dist / avg_dist if avg_dist else 0.0
        evidence.append(f"Min distance: {min_dist:.6f}")
        evidence.append(f"Avg distance: {avg_dist:.6f}")
        evidence.append(f"Clustering score: {clustering_score:.6f}")
        evidence.append("Clustering threshold: > 0.05")

        uniformity_ok = avg_ks < 0.05 and max_ks < 0.10
        clustering_ok = clustering_score > 0.05
        passed = uniformity_ok and clustering_ok
        uniformity_score = 1.0 - min(avg_ks / 0.05, 1.0)

        evidence.append("Uniformity OK" if uniformity_ok else "Uniformity FAIL")
        evidence.append("No clustering detected" if clustering_ok else "Clustering detected")

        result = MultiDimEntropyResult(
            test_id=f"MDIM-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            timestamp=datetime.now(),
            dimensions=dimensions,
            samples=samples,
            uniformity_score=uniformity_score,
            clustering_score=clustering_score,
            ks_statistic=avg_ks,
            passed=passed,
            evidence=evidence,
        )
        self.results.append(result)

        print("\n" + "=" * 60)
        print(f"RESULT: {'PASS' if passed else 'FAIL'}")
        print("=" * 60 + "\n")
        return result
