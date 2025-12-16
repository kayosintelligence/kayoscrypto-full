"""Hamming Decorrelator - reduz correlações sutis detectadas pelo BigCrush."""
from __future__ import annotations

from typing import List

import numpy as np


class HammingDecorrelator:
    """Aplica transformações leves quando correlações de Hamming aparecem."""

    def __init__(self, window_size: int = 300, correlation_threshold: float = 0.05) -> None:
        self.window_size = window_size
        self.correlation_threshold = correlation_threshold

    def decorrelate_hamming_sequences(self, byte_stream: bytes) -> bytes:
        """Processa janelas sobrepostas e quebra padrões fortemente correlacionados."""
        if len(byte_stream) < self.window_size:
            return byte_stream

        decorrelated = bytearray(byte_stream)
        step_size = max(10, self.window_size // 3)
        processed_keys = set()

        for start in range(0, len(byte_stream) - self.window_size + 1, step_size):
            window = byte_stream[start : start + self.window_size]
            key = start // step_size
            if key in processed_keys:
                continue
            processed_keys.add(key)

            weights = [self._hamming_weight(value) for value in window]
            if self._has_subtle_correlation(weights):
                transformed = self._apply_hamming_shuffle(window)
                decorrelated[start : start + self.window_size] = transformed

        return bytes(decorrelated)

    @staticmethod
    def _hamming_weight(value: int) -> int:
        return bin(value).count("1")

    def _has_subtle_correlation(self, weights: List[int]) -> bool:
        if len(weights) < 10:
            return False
        correlations: List[float] = []
        for lag in (1, 2, 3, 5, 8):
            if lag >= len(weights):
                continue
            first = weights[:-lag]
            second = weights[lag:]
            if len(first) < 2:
                continue
            matrix = np.corrcoef(first, second)
            coeff = matrix[0, 1]
            if not np.isnan(coeff):
                correlations.append(abs(float(coeff)))
        return bool(correlations) and max(correlations) > self.correlation_threshold

    def _apply_hamming_shuffle(self, window: bytes) -> bytes:
        shuffled = bytearray(window)
        for idx in range(0, len(shuffled), 7):  # passo primo para evitar padrões óbvios
            original = shuffled[idx]
            reversed_bits = int(f"{original:08b}"[::-1], 2)
            shuffled[idx] = reversed_bits
        for idx in range(1, len(shuffled) - 1, 2):
            if (shuffled[idx - 1] ^ shuffled[idx + 1]) % 2 == 0:
                shuffled[idx - 1], shuffled[idx] = shuffled[idx], shuffled[idx - 1]
        return bytes(shuffled)


if __name__ == "__main__":
    decorrelator = HammingDecorrelator()
    correlated = bytes([(i % 4) * 64 + (i % 16) for i in range(400)])
    result = decorrelator.decorrelate_hamming_sequences(correlated)
    print(f"Modified bytes: {sum(a != b for a, b in zip(correlated, result))}")
