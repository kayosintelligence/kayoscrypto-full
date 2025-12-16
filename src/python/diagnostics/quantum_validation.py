"""Quantum-oriented entropy validation helpers.

This module provides a light-weight validation engine that mirrors the
Fibonacci → Ezekiel → Core (Fishbone) pipeline at the analysis level. It is
able to inspect raw entropy captures (binary or ASCII) and correlate them with
PractRand/TestU01 style logs so we can keep automated diagnostics close to the
source of truth.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

import numpy as np

from python.quantum_optimization.fibonacci_optimizer import FibonacciAlignmentOptimizer


@dataclass(frozen=True)
class QuantumMetric:
    """Score for a single geometric/quantum heuristic."""

    name: str
    score: float
    threshold: float
    status: str
    details: str = ""


@dataclass(frozen=True)
class QuantumValidationReport:
    """Aggregate report produced by :class:`QuantumValidationEngine`."""

    entropy_path: Path
    practrand_log: Optional[Path]
    metrics: Sequence[QuantumMetric]
    anomalies: Sequence[str] = field(default_factory=tuple)

    @property
    def passed(self) -> bool:
        """Return ``True`` when every metric meets its expected threshold."""

        return all(metric.score >= metric.threshold for metric in self.metrics)


class QuantumValidationEngine:
    """Simple orchestrator for quantum-aligned entropy validation.

    Parameters
    ----------
    entropy_path:
        Path to the captured entropy stream (binary file or ASCII bit-stream).
    practrand_log:
        Optional PractRand/TestU01 log used for anomaly correlation.
    """

    _ASCII_BYTES = set(b"01 \t\n\r")

    def __init__(self, entropy_path: Path, practrand_log: Optional[Path] = None) -> None:
        self.entropy_path = Path(entropy_path)
        self.practrand_log = Path(practrand_log) if practrand_log else None
        self._fibonacci_optimizer = FibonacciAlignmentOptimizer()

    def evaluate(self, sample_bytes: int = 262_144) -> QuantumValidationReport:
        """Evaluate the entropy capture and return a structured report.

        Parameters
        ----------
        sample_bytes:
            Maximum amount of data (in bytes) to analyse. Defaults to 256 KiB to
            keep CI cycles fast while still observing multiple Ezekiel wheel
            periods.
        """

        values = self._load_entropy_window(sample_bytes)
        metrics = [
            self._fibonacci_alignment(values),
            self._ezekiel_tensor_balance(values),
            self._sator_cube_entropy(values),
        ]
        anomalies = self._parse_practrand_anomalies()
        return QuantumValidationReport(
            entropy_path=self.entropy_path,
            practrand_log=self.practrand_log,
            metrics=tuple(metrics),
            anomalies=tuple(anomalies),
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _load_entropy_window(self, sample_bytes: int) -> np.ndarray:
        if not self.entropy_path.exists():
            raise FileNotFoundError(self.entropy_path)

        raw = self.entropy_path.read_bytes()
        if not raw:
            raise ValueError("Entropy capture is empty")

        raw = raw[:sample_bytes] if sample_bytes else raw
        if self._looks_ascii_bits(raw):
            bit_values = [1 if byte == ord("1") else 0 for byte in raw if byte in (48, 49)]
            if len(bit_values) < 8:
                raise ValueError("Not enough bits to evaluate entropy stream")
            return np.array(bit_values, dtype=np.float64)

        return np.frombuffer(raw, dtype=np.uint8).astype(np.float64)

    def _looks_ascii_bits(self, data: bytes) -> bool:
        return len(set(data) - self._ASCII_BYTES) == 0

    def _fibonacci_alignment(self, values: np.ndarray) -> QuantumMetric:
        byte_values = np.clip(np.rint(values), 0, 255).astype(np.uint8)
        analysis = self._fibonacci_optimizer.analyze_fibonacci_pattern(byte_values)
        score = float(analysis.current_alignment)
        status = "pass" if score >= 0.35 else "monitor"
        spectral = analysis.pattern_analysis.get("spectral_score", 0.0)
        autocorr = analysis.pattern_analysis.get("autocorr_score", 0.0)
        sequence = analysis.pattern_analysis.get("sequence_score", 0.0)
        details = (
            f"spectral={spectral:.3f}, autocorr={autocorr:.3f}, sequence={sequence:.3f}, "
            f"threshold={analysis.effective_threshold:.3f}"
        )
        return QuantumMetric(
            name="Fibonacci Direction Alignment",
            score=score,
            threshold=0.35,
            status=status,
            details=details,
        )

    def _ezekiel_tensor_balance(self, values: np.ndarray) -> QuantumMetric:
        if len(values) < 48:
            raise ValueError("Need at least 48 samples for tensor balance analysis")

        reshaped = values[: len(values) - (len(values) % 3)].reshape(-1, 3)
        axis_std = reshaped.std(axis=0)
        balance = 1.0 - (axis_std.max() - axis_std.min()) / (axis_std.max() + 1e-6)
        score = max(0.0, min(1.0, balance))
        status = "pass" if score >= 0.60 else "monitor"
        details = f"axis_std={[round(val, 4) for val in axis_std]}"
        return QuantumMetric(
            name="Ezekiel Wheel Tensor Balance",
            score=score,
            threshold=0.60,
            status=status,
            details=details,
        )

    def _sator_cube_entropy(self, values: np.ndarray) -> QuantumMetric:
        hist = np.bincount(values.astype(int), minlength=256).astype(np.float64)
        probs = hist / hist.sum()
        non_zero = probs > 0
        entropy = -np.sum(probs[non_zero] * np.log2(probs[non_zero]))
        normalized_entropy = entropy / 8.0  # 8 bits per sample
        score = max(0.0, min(1.0, normalized_entropy))
        status = "pass" if score >= 0.92 else "monitor"
        details = f"entropy={entropy:.3f} bits/byte"
        return QuantumMetric(
            name="SATOR Cube Entropy",
            score=score,
            threshold=0.92,
            status=status,
            details=details,
        )

    def _parse_practrand_anomalies(self) -> List[str]:
        if not self.practrand_log or not self.practrand_log.exists():
            return []

        anomalies: List[str] = []
        anomaly_pattern = re.compile(r"p\s*=\s*([0-9eE+\-.]+).*?(FAIL|unusual)", re.IGNORECASE)
        for line in self.practrand_log.read_text(errors="ignore").splitlines():
            match = anomaly_pattern.search(line)
            if match:
                anomalies.append(line.strip())
        return anomalies