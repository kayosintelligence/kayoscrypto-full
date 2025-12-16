#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parity tests between Python and Cython entropy pool implementations."""

import sys
from pathlib import Path

import pytest

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from core.quantum.entropy_pool import GeometricEntropyPoolPython  # noqa: E402

try:  # noqa: E402
    from src.core.quantum.entropy_pool_optimized import GeometricEntropyPoolOptimized  # type: ignore
except ImportError:  # pragma: no cover - Cython build não disponível
    GeometricEntropyPoolOptimized = None


@pytest.mark.skipif(
    GeometricEntropyPoolOptimized is None,
    reason="Cython entropy pool build não disponível",
)
def test_python_cython_key_parity():
    """Verifica se as chaves geradas são idênticas para seeds fixas."""
    python_pool = GeometricEntropyPoolPython()
    cython_pool = GeometricEntropyPoolOptimized()

    seeds = [
        b"seed_parity_test_01",
        b"seed_parity_test_02",
        b"seed_parity_test_03",
    ]
    lengths = [32, 128, 512]

    for seed in seeds:
        for length in lengths:
            py_key = python_pool.generate_quantum_safe_key(length, seed)
            cy_key = cython_pool.generate_quantum_safe_key(length, seed)
            assert py_key == cy_key, (
                f"Chave divergente para seed {seed!r} e length {length}"
            )


@pytest.mark.skipif(
    GeometricEntropyPoolOptimized is None,
    reason="Cython entropy pool build não disponível",
)
def test_python_cython_source_analysis_parity():
    """Garante que métricas de fontes de entropia permaneçam alinhadas."""
    python_pool = GeometricEntropyPoolPython()
    cython_pool = GeometricEntropyPoolOptimized()

    py_sources = python_pool.analyze_sources(length=2048)
    cy_sources = cython_pool.analyze_sources(length=2048)

    assert len(py_sources) == len(cy_sources) == 4

    def _normalize(text: str) -> str:
        normalized = text.replace(" [OPTIMIZED]", "")
        normalized = normalized.replace(" + Lookup Tables", "")
        normalized = normalized.replace(" + lookup tables", "")
        return normalized.strip()

    for py_source, cy_source in zip(py_sources, cy_sources):
        assert _normalize(py_source.name) == _normalize(cy_source.name)
        assert _normalize(py_source.method) == _normalize(cy_source.method)
    assert pytest.approx(py_source.entropy_bits, rel=1e-6, abs=1e-6) == cy_source.entropy_bits