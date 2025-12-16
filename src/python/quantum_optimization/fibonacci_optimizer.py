"""Fibonacci alignment analytics and recommendations."""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
from scipy import stats

LOGGER = logging.getLogger(__name__)


@dataclass
class FibonacciAnalysis:
    """Container with the alignment analysis output."""

    current_alignment: float
    distribution_metrics: Dict[str, float]
    pattern_analysis: Dict[str, float]
    optimization_recommendations: List[str]
    golden_artifact_detected: bool = False
    raw_variance: float = 0.0
    normalized_variance: float = 0.0
    effective_threshold: float = 0.0


class FibonacciAlignmentOptimizer:
    """Analyzes and recommends fixes for the Fibonacci alignment metric."""

    def __init__(self, threshold: float = 0.64, min_improvement: float = 0.005) -> None:
        self.golden_ratio = (1 + math.sqrt(5)) / 2
        self.golden_ratio_conjugate = (math.sqrt(5) - 1) / 2
        self.threshold = threshold
        self.min_improvement = min_improvement
        self.optimal_window = (threshold - 0.005, threshold + 0.005)
        self.perfection_tolerance = 1e-10
        self.variation_tolerance = 1e-3
        self.high_variance_cutoff = 50.0
        self.natural_pattern_window = (0.61, 0.63)
        self.real_world_improvement_floor = max(0.0005, min_improvement / 2)
        self.spectral_weight = 0.45
        self.autocorr_weight = 0.35
        self.sequence_weight = 0.20
        self.fib_frequency_components = (
            1 / self.golden_ratio,
            1 / (self.golden_ratio**2),
            1 / (self.golden_ratio**3),
        )
        self.fib_autocorr_offsets = (3, 5, 8, 13, 21, 34, 55, 89)
        self.sequence_window_bits = 55
        self.sequence_sample_bytes = 512

    # ------------------------------------------------------------------
    def analyze_fibonacci_pattern(self, entropy_data: np.ndarray) -> FibonacciAnalysis:
        normalized = self._normalize(entropy_data)
        alignment, component_scores, artifact_detected, derivative_variation, dataset_variation = self._calculate_alignment(
            entropy_data, normalized
        )
        raw_variance = float(np.var(entropy_data.astype(np.float64)))
        normalized_variance = dataset_variation**2
        effective_threshold = self.determine_threshold(raw_variance)
        distribution_metrics = self._distribution_metrics(normalized)
        distribution_metrics.update(
            {
                "raw_variance": raw_variance,
                "normalized_variance": normalized_variance,
                "derivative_variance": derivative_variation,
                "spectral_score": component_scores["spectral_score"],
                "autocorr_score": component_scores["autocorr_score"],
                "sequence_score": component_scores["sequence_score"],
            }
        )
        pattern_analysis = self._pattern_analysis(normalized)
        pattern_analysis.update(component_scores)
        recommendations = (
            self._build_recommendations(alignment, distribution_metrics)
            if alignment < self.threshold
            else []
        )
        return FibonacciAnalysis(
            current_alignment=alignment,
            distribution_metrics=distribution_metrics,
            pattern_analysis=pattern_analysis,
            optimization_recommendations=recommendations,
            golden_artifact_detected=artifact_detected,
            raw_variance=raw_variance,
            normalized_variance=normalized_variance,
            effective_threshold=effective_threshold,
        )

    # ------------------------------------------------------------------
    def _normalize(self, entropy_data: np.ndarray) -> np.ndarray:
        arr = entropy_data.astype(np.float64)
        maximum = float(arr.max(initial=1.0))
        return arr / maximum if maximum else arr

    def _calculate_alignment(
        self,
        entropy_data: np.ndarray,
        normalized: np.ndarray,
    ) -> Tuple[float, Dict[str, float], bool, float, float]:
        if normalized.size < 64:
            zeros = {"spectral_score": 0.0, "autocorr_score": 0.0, "sequence_score": 0.0}
            return 0.0, zeros, False, 0.0, 0.0

        derivative_variation = float(np.std(np.diff(normalized))) if normalized.size > 2 else 0.0
        dataset_variation = float(np.std(normalized))
        alignment, components = self._compute_alignment_scores(entropy_data, normalized)
        is_flat_stream = dataset_variation < self.variation_tolerance and derivative_variation < self.variation_tolerance
        artifact_detected = (
            is_flat_stream
            or (
                dataset_variation < self.variation_tolerance
                and components["spectral_score"] > 0.8
                and components["autocorr_score"] < 0.2
            )
        )
        return alignment, components, artifact_detected, derivative_variation, dataset_variation

    def _compute_alignment_scores(self, entropy_data: np.ndarray, normalized: np.ndarray) -> Tuple[float, Dict[str, float]]:
        spectral_score = self._spectral_fibonacci_score(normalized)
        autocorr_score = self._autocorr_fibonacci_score(entropy_data)
        sequence_score = self._sequence_pattern_score(entropy_data)
        alignment = (
            self.spectral_weight * spectral_score
            + self.autocorr_weight * autocorr_score
            + self.sequence_weight * sequence_score
        )
        return alignment, {
            "spectral_score": spectral_score,
            "autocorr_score": autocorr_score,
            "sequence_score": sequence_score,
        }

    def _distribution_metrics(self, normalized: np.ndarray) -> Dict[str, float]:
        histogram, _ = np.histogram(normalized, bins=64, range=(0.0, 1.0))
        histogram = histogram.astype(np.float64) + 1e-9
        histogram /= histogram.sum()
        entropy = -np.sum(histogram * np.log2(histogram))
        skewness = float(stats.skew(normalized)) if normalized.size else 0.0
        kurtosis = float(stats.kurtosis(normalized)) if normalized.size else 0.0
        uniformity = float(stats.kstest(normalized, "uniform").pvalue) if normalized.size else 0.0
        return {
            "entropy": float(entropy / math.log2(64) if entropy else 0.0),
            "skewness": skewness,
            "kurtosis": kurtosis,
            "uniformity": uniformity,
        }

    def _pattern_analysis(self, normalized: np.ndarray) -> Dict[str, float]:
        fib_scales = (3, 5, 8, 13, 21, 34)
        analysis: Dict[str, float] = {}
        for scale in fib_scales:
            if normalized.size > scale:
                a = normalized[:-scale]
                b = normalized[scale:]
                if a.std() == 0 or b.std() == 0:
                    correlation = 0.0
                else:
                    correlation = float(np.corrcoef(a, b)[0, 1])
                analysis[f"fib_scale_{scale}"] = abs(correlation)
        return analysis

    def _build_recommendations(self, alignment: float, metrics: Dict[str, float]) -> List[str]:
        recs: List[str] = []
        if alignment < 0.62:
            recs.append("REBALANCEAR_FONTES_ENTROPIA")
        if metrics.get("skewness", 0.0) > 0.1:
            recs.append("REDUZIR_ASSIMETRIA_POSITIVA")
        if metrics.get("kurtosis", 0.0) < -0.5:
            recs.append("AUMENTAR_DENSIDADE_CENTRAL")
        if metrics.get("uniformity", 1.0) < 0.05:
            recs.append("OTIMIZAR_PARÂMETROS_CONDICIONAMENTO")
        if not recs:
            recs.append("AJUSTE_FINE_TUNING_FIBONACCI")
        return recs

    # Public helper for other modules/tests
    def calculate_alignment(self, entropy_data: np.ndarray) -> float:
        normalized = self._normalize(entropy_data)
        alignment, *_ = self._calculate_alignment(entropy_data, normalized)
        return alignment

    def _spectral_fibonacci_score(self, normalized: np.ndarray) -> float:
        series = normalized
        if series.size > 4096:
            series = series[:4096]
        centered = series - np.mean(series)
        if not np.any(centered):
            return 0.0
        spectrum = np.fft.rfft(centered)
        freqs = np.fft.rfftfreq(centered.size, d=0.5)
        total_power = float(np.sum(np.abs(spectrum)))
        if total_power == 0.0:
            return 0.0
        fib_power = 0.0
        for target in self.fib_frequency_components:
            if target > freqs.max():
                continue
            idx = int(np.argmin(np.abs(freqs - target)))
            fib_power += float(np.abs(spectrum[idx]))
        return min(1.0, fib_power / total_power)

    def _autocorr_fibonacci_score(self, entropy_data: np.ndarray) -> float:
        data = entropy_data.astype(np.float64)
        max_offset = self.fib_autocorr_offsets[-1]
        if data.size <= max_offset + 1:
            return 0.0
        centered = data - np.mean(data)
        std = np.std(centered)
        if std < 1e-9:
            return 0.0
        norm = centered / std
        scores: List[float] = []
        for offset in self.fib_autocorr_offsets:
            if offset >= norm.size:
                break
            corr = np.corrcoef(norm[:-offset], norm[offset:])[0, 1]
            if math.isnan(corr):
                continue
            scores.append(1.0 - min(1.0, abs(float(corr))))
        if not scores:
            return 0.0
        return float(np.clip(np.mean(scores), 0.0, 1.0))

    def _sequence_pattern_score(self, entropy_data: np.ndarray) -> float:
        sample = entropy_data.astype(np.uint8)
        if sample.size < self.sequence_window_bits // 8:
            return 0.0
        if sample.size > self.sequence_sample_bytes:
            sample = sample[: self.sequence_sample_bytes]
        bits = np.unpackbits(sample)
        window = self.sequence_window_bits
        if bits.size < window:
            return 0.0
        matches = 0
        windows = 0
        for start in range(0, bits.size - window, window // 2 or 1):
            window_bits = bits[start : start + window]
            ones = int(window_bits.sum())
            zeros = window - ones
            if zeros == 0:
                continue
            ratio = ones / zeros
            if abs(ratio - self.golden_ratio) <= 0.05:
                matches += 1
            windows += 1
        if windows == 0:
            return 0.0
        return matches / windows

    def determine_threshold(self, raw_variance: float) -> float:
        return 0.62 if raw_variance >= self.high_variance_cutoff else self.threshold

    def should_apply_optimization(self, current_alignment: float, predicted_improvement: float, raw_variance: float) -> bool:
        """Decide if a corrective pass should be executed."""

        effective_threshold = self.determine_threshold(raw_variance)
        min_improvement = self.real_world_improvement_floor if raw_variance >= self.high_variance_cutoff else self.min_improvement
        conditions = (
            current_alignment < effective_threshold,
            predicted_improvement >= min_improvement,
            current_alignment < 0.99,
        )
        return all(conditions)

    def _is_excessively_perfect_value(self, value: float) -> bool:
        return abs(value - self.golden_ratio_conjugate) < self.perfection_tolerance

    def is_natural_pattern(self, alignment: float, raw_variance: float) -> bool:
        low_bound, high_bound = self.natural_pattern_window
        return raw_variance >= self.high_variance_cutoff and low_bound <= alignment <= high_bound


# =============================================================================
# INTEGRAÇÃO ENTERPRISE - ADICIONADA AO SISTEMA EXISTENTE
# =============================================================================


class FibonacciEnterpriseIntegration:
    """Integração do sistema enterprise com o otimizador Fibonacci."""

    def __init__(self) -> None:
        try:
            from python.quantum_optimization.enterprise_optimizer import (
                EnterpriseDiagnosis,
                FibonacciEnterpriseOptimizer,
            )

            self.enterprise_optimizer = FibonacciEnterpriseOptimizer()
            self.enterprise_available = True
        except ImportError:
            self.enterprise_available = False
            LOGGER.warning("Sistema enterprise não disponível")

    def execute_enterprise_analysis(self, data: np.ndarray, current_alignment: float):
        """Executa análise enterprise se disponível."""

        if not self.enterprise_available:
            return None, None

        try:
            diagnosis = self.enterprise_optimizer.diagnosticar_problema_alinhamento(
                data, current_alignment
            )
            if diagnosis.optimization_strategy.value != "manter_atual":
                optimized_data = self.enterprise_optimizer.aplicar_correcao_enterprise(
                    data, diagnosis.optimization_strategy
                )
            else:
                optimized_data = data

            report = self.enterprise_optimizer.gerar_relatorio_executivo(diagnosis)
            return optimized_data, report
        except Exception as exc:  # pragma: no cover - defensive guard
            LOGGER.error("Erro na análise enterprise: %s", exc)
            return None, None


def _enhance_with_enterprise():
    """Adiciona capacidades enterprise ao FibonacciAlignmentOptimizer."""

    FibonacciAlignmentOptimizer.enterprise_integration = FibonacciEnterpriseIntegration()

    def analyze_with_enterprise(self, data: np.ndarray):
        original_analysis = self.analyze_fibonacci_pattern(data)
        enterprise_data, enterprise_report = self.enterprise_integration.execute_enterprise_analysis(
            data, original_analysis.current_alignment
        )
        return {
            "original_analysis": original_analysis,
            "enterprise_diagnosis": enterprise_report,
            "enterprise_optimized_data": enterprise_data,
        }

    FibonacciAlignmentOptimizer.analyze_with_enterprise = analyze_with_enterprise


_enhance_with_enterprise()
