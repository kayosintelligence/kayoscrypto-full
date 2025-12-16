"""Enhanced pipeline connecting Fibonacci optimization to Sator layers."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np

from kayoscrypto.enhanced_trng import KayosCryptoEnhanced

from .fibonacci_corrector import FibonacciAlignmentCorrector
from .fibonacci_optimizer import FibonacciAlignmentOptimizer


class EnhancedQuantumPipeline:
    """Applies Fibonacci optimizer, corrector and Sator engineering layers."""

    def __init__(self, use_sator_enhancements: bool = True) -> None:
        self.use_enhancements = use_sator_enhancements
        self.optimizer = FibonacciAlignmentOptimizer()
        self.corrector = FibonacciAlignmentCorrector(self.optimizer)
        self.enhancer = KayosCryptoEnhanced(use_enhancements=use_sator_enhancements)
        self.stats = {
            "total_bytes": 0,
            "chunks_processed": 0,
            "sator_enhancements": 0,
        }

    def optimize_entropy_stream(
        self,
        data: bytes,
        *,
        target_alignment: float = 0.35,
        apply_correction: bool = True,
    ) -> Tuple[bytes, Dict[str, float]]:
        """Run Fibonacci optimization followed by Sator layers."""
        metrics: Dict[str, float] = {}
        entropy_array = np.frombuffer(data, dtype=np.uint8)
        analysis = self.optimizer.analyze_fibonacci_pattern(entropy_array)
        alignment = analysis.current_alignment
        metrics["original_alignment"] = alignment

        processed = data
        if apply_correction and alignment < target_alignment:
            processed = self.corrector.apply_fibonacci_correction(data, analysis)
            corrected_alignment = self.optimizer.calculate_alignment(
                np.frombuffer(processed, dtype=np.uint8)
            )
            metrics["corrected_alignment"] = corrected_alignment
        else:
            metrics["corrected_alignment"] = alignment

        if self.use_enhancements:
            enhanced = self.enhancer.enhance_entropy_stream(processed)
            if enhanced is not processed:
                metrics["sator_enhancement"] = 1
                processed = enhanced
                self.stats["sator_enhancements"] += 1
            else:
                metrics["sator_enhancement"] = 0
        else:
            metrics["sator_enhancement"] = 0

        final_alignment = self.optimizer.calculate_alignment(
            np.frombuffer(processed, dtype=np.uint8)
        )
        metrics["final_alignment"] = final_alignment
        metrics["last_harmony_score"] = self.enhancer.get_enhancement_metrics()[
            "last_harmony_score"
        ]

        self.stats["total_bytes"] += len(processed)
        self.stats["chunks_processed"] += 1
        return processed, metrics

    def process_entropy_file(
        self,
        input_path: Path,
        output_path: Path,
        *,
        chunk_size: int = 1_048_576,
    ) -> Dict[str, float]:
        """Stream files through Fibonacci + Sator pipeline."""
        total_metrics = {
            "chunks": 0,
            "sator_chunks": 0,
            "bytes": 0,
        }
        with open(input_path, "rb") as src, open(output_path, "wb") as dst:
            while True:
                chunk = src.read(chunk_size)
                if not chunk:
                    break
                processed, chunk_metrics = self.optimize_entropy_stream(chunk)
                dst.write(processed)
                total_metrics["chunks"] += 1
                total_metrics["bytes"] += len(chunk)
                if chunk_metrics.get("sator_enhancement"):
                    total_metrics["sator_chunks"] += 1
        return total_metrics

    def reset_statistics(self) -> None:
        self.stats = {"total_bytes": 0, "chunks_processed": 0, "sator_enhancements": 0}
        self.enhancer.reset_metrics()


if __name__ == "__main__":
    pipeline = EnhancedQuantumPipeline()
    test_data = bytes([(i * 5 + 11) % 256 for i in range(5000)])
    processed, info = pipeline.optimize_entropy_stream(test_data)
    print(f"Processed {len(processed)} bytes")
    print(info)
