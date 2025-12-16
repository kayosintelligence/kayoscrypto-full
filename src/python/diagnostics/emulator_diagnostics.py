"""Diagnostic helpers for the KayosCrypto TRNG emulator.

The intent of this module is to keep the TRNG emulator health checks close to
our reference Python tooling so CI/CD pipelines and manual investigations share
exactly the same heuristics. The diagnostics reflect the canonical pipeline:
ring oscillators → thermal noise → clock jitter → conditioning network.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Mapping, MutableMapping, Optional, Sequence

import numpy as np


@dataclass(frozen=True)
class SubsystemHealth:
    """Health score produced for one subsystem."""

    name: str
    stability: float
    noise_floor: float
    confidence: float
    status: str
    diagnostics: str


@dataclass(frozen=True)
class EmulatorDiagnosticsReport:
    """Aggregate health snapshot covering every subsystem."""

    entropy_path: Path
    subsystems: Sequence[SubsystemHealth]

    @property
    def passed(self) -> bool:
        return all(subsystem.status == "pass" for subsystem in self.subsystems)


class EmulatorDiagnosticsSuite:
    """Analyzes entropy captures with emulator-specific heuristics."""

    def __init__(
        self,
        entropy_path: Path,
        telemetry: Optional[Mapping[str, Sequence[float]]] = None,
    ) -> None:
        self.entropy_path = Path(entropy_path)
        self.telemetry: Mapping[str, Sequence[float]] = telemetry or {}

    def evaluate(self, sample_bytes: int = 131_072) -> EmulatorDiagnosticsReport:
        raw_series = self._load_entropy_window(sample_bytes)
        slices = self._segment_series(raw_series)
        subsystems = [
            self._score_subsystem("Ring Oscillator", slices["ring"]),
            self._score_subsystem("Thermal Noise", slices["thermal"]),
            self._score_subsystem("Clock Jitter", slices["jitter"]),
            self._score_subsystem("Conditioning", slices["conditioning"]),
        ]
        return EmulatorDiagnosticsReport(entropy_path=self.entropy_path, subsystems=tuple(subsystems))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _load_entropy_window(self, sample_bytes: int) -> np.ndarray:
        if not self.entropy_path.exists():
            raise FileNotFoundError(self.entropy_path)

        raw = self.entropy_path.read_bytes()
        if not raw:
            raise ValueError("Entropy capture is empty")

        raw = raw[:sample_bytes] if sample_bytes else raw
        return np.frombuffer(raw, dtype=np.uint8).astype(np.float64)

    def _segment_series(self, series: np.ndarray) -> MutableMapping[str, np.ndarray]:
        if len(series) < 64:
            raise ValueError("Entropy capture too small for diagnostics")

        segments: MutableMapping[str, np.ndarray] = {
            "ring": series[0::4],
            "thermal": series[1::4],
            "jitter": series[2::4],
            "conditioning": series[3::4],
        }
        for name, override in self.telemetry.items():
            if name in segments and override:
                segments[name] = np.asarray(override, dtype=np.float64)
        return segments

    def _score_subsystem(self, name: str, samples: np.ndarray) -> SubsystemHealth:
        if samples.size < 16:
            raise ValueError(f"Subsystem {name} received insufficient samples")

        normalized = samples / 255.0
        stability = 1.0 - float(np.abs(np.mean(normalized) - 0.5) * 2)
        noise_floor = float(np.std(normalized))
        crest_factor = float(np.max(normalized) / (np.mean(normalized) + 1e-6))
        confidence = float(max(0.0, 1.0 - abs(crest_factor - 1.8) / 1.8))

        passing = stability >= 0.70 and 0.04 <= noise_floor <= 0.32 and confidence >= 0.55
        status = "pass" if passing else "investigate"
        diagnostics = (
            f"mean={np.mean(normalized):.4f}, std={noise_floor:.4f}, "
            f"crest={crest_factor:.3f}, stability={stability:.3f}, confidence={confidence:.3f}"
        )
        return SubsystemHealth(
            name=name,
            stability=stability,
            noise_floor=noise_floor,
            confidence=confidence,
            status=status,
            diagnostics=diagnostics,
        )