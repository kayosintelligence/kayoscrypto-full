"""Geometric Entropy Pool for quantum-safe key derivation."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Dict, Iterable, List

import numpy as np

from . import register_quantum_hook


@dataclass
class EntropySource:
    name: str
    values: List[float]

    def as_array(self) -> np.ndarray:
        return np.array(self.values, dtype=np.float64)


class GeometricEntropyPool:
    """Combine geometric signals into deterministic quantum-safe entropy."""

    name = "geometric_entropy_pool"

    def __init__(self) -> None:
        self._last_seed: bytes | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def seed_from_state(self, tensor: Dict[str, float]) -> bytes:
        """Derive a deterministic seed from the Spine tensor state."""
        numeric_values = []
        for key in sorted(tensor.keys()):
            value = tensor.get(key, 0.0)
            if isinstance(value, (int, float)):
                numeric_values.append(float(value))
            elif isinstance(value, (bytes, bytearray)) and value:
                # Derive a deterministic scalar from byte-oriented signals.
                numeric_values.append(sum(value) / (len(value) * 255.0))
        if not numeric_values:
            return b""
        arr = np.array(numeric_values, dtype=np.float64)
        # Normalize to [0, 1) and scale
        normalized = np.mod(arr / (np.abs(arr).max() or 1.0), 1.0)
        angles = np.sin(np.arange(normalized.size) * np.pi / 4.0)
        mixed = normalized + angles
        mixed = np.roll(mixed, 1)
        return mixed.tobytes()

    def mix_entropy(self, sources: Iterable[EntropySource]) -> bytes:
        """Mix multiple sources using circular permutations only."""
        arrays = [source.as_array() for source in sources if source.values]
        if not arrays:
            return b""
        combined = arrays[0].copy()
        for i, array in enumerate(arrays[1:], start=1):
            shift = i % array.size
            combined = np.roll(combined, shift) + np.roll(array, -shift)
        combined = np.mod(combined, 1.0)
        return combined.tobytes()

    def generate_quantum_safe_key(self, length: int, context: Dict[str, float] | None = None) -> bytes:
        """Generate a deterministic quantum-safe key of the desired length."""
        context = context or {}
        seed = self.seed_from_state(context)
        if not seed:
            seed = self._last_seed or b""
        digest = hashlib.sha3_512(seed or b"kayos-quantum-entropy").digest()
        while len(digest) < length:
            digest += hashlib.sha3_512(digest).digest()
        key = digest[:length]
        return key

    # ------------------------------------------------------------------
    # Hook interface
    # ------------------------------------------------------------------
    def update(self, state: Dict[str, object]) -> None:
        snapshot = state.get("quantum_snapshot", {})
        if not isinstance(snapshot, dict):
            return
        key_length = int(snapshot.get("key_length", 64))
        context = dict(snapshot)
        if "ciphertext" in state:
            ciphertext = state["ciphertext"]
            if isinstance(ciphertext, (bytes, bytearray)):
                context["cipher_entropy"] = float(len(ciphertext)) / 1024.0
        entropy_key = self.generate_quantum_safe_key(key_length, context)
        state.setdefault("quantum_entropy", {})["geometric_entropy_pool"] = entropy_key.hex()
        if state.get("phase") == "encrypt":
            self._last_seed = self.seed_from_state(context)


__all__ = ["GeometricEntropyPool", "EntropySource"]

_POOL = GeometricEntropyPool()


class EntropyAliasHook:
    """Wrapper hook exposing GeometricEntropyPool as the generic "entropy" hook."""

    name = "entropy"

    def __init__(self, delegate: GeometricEntropyPool) -> None:
        self._delegate = delegate

    def update(self, state: Dict[str, object]) -> None:
        self._delegate.update(state)
        entropy_map = state.get("quantum_entropy", {})
        entropy_hex = None
        if isinstance(entropy_map, dict):
            entropy_hex = entropy_map.get("geometric_entropy_pool")
        snapshot = state.get("quantum_snapshot")
        highlighted_metrics = None
        if isinstance(snapshot, dict):
            highlighted_metrics = {
                key: snapshot.get(key)
                for key in ("avalanche", "entropy", "key_bits", "log_sensitivity")
                if key in snapshot
            }
        state[self.name] = {
            "entropy_hex": entropy_hex,
            "entropy_bytes": len(entropy_hex) // 2 if isinstance(entropy_hex, str) else None,
            "metrics": highlighted_metrics,
        }


register_quantum_hook(_POOL)
register_quantum_hook(EntropyAliasHook(_POOL))
