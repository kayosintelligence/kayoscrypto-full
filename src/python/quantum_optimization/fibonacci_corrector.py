"""Corrective transformations to push Fibonacci alignment upwards."""

from __future__ import annotations

import logging
import math

import numpy as np

from .fibonacci_optimizer import FibonacciAlignmentOptimizer, FibonacciAnalysis

LOGGER = logging.getLogger(__name__)


class FibonacciAlignmentCorrector:
    """Applies lightweight corrective passes to entropy streams."""

    def __init__(self, optimizer: FibonacciAlignmentOptimizer | None = None) -> None:
        self.optimizer = optimizer or FibonacciAlignmentOptimizer()

    def apply_fibonacci_correction(
        self, entropy_stream: bytes, analysis: FibonacciAnalysis | None = None
    ) -> bytes:
        data = np.frombuffer(entropy_stream, dtype=np.uint8)
        analysis = analysis or self.optimizer.analyze_fibonacci_pattern(data)
        raw_variance = analysis.raw_variance
        effective_threshold = analysis.effective_threshold or self.optimizer.determine_threshold(raw_variance)

        if self._is_exact_golden_ratio(analysis) or analysis.golden_artifact_detected:
            LOGGER.info("Forcing Fibonacci correction due to perfect golden ratio pattern")
            return self._apply_forced_correction(data)

        if analysis.current_alignment >= effective_threshold:
            return entropy_stream

        if self.optimizer.is_natural_pattern(analysis.current_alignment, raw_variance):
            LOGGER.info(
                "Applying natural-pattern correction (%.3f alignment, variance %.2f)",
                analysis.current_alignment,
                raw_variance,
            )
            corrected = self._apply_natural_correction(data.astype(np.float64))
        else:
            LOGGER.info(
                "Fibonacci correction triggered (%.3f -> %.3f target)",
                analysis.current_alignment,
                effective_threshold,
            )
            corrected = self._correct_fibonacci_alignment(data.astype(np.float64))

        corrected = np.clip(corrected, 0, 255).astype(np.uint8)
        return corrected.tobytes()

    def apply_forced_correction(self, entropy_stream: bytes | np.ndarray) -> bytes:
        """Expose forced correction path for callers that must override heuristics."""

        if isinstance(entropy_stream, np.ndarray):
            data = entropy_stream.astype(np.uint8)
        else:
            data = np.frombuffer(entropy_stream, dtype=np.uint8)
        return self._apply_forced_correction(data)

    # ------------------------------------------------------------------
    def _correct_fibonacci_alignment(self, data: np.ndarray) -> np.ndarray:
        weighted = data * self._generate_fibonacci_weights(len(data))
        transformed = self._apply_golden_ratio_transform(weighted)
        return self._fibonacci_resampling(transformed)

    def _generate_fibonacci_weights(self, length: int) -> np.ndarray:
        base = np.array([1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89], dtype=np.float64)
        if length <= base.size:
            weights = base[:length]
        else:
            weights = np.resize(base, length)
        return weights / weights.max(initial=1.0)

    def _apply_golden_ratio_transform(self, data: np.ndarray) -> np.ndarray:
        phi = self.optimizer.golden_ratio
        phases = (np.arange(len(data)) * phi) % 1.0
        return (data + phases * 255.0) % 256.0

    def _fibonacci_resampling(self, data: np.ndarray) -> np.ndarray:
        fib_offsets = (0, 1, 2, 3, 5, 8, 13, 21)
        resampled = np.empty_like(data)
        for idx in range(len(data)):
            samples = []
            for offset in fib_offsets:
                pos = idx + offset
                if pos < len(data):
                    samples.append(data[pos])
            resampled[idx] = np.median(samples) if samples else data[idx]
        return resampled

    # ------------------------------------------------------------------
    def _is_exact_golden_ratio(self, analysis: FibonacciAnalysis | float) -> bool:
        if isinstance(analysis, float):
            alignment = analysis
        else:
            alignment = analysis.current_alignment
        return abs(alignment - self.optimizer.golden_ratio_conjugate) < self.optimizer.perfection_tolerance

    def _apply_forced_correction(self, data: np.ndarray) -> bytes:
        float_data = data.astype(np.float32)
        candidates = []
        for candidate in self._generate_forced_candidates(float_data):
            clipped = np.clip(candidate, 0, 255)
            alignment = self.optimizer.calculate_alignment(clipped.astype(np.uint8))
            candidates.append((alignment, clipped))

        if not candidates:
            LOGGER.warning("Forced correction fallback produced no candidates; returning original stream")
            return data.tobytes()

        best_alignment, best_candidate = max(candidates, key=lambda item: item[0])
        if np.array_equal(best_candidate.astype(np.uint8), data.astype(np.uint8)):
            best_candidate = self._apply_structural_correction(data.astype(np.float32))
            best_alignment = self.optimizer.calculate_alignment(best_candidate.astype(np.uint8))
        LOGGER.info("Forced correction lifted alignment to %.6f", best_alignment)
        return best_candidate.astype(np.uint8).tobytes()

    def _generate_forced_candidates(self, data: np.ndarray):
        transforms = (
            self._apply_quantum_perturbation,
            self._apply_entropy_redistribution,
            self._apply_multidimensional_shuffle,
            self._apply_fibonacci_reshuffling,
            self._apply_golden_ratio_phase_shift,
            self._apply_fibonacci_xor_mask,
        )
        for transform in transforms:
            candidate = transform(data)
            candidate = self._inject_phi_alignment(candidate)
            candidate = self._inject_deterministic_variation(candidate)
            yield candidate

    def _apply_quantum_perturbation(self, data: np.ndarray) -> np.ndarray:
        phi = self.optimizer.golden_ratio
        phases = np.sin(np.arange(len(data)) * phi) * 0.5 + 0.5
        perturbation = phases * 21.0
        return (data + perturbation) % 256.0

    def _apply_entropy_redistribution(self, data: np.ndarray) -> np.ndarray:
        rolled = np.roll(data, 13)
        blended = 0.65 * data + 0.35 * rolled
        return blended

    def _apply_multidimensional_shuffle(self, data: np.ndarray) -> np.ndarray:
        block = 8
        trimmed_len = len(data) - (len(data) % block)
        reshaped = data[:trimmed_len].reshape(-1, block)
        shuffled = reshaped[:, ::-1]
        result = np.copy(data)
        result[:trimmed_len] = shuffled.reshape(-1)
        return result

    def _apply_fibonacci_reshuffling(self, data: np.ndarray) -> np.ndarray:
        result = np.copy(data)
        fib_seq = (1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89)
        for idx, offset in enumerate(fib_seq):
            target = idx + offset
            if target < result.size:
                result[idx], result[target] = result[target], result[idx]
        return result

    def _apply_golden_ratio_phase_shift(self, data: np.ndarray) -> np.ndarray:
        phi = self.optimizer.golden_ratio
        idx = np.arange(len(data), dtype=np.float32)
        phase = ((idx / phi) % 1.0) * 37.0
        return (data + phase) % 256.0

    def _apply_fibonacci_xor_mask(self, data: np.ndarray) -> np.ndarray:
        mask = self._generate_fibonacci_mask(len(data))
        return np.bitwise_xor(data.astype(np.uint8), mask).astype(np.float32)

    def _generate_fibonacci_mask(self, length: int) -> np.ndarray:
        mask = np.empty(length, dtype=np.uint8)
        a, b = 1, 1
        for idx in range(length):
            mask[idx] = a % 256
            a, b = b, (a + b) % 256
        return mask

    def _apply_structural_correction(self, data: np.ndarray) -> np.ndarray:
        mutated = self._apply_fibonacci_reshuffling(data)
        mutated = self._apply_golden_ratio_phase_shift(mutated)
        mask = self._generate_fibonacci_mask(len(mutated))
        mutated = np.bitwise_xor(mutated.astype(np.uint8), mask).astype(np.float32)
        return np.clip(mutated, 0, 255)

    def _inject_deterministic_variation(self, candidate: np.ndarray) -> np.ndarray:
        perturb = (np.arange(len(candidate), dtype=np.float32) % 31) + 1.0
        return (candidate + perturb) % 256.0

    def _inject_phi_alignment(self, candidate: np.ndarray) -> np.ndarray:
        phi = self.optimizer.golden_ratio
        base_value = 255.0 / phi
        idx = np.arange(len(candidate), dtype=np.float32)
        phi_pattern = np.where((idx % 2) == 0, base_value, 255.0)
        blended = 0.55 * candidate + 0.45 * phi_pattern
        return blended % 256.0

    def _apply_natural_correction(self, data: np.ndarray) -> np.ndarray:
        block = 32
        trimmed = len(data) - (len(data) % block)
        reshaped = data[:trimmed].reshape(-1, block).astype(np.float64)
        sorted_blocks = np.sort(reshaped, axis=1)
        ramp = np.arange(block, dtype=np.float64)
        sorted_blocks = (sorted_blocks + ramp) % 256.0
        blended = np.copy(data).astype(np.float64)
        blended[:trimmed] = sorted_blocks.reshape(-1)
        blended = 0.85 * blended + 0.15 * np.roll(blended, 5)
        return blended
