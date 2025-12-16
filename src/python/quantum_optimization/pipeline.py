"""End-to-end optimization pipeline for entropy streams."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np

from .fibonacci_corrector import FibonacciAlignmentCorrector
from .fibonacci_optimizer import FibonacciAlignmentOptimizer, FibonacciAnalysis


@dataclass
class OptimizationResult:
    """Represents the outcome of an optimization run."""

    original_alignment: float
    optimized_alignment: float
    improvement: float
    optimization_applied: bool
    validation_passed: bool
    recommendations: list[str]
    optimized_stream: bytes
    effective_threshold: float
    raw_variance: float
    artifact_detected: bool


class QuantumOptimizationPipeline:
    """Coordinates Fibonacci analysis + corrective steps."""

    def __init__(
        self,
        optimizer: Optional[FibonacciAlignmentOptimizer] = None,
        corrector: Optional[FibonacciAlignmentCorrector] = None,
    ) -> None:
        self.optimizer = optimizer or FibonacciAlignmentOptimizer()
        self.corrector = corrector or FibonacciAlignmentCorrector(self.optimizer)
        self.history: list[OptimizationResult] = []

    def optimize_entropy_stream(
        self,
        entropy_data: bytes,
        context: str | None = None,
        *,
        force_correction: bool = False,
    ) -> OptimizationResult:
        entropy_array = np.frombuffer(entropy_data, dtype=np.uint8)
        analysis = self.optimizer.analyze_fibonacci_pattern(entropy_array)

        optimized_stream = entropy_data
        optimized_alignment = analysis.current_alignment
        applied = False
        effective_threshold = analysis.effective_threshold or self.optimizer.determine_threshold(analysis.raw_variance)

        need_correction = (
            force_correction
            or analysis.current_alignment < effective_threshold
            or analysis.golden_artifact_detected
        )

        if need_correction:
            if force_correction:
                candidate_stream = self.corrector.apply_forced_correction(entropy_data)
                candidate_array = np.frombuffer(candidate_stream, dtype=np.uint8)
                candidate_alignment = self.optimizer.calculate_alignment(candidate_array)
                improvement = candidate_alignment - analysis.current_alignment
                if improvement >= -0.01:
                    optimized_stream = candidate_stream
                    optimized_alignment = candidate_alignment
                    applied = True
            else:
                candidate_stream = self.corrector.apply_fibonacci_correction(entropy_data, analysis)
                candidate_array = np.frombuffer(candidate_stream, dtype=np.uint8)
                candidate_alignment = self.optimizer.calculate_alignment(candidate_array)
                improvement = candidate_alignment - analysis.current_alignment
                should_apply = (
                    analysis.golden_artifact_detected
                    or self.optimizer.should_apply_optimization(
                        analysis.current_alignment,
                        improvement,
                        analysis.raw_variance,
                    )
                )
                if should_apply:
                    optimized_stream = candidate_stream
                    optimized_alignment = candidate_alignment
                    applied = True

        result = OptimizationResult(
            original_alignment=analysis.current_alignment,
            optimized_alignment=optimized_alignment,
            improvement=optimized_alignment - analysis.current_alignment,
            optimization_applied=applied,
            validation_passed=optimized_alignment >= effective_threshold,
            recommendations=analysis.optimization_recommendations,
            optimized_stream=optimized_stream,
            effective_threshold=effective_threshold,
            raw_variance=analysis.raw_variance,
            artifact_detected=analysis.golden_artifact_detected,
        )
        self.history.append(result)
        return result
