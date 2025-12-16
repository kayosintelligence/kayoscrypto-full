import json
import os
import subprocess
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import numpy as np
import pytest

from python.quantum_optimization import QuantumOptimizationPipeline


def test_pipeline_improves_alignment_when_needed():
    data = np.linspace(0, 255, num=1024, dtype=np.uint8)
    pipeline = QuantumOptimizationPipeline()
    result = pipeline.optimize_entropy_stream(data.tobytes())

    assert result.optimization_applied in {True, False}
    assert result.optimized_alignment >= 0.0
    assert isinstance(result.optimized_stream, bytes)
    assert result.effective_threshold > 0.0
    assert result.raw_variance >= 0.0

    if result.optimization_applied:
        assert result.optimized_alignment >= result.original_alignment


def test_pipeline_forces_correction_on_perfect_alignment():
    data = np.full(2048, 187, dtype=np.uint8)
    pipeline = QuantumOptimizationPipeline()
    result = pipeline.optimize_entropy_stream(data.tobytes())

    assert result.optimization_applied is True
    assert result.optimized_alignment > result.original_alignment
    assert result.artifact_detected is True


def test_adaptive_threshold_detects_real_variance():
    rng = np.random.default_rng(0)
    data = rng.integers(0, 256, size=4096, dtype=np.uint8)
    pipeline = QuantumOptimizationPipeline()
    analysis = pipeline.optimizer.analyze_fibonacci_pattern(data)

    assert analysis.raw_variance >= pipeline.optimizer.high_variance_cutoff
    assert pytest.approx(0.62, rel=1e-6) == analysis.effective_threshold


def test_cli_optimize_fibonacci_generates_output(tmp_path):
    entropy_file = tmp_path / "entropy.bin"
    entropy_file.write_bytes(bytes(range(256)) * 8)
    output_file = tmp_path / "optimized.bin"

    env = os.environ.copy()
    src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [src_path, env.get("PYTHONPATH")]))

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "python.diagnostics.cli",
            "optimize-fibonacci",
            str(entropy_file),
            "--output",
            str(output_file),
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )

    assert output_file.exists()
    payload = json.loads(result.stdout)
    assert "optimized_alignment" in payload
    assert "optimization_applied" in payload
    assert "effective_threshold" in payload
