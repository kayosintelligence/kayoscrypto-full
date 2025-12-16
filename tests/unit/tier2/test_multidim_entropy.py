"""Unit tests for the MultiDimEntropyTest harness."""
from __future__ import annotations

import hashlib

from python.kdevf.tier2.multidim_entropy import MultiDimEntropyTest


def pseudo_trng(seed: bytes, length: int) -> bytes:
    """Deterministic byte stream derived from SHA-256 chaining."""
    output = bytearray()
    counter = 0
    while len(output) < length:
        digest = hashlib.sha256(seed + counter.to_bytes(4, "big")).digest()
        output.extend(digest)
        counter += 1
    return bytes(output[:length])


def test_multidimensional_entropy_passes_for_uniform_like_stream():
    tester = MultiDimEntropyTest(pseudo_trng)
    result = tester.execute(seed=b"kayos-tier2", dimensions=4, samples=500)

    assert result.dimensions == 4
    assert result.samples == 500
    assert 0.0 <= result.uniformity_score <= 1.0
    assert result.clustering_score > 0.01
    assert result.passed is True