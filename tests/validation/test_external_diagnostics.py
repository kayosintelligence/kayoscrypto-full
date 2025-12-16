"""Regression tests for the external diagnostic/validation helpers."""

import json
import os
import subprocess
import sys
from pathlib import Path

from python.diagnostics import EmulatorDiagnosticsSuite, QuantumValidationEngine

from kayoscrypto.mpcn.guard import MPCNGuardAlert, enforce_guardian


REQUIRED_MPCN_INSTRUCTIONS = [
    "GLASSE-32GB",
    "BATTERY-DIEHARDER",
    "BATTERY-BIGCRUSH",
    "LANG-PT-BR",
]

try:
    enforce_guardian(
        actor="pytest_external_diagnostics",
        intent="tests.validation.external",
        required_instruction_ids=REQUIRED_MPCN_INSTRUCTIONS,
        max_inactive_minutes=60,
        fail_on_warnings=False,
    )
except MPCNGuardAlert as exc:
    raise RuntimeError(
        "Guardião MPC-N bloqueou os testes de validação externa; execute tools/mpcn_guard.py antes."
    ) from exc


def _write_entropy_fixture(path: Path, cycles: int = 4) -> None:
    path.write_bytes(bytes(range(256)) * cycles)


def test_quantum_validation_engine_reports_metrics(tmp_path):
    entropy_file = tmp_path / "entropy.bin"
    _write_entropy_fixture(entropy_file, cycles=8)

    practrand_log = tmp_path / "practrand.log"
    practrand_log.write_text(
        "rng=RNG_stdin32, seed=unknown\n"
        "length= 16 kilobytes (2^14 bytes)\n"
        "  Test Name                         Raw       Processed     Evaluation\n"
        "  [Low8/32]Gap-16:A                 R=  +4.9  p =  5.6e-4   unusual\n"
    )

    engine = QuantumValidationEngine(entropy_file, practrand_log)
    report = engine.evaluate(sample_bytes=4096)

    assert report.entropy_path == entropy_file
    assert len(report.metrics) == 3
    assert report.metrics[0].name == "Fibonacci Direction Alignment"
    assert "spectral=" in report.metrics[0].details
    assert any("p =" in line for line in report.anomalies)
    assert isinstance(report.passed, bool)


def test_emulator_diagnostics_suite_segments_pipeline(tmp_path):
    entropy_file = tmp_path / "entropy.bin"
    _write_entropy_fixture(entropy_file, cycles=16)

    suite = EmulatorDiagnosticsSuite(entropy_file)
    report = suite.evaluate(sample_bytes=4096)

    assert len(report.subsystems) == 4
    assert {subsystem.name for subsystem in report.subsystems} == {
        "Ring Oscillator",
        "Thermal Noise",
        "Clock Jitter",
        "Conditioning",
    }
    assert report.passed in {True, False}


def test_quantum_engine_accepts_ascii_bitstreams(tmp_path):
    entropy_file = tmp_path / "entropy_ascii.txt"
    entropy_file.write_text("01" * 512)

    engine = QuantumValidationEngine(entropy_file)
    report = engine.evaluate(sample_bytes=1024)

    assert report.metrics[0].threshold == 0.35
    assert len(report.anomalies) == 0


def test_cli_outputs_json_report(tmp_path):
    entropy_file = tmp_path / "entropy.bin"
    _write_entropy_fixture(entropy_file, cycles=4)

    env = os.environ.copy()
    src_path = Path(__file__).resolve().parents[2] / "src"
    env["PYTHONPATH"] = os.pathsep.join(
        part for part in (str(src_path), env.get("PYTHONPATH")) if part
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "python.diagnostics.cli",
            str(entropy_file),
            "--sample-bytes",
            "1024",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )

    payload = json.loads(result.stdout)
    assert "quantum" in payload
    assert "emulator" in payload
    assert payload["quantum"]["metrics"]
