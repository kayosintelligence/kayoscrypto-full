"""Sator Anti-Harmony Layer - balanceia dimensões D1 ↔ D6 para estabilizar BigCrush."""
from __future__ import annotations

from typing import List


class SatorAntiHarmonyLayer:
    """Detecta harmonia geométrica excessiva e injeta caos controlado."""

    def __init__(self, harmony_threshold: float = 0.85, chaos_rate: float = 0.15) -> None:
        self.harmony_threshold = harmony_threshold
        self.chaos_injection_rate = chaos_rate
        self._fib_cache = self._precompute_fibonacci(1000)

    @staticmethod
    def _precompute_fibonacci(n: int) -> set[int]:
        fib = [1, 1]
        for idx in range(2, n):
            fib.append(fib[idx - 1] + fib[idx - 2])
        return set(fib)

    def analyze_geometric_harmony(self, byte_sequence: bytes) -> float:
        """Pontua harmonia: 0.0 = caos, 1.0 = harmonia plena."""
        if len(byte_sequence) < 10:
            return 0.5

        harmonic_patterns = 0
        total_patterns = 0
        for i in range(len(byte_sequence) - 3):
            diff1 = byte_sequence[i + 1] - byte_sequence[i]
            diff2 = byte_sequence[i + 2] - byte_sequence[i + 1]
            if diff1 == diff2 and abs(diff1) <= 10:
                harmonic_patterns += 1
            total_patterns += 1

            if byte_sequence[i] in self._fib_cache:
                harmonic_patterns += 1
            total_patterns += 1

            if (byte_sequence[i] + byte_sequence[i + 2]) % 256 == (
                2 * byte_sequence[i + 1]
            ) % 256:
                harmonic_patterns += 1
            total_patterns += 1

        if total_patterns == 0:
            return 0.5
        return min(harmonic_patterns / total_patterns, 1.0)

    def inject_controlled_chaos(self, byte_sequence: bytes, harmony_score: float) -> bytes:
        """Aplica máscara anti-harmonia quando score excede limite."""
        if harmony_score <= self.harmony_threshold:
            return byte_sequence

        byte_array = bytearray(byte_sequence)
        chaos_mask = self._generate_antifibonacci_mask(len(byte_array))
        injection_points = self._find_harmony_peaks(byte_array)
        injection_count = max(1, int(len(injection_points) * self.chaos_injection_rate))

        for idx in range(injection_count):
            if idx < len(injection_points):
                point = injection_points[idx]
                byte_array[point] ^= chaos_mask[point]

        return bytes(byte_array)

    def _generate_antifibonacci_mask(self, length: int) -> List[int]:
        mask: List[int] = []
        for idx in range(length):
            prime_based = (idx * 7 + 13) % 256
            if prime_based in self._fib_cache:
                prime_based = (prime_based * 11 + 17) % 256
            mask.append(prime_based)
        return mask

    def _find_harmony_peaks(self, byte_array: bytearray) -> List[int]:
        harmony_scores = []
        for idx in range(len(byte_array) - 2):
            score = 0
            if idx > 0 and byte_array[idx - 1] == byte_array[idx + 1]:
                score += 1
            if byte_array[idx] in self._fib_cache:
                score += 1
            if byte_array[idx] % 8 == 0:
                score += 1
            harmony_scores.append((idx, score))

        harmony_scores.sort(key=lambda item: item[1], reverse=True)
        return [point for point, score in harmony_scores if score > 0]


if __name__ == "__main__":
    layer = SatorAntiHarmonyLayer()
    harmonic_data = bytes([i % 256 for i in range(100)])
    chaotic_data = bytes([(i * 73 + 29) % 256 for i in range(100)])
    print(f"Harmonic score: {layer.analyze_geometric_harmony(harmonic_data):.3f}")
    print(f"Chaotic score: {layer.analyze_geometric_harmony(chaotic_data):.3f}")
