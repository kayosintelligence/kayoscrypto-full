"""QuantumResistanceManager implements post-quantum readiness assessments."""
from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
import json
import statistics
from . import register_quantum_hook

try:
    import tomllib  # Python >=3.11
except ModuleNotFoundError:  # pragma: no cover - compatibility fallback
    import tomli as tomllib  # type: ignore


DEFAULT_THRESHOLDS = {
    "grover_avalanche_min": 0.35,
    "grover_entropy_min": 0.75,
    "shor_key_bits_min": 512,
    "shor_entropy_min": 0.85,
    "log_sensitivity_max": 0.25,
}


class ThreatLevel(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


class QuantumThreat(str, Enum):
    SHOR = "shor"
    GROVER = "grover"
    HYBRID = "hybrid"


@dataclass
class VulnerabilityReport:
    threat: QuantumThreat
    score: float
    level: ThreatLevel
    notes: str = ""


@dataclass
class QuantumResistanceReport:
    metrics: Dict[str, float]
    vulnerabilities: List[VulnerabilityReport] = field(default_factory=list)

    def overall_level(self) -> ThreatLevel:
        levels = {report.level for report in self.vulnerabilities}
        if ThreatLevel.RED in levels:
            return ThreatLevel.RED
        if ThreatLevel.YELLOW in levels:
            return ThreatLevel.YELLOW
        return ThreatLevel.GREEN


class QuantumResistanceManager:
    """Evaluate cipher data against post-quantum threat models."""

    name = "quantum_resistance_manager"

    def __init__(self, config_path: Path | None = None) -> None:
        self.thresholds = self._load_thresholds(config_path)
        self.history_dir = Path("reports/quantum")
        self.history_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------
    def _load_thresholds(self, config_path: Path | None) -> Dict[str, float]:
        if config_path is None:
            config_path = Path("pyproject.toml")
        if not config_path.exists():
            return DEFAULT_THRESHOLDS.copy()

        try:
            with config_path.open("rb") as f:
                data = tomllib.load(f)
        except (OSError, tomllib.TOMLDecodeError):
            return DEFAULT_THRESHOLDS.copy()

        thresholds = data.get("tool", {}).get("kayos", {}).get("quantum", {})
        result = DEFAULT_THRESHOLDS.copy()
        for key, value in thresholds.items():
            if isinstance(value, (int, float)):
                result[key] = float(value)
        return result

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------
    def compute_metrics(self, snapshot: Dict[str, float | bytes]) -> Dict[str, float]:
        """Normalize cipher snapshot into metrics used by the threat models."""
        metrics = {
            "avalanche": float(snapshot.get("avalanche", 0.0)),
            "entropy": float(snapshot.get("entropy", 0.0)),
            "key_bits": float(snapshot.get("key_bits", 0.0)),
            "log_sensitivity": float(snapshot.get("log_sensitivity", 0.0)),
        }

        raw_plaintext = snapshot.get("plaintext_bytes")
        raw_ciphertext = snapshot.get("ciphertext_bytes")
        raw_key = snapshot.get("key_bytes")

        if isinstance(raw_plaintext, (bytes, bytearray)) and isinstance(raw_ciphertext, (bytes, bytearray)):
            metrics.setdefault("avalanche", self._calculate_avalanche_ratio(raw_plaintext, raw_ciphertext))
            metrics.setdefault("entropy", self._shannon_entropy(raw_ciphertext))
            metrics.setdefault("log_sensitivity", self._log_sensitivity(raw_plaintext, raw_ciphertext))

        if isinstance(raw_key, (bytes, bytearray)):
            metrics.setdefault("key_bits", float(len(raw_key) * 8))

        # Optional historical entropy mixing
        entropy_samples = snapshot.get("entropy_samples")
        if isinstance(entropy_samples, Iterable):
            samples = [float(sample) for sample in entropy_samples]
            if samples:
                metrics["entropy"] = statistics.fmean(samples)
                metrics["entropy_deviation"] = statistics.pstdev(samples)
        return metrics

    # ------------------------------------------------------------------
    # Threat models
    # ------------------------------------------------------------------
    def assess_vulnerability(self, snapshot: Dict[str, float | bytes] | None = None) -> QuantumResistanceReport:
        metrics = self.compute_metrics(snapshot or {})
        vulnerabilities: List[VulnerabilityReport] = []

        vulnerabilities.append(self._evaluate_shor(metrics))
        vulnerabilities.append(self._evaluate_grover(metrics))
        vulnerabilities.append(self._evaluate_hybrid(metrics))

        report = QuantumResistanceReport(metrics=metrics, vulnerabilities=vulnerabilities)
        self._persist_report(report)
        return report

    def _evaluate_shor(self, metrics: Dict[str, float]) -> VulnerabilityReport:
        key_bits = metrics.get("key_bits", 0.0)
        entropy = metrics.get("entropy", 0.0)
        threshold_bits = self.thresholds["shor_key_bits_min"]
        threshold_entropy = self.thresholds["shor_entropy_min"]

        score_bits = min(1.0, key_bits / threshold_bits) if threshold_bits else 0.0
        score_entropy = min(1.0, entropy / threshold_entropy) if threshold_entropy else 0.0
        score = 0.6 * score_bits + 0.4 * score_entropy

        if score >= 1.0:
            level = ThreatLevel.GREEN
            notes = "Key size and entropy exceed Shor thresholds."
        elif score >= 0.75:
            level = ThreatLevel.YELLOW
            notes = "Increase key size or entropy for Shor resistance."
        else:
            level = ThreatLevel.RED
            notes = "Key size/entropy below recommended minimum for Shor attacks."

        return VulnerabilityReport(QuantumThreat.SHOR, round(score, 3), level, notes)

    def _evaluate_grover(self, metrics: Dict[str, float]) -> VulnerabilityReport:
        avalanche = metrics.get("avalanche", 0.0)
        entropy = metrics.get("entropy", 0.0)
        threshold_avalanche = self.thresholds["grover_avalanche_min"]
        threshold_entropy = self.thresholds["grover_entropy_min"]

        score_avalanche = min(1.0, avalanche / threshold_avalanche) if threshold_avalanche else 0.0
        score_entropy = min(1.0, entropy / threshold_entropy) if threshold_entropy else 0.0
        score = 0.5 * score_avalanche + 0.5 * score_entropy

        if score >= 1.0:
            level = ThreatLevel.GREEN
            notes = "Avalanche and entropy meet Grover requirements."
        elif score >= 0.8:
            level = ThreatLevel.YELLOW
            notes = "Avalanche effect marginal for Grover attacks."
        else:
            level = ThreatLevel.RED
            notes = "Increase diffusion/entropy to resist Grover attacks."

        return VulnerabilityReport(QuantumThreat.GROVER, round(score, 3), level, notes)

    def _evaluate_hybrid(self, metrics: Dict[str, float]) -> VulnerabilityReport:
        log_sensitivity = metrics.get("log_sensitivity", 0.0)
        threshold = self.thresholds["log_sensitivity_max"]
        ratio = threshold / log_sensitivity if log_sensitivity else float("inf")
        score = min(1.0, ratio)

        if score >= 1.0:
            level = ThreatLevel.GREEN
            notes = "Low key derivation sensitivity to hybrid attacks."
        elif score >= 0.7:
            level = ThreatLevel.YELLOW
            notes = "Monitor key derivation sensitivity under hybrid threats."
        else:
            level = ThreatLevel.RED
            notes = "Reduce key derivation leakage for hybrid attack resistance."

        return VulnerabilityReport(QuantumThreat.HYBRID, round(score, 3), level, notes)

    # ------------------------------------------------------------------
    # Reporting & guidance
    # ------------------------------------------------------------------
    def build_report(self, report: QuantumResistanceReport) -> Dict[str, object]:
        return {
            "metrics": report.metrics,
            "vulnerabilities": [
                {
                    "threat": vr.threat.value,
                    "score": vr.score,
                    "level": vr.level.value,
                    "notes": vr.notes,
                }
                for vr in report.vulnerabilities
            ],
            "overall": report.overall_level().value,
        }

    def recommend_improvements(self, report: QuantumResistanceReport) -> List[str]:
        suggestions: List[str] = []
        for vulnerability in report.vulnerabilities:
            if vulnerability.level == ThreatLevel.GREEN:
                continue
            suggestions.append(vulnerability.notes)
        if not suggestions:
            suggestions.append("Maintain current parameters; quantum profile is stable.")
        return suggestions

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------
    def _persist_report(self, report: QuantumResistanceReport) -> None:
        payload = self.build_report(report)
        filename = self.history_dir / f"quantum_report_{payload['overall']}.json"
        try:
            with filename.open("w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except OSError:
            # Persistence is optional; ignore file system issues for now.
            return

    # ------------------------------------------------------------------
    # Hook protocol (for future Spine integration)
    # ------------------------------------------------------------------
    def update(self, state: dict) -> None:
        """Hook entry point compatible with Spine quantum hooks."""
        snapshot = state.get("quantum_snapshot", {})
        report = self.assess_vulnerability(snapshot)
        state.setdefault("quantum_reports", {})[self.name] = self.build_report(report)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _shannon_entropy(data: bytes | bytearray) -> float:
        if not data:
            return 0.0
        counts = Counter(data)
        length = len(data)
        entropy_bits = -sum((count / length) * math.log2(count / length) for count in counts.values())
        return entropy_bits / 8.0  # normalize 0-1

    @staticmethod
    def _calculate_avalanche_ratio(plaintext: bytes, ciphertext: bytes) -> float:
        total_bits = min(len(plaintext), len(ciphertext)) * 8
        if total_bits == 0:
            return 0.0
        diff_bits = 0
        for b1, b2 in zip(plaintext, ciphertext):
            diff_bits += (b1 ^ b2).bit_count()
        return diff_bits / total_bits

    @staticmethod
    def _log_sensitivity(plaintext: bytes, ciphertext: bytes) -> float:
        if not plaintext or not ciphertext:
            return 0.0
        span = [b1 ^ b2 for b1, b2 in zip(plaintext, ciphertext)]
        if not span:
            return 0.0
        mean = sum(span) / len(span)
        variance = sum((value - mean) ** 2 for value in span) / len(span)
        return min(1.0, math.sqrt(variance) / 255.0)


__all__ = [
    "QuantumResistanceManager",
    "QuantumThreat",
    "ThreatLevel",
    "VulnerabilityReport",
    "QuantumResistanceReport",
]

register_quantum_hook(QuantumResistanceManager())
