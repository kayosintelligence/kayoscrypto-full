"""Unit tests for the GeometricEntropyPool."""
from __future__ import annotations

from src.quantum.entropy_pool import EntropySource, GeometricEntropyPool


def test_seed_from_state_is_deterministic() -> None:
    pool = GeometricEntropyPool()
    tensor = {"avalanche": 0.48, "entropy": 0.83, "key_bits": 640}
    seed1 = pool.seed_from_state(tensor)
    seed2 = pool.seed_from_state(tensor)
    assert seed1 == seed2
    assert seed1  # non-empty


def test_mix_entropy_uses_permutations() -> None:
    pool = GeometricEntropyPool()
    src1 = EntropySource("fib", [0.1, 0.2, 0.3])
    src2 = EntropySource("eze", [0.4, 0.5, 0.6])
    mixed = pool.mix_entropy([src1, src2])
    assert mixed
    assert mixed != src1.as_array().tobytes()


def test_generate_quantum_safe_key_depends_on_context() -> None:
    pool = GeometricEntropyPool()
    ctx_a = {"entropy": 0.9, "key_bits": 768}
    ctx_b = {"entropy": 0.7, "key_bits": 512}
    key_a = pool.generate_quantum_safe_key(32, ctx_a)
    key_b = pool.generate_quantum_safe_key(32, ctx_b)
    assert len(key_a) == 32
    assert len(key_b) == 32
    assert key_a != key_b


def test_hook_updates_state() -> None:
    pool = GeometricEntropyPool()
    state = {"quantum_snapshot": {"key_length": 16, "entropy": 0.91}, "ciphertext": b"abc"}
    pool.update(state)
    entropy = state.get("quantum_entropy", {}).get("geometric_entropy_pool")
    assert entropy
    state2 = {"quantum_snapshot": {"key_length": 16, "entropy": 0.91}, "ciphertext": b"abc"}
    pool.update(state2)
    # Deterministic given same context
    assert state2["quantum_entropy"]["geometric_entropy_pool"] == entropy
