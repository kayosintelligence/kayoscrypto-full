"""Tests for the QuantumResistanceManager module."""
from __future__ import annotations

import pytest

from src.quantum.resistance_manager import (
    QuantumResistanceManager,
    QuantumThreat,
    ThreatLevel,
)


def test_compute_metrics_with_samples() -> None:
    manager = QuantumResistanceManager()
    snapshot = {
        "avalanche": 0.45,
        "entropy": 0.8,
        "key_bits": 640,
        "log_sensitivity": 0.15,
        "entropy_samples": [0.78, 0.82, 0.8],
    }
    metrics = manager.compute_metrics(snapshot)
    assert pytest.approx(metrics["entropy"], rel=1e-3) == 0.8
    assert "entropy_deviation" in metrics
    assert metrics["entropy_deviation"] >= 0.0


def test_assess_vulnerability_green_profile() -> None:
    manager = QuantumResistanceManager()
    snapshot = {
        "avalanche": 0.5,
        "entropy": 0.92,
        "key_bits": 768,
        "log_sensitivity": 0.05,
    }
    report = manager.assess_vulnerability(snapshot)
    assert report.overall_level() == ThreatLevel.GREEN
    payload = manager.build_report(report)
    assert payload["overall"] == ThreatLevel.GREEN.value
    suggestions = manager.recommend_improvements(report)
    assert suggestions == ["Maintain current parameters; quantum profile is stable."]


def test_assess_vulnerability_flags_risks() -> None:
    manager = QuantumResistanceManager()
    snapshot = {
        "avalanche": 0.18,
        "entropy": 0.52,
        "key_bits": 256,
        "log_sensitivity": 0.5,
    }
    report = manager.assess_vulnerability(snapshot)
    assert report.overall_level() == ThreatLevel.RED
    assert any(v.threat == QuantumThreat.SHOR and v.level == ThreatLevel.RED for v in report.vulnerabilities)
    assert any(v.threat == QuantumThreat.GROVER for v in report.vulnerabilities)
    suggestions = manager.recommend_improvements(report)
    assert suggestions  # there should be actionable items
