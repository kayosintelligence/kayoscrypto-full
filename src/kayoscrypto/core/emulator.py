"""QuantumEntropyEmulator: helper used during investor demos.

The emulator does not replace the production entropy pipeline. It simply wraps
``KayosCryptoUltimate`` so we can materialize deterministic entropy slices
on-demand during meetings without carrying the entire PractRand apparatus.
"""

from __future__ import annotations

import hashlib
import os
from typing import Optional

from core.kayoscrypto_ultimate import KayosCryptoUltimate


class QuantumEntropyEmulator:
    """Lightweight entropy surface for demos and quick verifications."""

    def __init__(
        self,
        *,
        block_size: int = 4096,
        level: int = 3,
        password: Optional[str] = None,
        use_quantum: bool = False,
    ) -> None:
        if block_size <= 0:
            raise ValueError("block_size must be positive")
        self.block_size = block_size
        self.level = level
        self.password = password or self._derive_default_password()
        self._seed = hashlib.sha256(b"KayosQuantumEntropyEmulator").digest()
        self._counter = 0
        self.engine = KayosCryptoUltimate(
            use_concentric=True,
            use_direction=True,
            use_quantum=use_quantum,
            quantum_entropy_mode="compatible",
        )

    def _derive_default_password(self) -> str:
        override = os.environ.get("KAYOS_EMULATOR_PASSWORD")
        if override:
            return override
        # Blend hostname + seed so multiple operators get unique streams.
        host = os.uname().nodename
        return hashlib.sha256(f"kayos-emulator::{host}".encode()).hexdigest()

    def _next_plaintext(self) -> bytes:
        counter_bytes = self._counter.to_bytes(16, "big")
        self._counter += 1
        repeats = self.block_size // len(self._seed) + 2
        buffer = (self._seed + counter_bytes) * repeats
        return buffer[: self.block_size]

    def generate_entropy(self, length: int = 1024) -> bytes:
        if length <= 0:
            raise ValueError("length must be positive")
        chunks = []
        produced = 0
        while produced < length:
            plaintext = self._next_plaintext()
            ciphertext = self.engine.encrypt(plaintext, self.password, level=self.level)
            if isinstance(ciphertext, dict):
                ciphertext = ciphertext["ciphertext"]
            chunks.append(ciphertext)
            produced += len(ciphertext)
        return b"".join(chunks)[:length]

    def healthcheck(self) -> dict:
        sample = self.generate_entropy(64)
        return {
            "status": "ok",
            "sample_hex": sample.hex(),
            "block_size": self.block_size,
            "level": self.level,
            "engine": "KayosCryptoUltimate",
        }

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return (
            "<QuantumEntropyEmulator block_size={block} level={level}"
            " counter={counter}>"
        ).format(block=self.block_size, level=self.level, counter=self._counter)
