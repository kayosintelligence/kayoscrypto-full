"""Enterprise wrapper for EnhancedQuantumPipeline with reporting."""
from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np

from .enhanced_pipeline import EnhancedQuantumPipeline
from .fibonacci_optimizer import FibonacciAlignmentOptimizer


class EnhancedEnterpriseOptimizer:
    """Generates enterprise reports after running the enhanced pipeline."""

    def __init__(self, enable_sator_engineering: bool = True) -> None:
        self.enable_sator = enable_sator_engineering
        self.pipeline = EnhancedQuantumPipeline(use_sator_enhancements=enable_sator_engineering)
        self.analyzer = FibonacciAlignmentOptimizer()

    def enterprise_optimize(self, data: bytes, context: Optional[str] = None) -> Dict[str, Any]:
        if len(data) < 1024:
            return {
                "status": "skipped",
                "reason": "insufficient-data",
                "enhanced_data": data,
            }

        initial = self._analyze(data)
        processed, metrics = self.pipeline.optimize_entropy_stream(data)
        final = self._analyze(processed)

        report = {
            "status": "success",
            "context": context or "enterprise_pipeline",
            "initial_analysis": initial,
            "final_analysis": final,
            "pipeline_metrics": metrics,
            "sator_engineering": self.enable_sator,
            "bigcrush_ready": self._assess_bigcrush(final),
        }
        report["improvements"] = self._compute_improvements(initial, final)

        return {"report": report, "enhanced_data": processed}

    def _analyze(self, data: bytes) -> Dict[str, Any]:
        array = np.frombuffer(data, dtype=np.uint8)
        distribution = {
            "min": int(array.min()),
            "max": int(array.max()),
            "mean": float(array.mean()),
            "std": float(array.std()),
            "unique_ratio": float(len(np.unique(array)) / 256.0),
        }
        alignment = float(self.analyzer.calculate_alignment(array))
        chi_square = float(np.sum((np.bincount(array, minlength=256) - len(array) / 256) ** 2) / (len(array) / 256))
        return {
            "alignment": alignment,
            "distribution": distribution,
            "chi_square": chi_square,
            "quality": self._classify_quality(alignment, distribution, chi_square),
        }

    @staticmethod
    def _classify_quality(alignment: float, distribution: Dict[str, float], chi_square: float) -> str:
        if distribution["unique_ratio"] > 0.95 and 0.2 < alignment < 0.45 and abs(distribution["mean"] - 127.5) < 10:
            return "EXCELLENT"
        if distribution["unique_ratio"] > 0.9 and distribution["std"] > 60:
            return "GOOD"
        return "NEEDS_IMPROVEMENT"

    @staticmethod
    def _compute_improvements(initial: Dict[str, Any], final: Dict[str, Any]) -> Dict[str, float]:
        result: Dict[str, float] = {}
        for key in ("alignment",):
            diff = final.get(key, 0.0) - initial.get(key, 0.0)
            result[f"{key}_delta"] = diff
        return result

    @staticmethod
    def _assess_bigcrush(final: Dict[str, Any]) -> Dict[str, Any]:
        criteria = {
            "quality": final.get("quality") == "EXCELLENT",
            "alignment": 0.25 < final.get("alignment", 0.0) < 0.45,
            "unique_ratio": final.get("distribution", {}).get("unique_ratio", 0.0) > 0.98,
        }
        return {
            "ready": all(criteria.values()),
            "criteria": criteria,
        }


if __name__ == "__main__":
    optimizer = EnhancedEnterpriseOptimizer()
    sample = bytes([(i * 7 + 13) % 256 for i in range(10_000)])
    result = optimizer.enterprise_optimize(sample)
    print(result["report"]["bigcrush_ready"])
