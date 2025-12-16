"""KayosCryptoEnhanced aplica camadas Sator sobre fluxos de entropia."""
from __future__ import annotations

from typing import Optional

from kayoscrypto.enhanced_layers.hamming_decorrelator import HammingDecorrelator
from kayoscrypto.enhanced_layers.sator_anti_harmony import SatorAntiHarmonyLayer


class KayosCryptoEnhanced:
    """Conecta Anti-Harmony + Hamming Decorrelator para corrigir BigCrush."""

    def __init__(self, use_enhancements: bool = True) -> None:
        self.use_enhancements = use_enhancements
        self.anti_harmony_layer = SatorAntiHarmonyLayer()
        self.hamming_decorrelator = HammingDecorrelator()
        self._last_harmony_score: float = 0.5
        self._enhancement_count = 0

    def enhance_entropy_stream(self, input_bytes: bytes, source_info: Optional[str] = None) -> bytes:
        """Aplica camadas Sator quando stream apresenta harmonia/ correlação."""
        if not self.use_enhancements or len(input_bytes) < 100:
            return input_bytes

        processed = input_bytes
        harmony_score = self.anti_harmony_layer.analyze_geometric_harmony(processed)
        self._last_harmony_score = harmony_score
        if harmony_score > 0.7:
            processed = self.anti_harmony_layer.inject_controlled_chaos(processed, harmony_score)
            self._enhancement_count += 1

        if len(processed) >= 300:
            processed = self.hamming_decorrelator.decorrelate_hamming_sequences(processed)
            self._enhancement_count += 1

        return processed

    def get_enhancement_metrics(self) -> dict:
        return {
            "enhancements_applied": self._enhancement_count,
            "last_harmony_score": self._last_harmony_score,
            "enhancement_enabled": self.use_enhancements,
        }

    def reset_metrics(self) -> None:
        self._enhancement_count = 0
        self._last_harmony_score = 0.5


if __name__ == "__main__":
    system = KayosCryptoEnhanced()
    pattern = bytes([(i * 3 + 7) % 256 for i in range(1000)])
    enhanced = system.enhance_entropy_stream(pattern)
    print(f"Bytes processados: {len(enhanced)}")
    print(system.get_enhancement_metrics())