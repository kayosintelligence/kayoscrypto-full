#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes de segurança focados no pipeline quântico."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

# Ajustar caminho para importar módulos do src
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))

from core.quantum.certification_tracker import CertificationTracker  # noqa: E402
from core.quantum.geometric_entropy_pool import GeometricEntropyPool  # noqa: E402


@pytest.fixture
def tmp_snapshot_dir(tmp_path: Path) -> Path:
    """Retorna diretório temporário para snapshots de certificação."""
    return tmp_path / "cert_snapshots"


def test_certification_tracker_updates_with_scorecard(tmp_snapshot_dir: Path) -> None:
    tracker = CertificationTracker()
    tmp_snapshot_dir.mkdir(parents=True, exist_ok=True)
    tracker.SNAPSHOT_DIR = tmp_snapshot_dir

    metrics = {
        'avalanche': 0.52,
        'entropy': 0.91,
        'key_bits': 768.0,
        'log_sensitivity': 0.18,
    }
    scorecard = {
        'phase_scores': {'fibonacci': 0.92, 'ezekiel': 0.9, 'core': 0.78},
        'threat_scores': {'shor': 0.93, 'grover': 0.88, 'entropy': 0.9, 'sensitivity': 0.81},
        'composite_score': 0.885,
        'readiness_index': 0.885,
        'target_delta': 0.065,
        'semaphore': '',
        'generated_at': '2025-11-16T12:00:00Z',
    }
    findings = ["Sensibilidade logarítmica dentro da meta", "Core abaixo de 0.80 requer reforço"]

    snapshot = tracker.update_from_assurance(
        metrics,
        performance_kbps=640.0,
        scorecard=scorecard,
        findings=findings,
        suggestions=["Aumentar key stretching", "Rodar NIST SP 800-22"],
    )

    assert pytest.approx(tracker.current_state['quantum_resistance'], rel=1e-6) == scorecard['readiness_index']
    assert tracker.current_state['performance'] == pytest.approx(1.0)
    assert 'scorecard' in snapshot and snapshot['scorecard']['semaphore'] == ''
    assert snapshot['target_delta'] == scorecard['target_delta']
    assert snapshot['findings'] == findings

    files = list(tmp_snapshot_dir.glob('cert_snapshot_*.json'))
    assert len(files) == 1
    saved = json.loads(files[0].read_text(encoding='utf-8'))
    assert saved['scorecard']['target_delta'] == scorecard['target_delta']
    assert saved['findings'] == findings


def test_geometric_entropy_pool_entropy_quality() -> None:
    pool = GeometricEntropyPool()
    key = pool.generate_quantum_safe_key(32)
    entropy_bits = pool.calculate_entropy_bits(key)

    assert len(key) == 32
    max_entropy = len(key) * 8
    assert entropy_bits >= max_entropy * 0.85


