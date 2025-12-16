"""Command-line interface for KayosCrypto diagnostic helpers."""

from __future__ import annotations

import argparse
import json
import tempfile
from dataclasses import asdict
import sys
from pathlib import Path
from typing import Any, Dict, Sequence

from .emulator_diagnostics import EmulatorDiagnosticsSuite
from .quantum_validation import QuantumValidationEngine
from python.quantum_optimization import QuantumOptimizationPipeline


def _report_to_dict(report: Any) -> Dict[str, Any]:
    """Serialize diagnostic reports into JSON-friendly structures."""

    if hasattr(report, "metrics"):
        return {
            "entropy_path": str(report.entropy_path),
            "practrand_log": str(report.practrand_log) if report.practrand_log else None,
            "metrics": [asdict(metric) for metric in report.metrics],
            "anomalies": list(report.anomalies),
            "passed": report.passed,
        }

    if hasattr(report, "subsystems"):
        return {
            "entropy_path": str(report.entropy_path),
            "subsystems": [asdict(subsystem) for subsystem in report.subsystems],
            "passed": report.passed,
        }

    raise TypeError(f"Unsupported report type: {type(report)!r}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run KayosCrypto quantum/emulator diagnostics over entropy captures",
    )
    parser.add_argument("entropy", type=Path, help="Path to the entropy capture (binary or ASCII bits)")
    parser.add_argument(
        "--practrand-log",
        type=Path,
        help="Optional PractRand/TestU01 log for anomaly extraction",
    )
    parser.add_argument(
        "--sample-bytes",
        type=int,
        default=262_144,
        help="Number of bytes to analyze (default: 262144)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit structured JSON instead of human-readable text",
    )
    parser.add_argument(
        "--no-emulator",
        action="store_true",
        help="Skip emulator diagnostics and run only quantum validation",
    )
    parser.add_argument(
        "--no-quantum",
        action="store_true",
        help="Skip quantum validation and run only emulator diagnostics",
    )
    return parser


def build_optimize_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="optimize-fibonacci",
        description="Optimize Fibonacci alignment on an entropy capture",
    )
    parser.add_argument("entropy", type=Path, help="Entropy capture to optimize")
    parser.add_argument("--output", "-o", type=Path, help="Where to store the optimized stream")
    parser.add_argument(
        "--context",
        default="cli",
        help="Optional label recorded with the optimization history",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run quantum validation over the optimized output",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON payload for automation",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    else:
        argv = list(argv)
    if argv and argv[0] == "optimize-fibonacci":
        return _run_optimize(argv[1:])

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.no_emulator and args.no_quantum:
        parser.error("Both --no-emulator and --no-quantum flags are set; nothing to run")

    entropy_path: Path = args.entropy
    if not entropy_path.exists():
        parser.error(f"Entropy capture not found: {entropy_path}")

    outputs: Dict[str, Any] = {}

    if not args.no_quantum:
        q_engine = QuantumValidationEngine(entropy_path, args.practrand_log)
        q_report = q_engine.evaluate(sample_bytes=args.sample_bytes)
        outputs["quantum"] = _report_to_dict(q_report)

    if not args.no_emulator:
        e_suite = EmulatorDiagnosticsSuite(entropy_path)
        e_report = e_suite.evaluate(sample_bytes=args.sample_bytes)
        outputs["emulator"] = _report_to_dict(e_report)

    if args.json:
        print(json.dumps(outputs, indent=2))
    else:
        if "quantum" in outputs:
            q = outputs["quantum"]
            print("=== Quantum Validation ===")
            for metric in q["metrics"]:
                print(
                    f"- {metric['name']}: {metric['score']:.3f} "
                    f"(threshold {metric['threshold']}) -> {metric['status']}"
                )
            print(f"Anomalies: {len(q['anomalies'])}")
            if q["anomalies"]:
                for line in q["anomalies"][:3]:
                    print(f"  {line}")
            print()
        if "emulator" in outputs:
            e = outputs["emulator"]
            print("=== Emulator Diagnostics ===")
            for subsystem in e["subsystems"]:
                print(
                    f"- {subsystem['name']}: {subsystem['status']} "
                    f"[{subsystem['diagnostics']}]"
                )
            print(f"Overall passed: {e['passed']}")
    return 0


def _run_optimize(argv: Sequence[str]) -> int:
    parser = build_optimize_parser()
    args = parser.parse_args(argv)

    if not args.entropy.exists():
        parser.error(f"Entropy capture not found: {args.entropy}")

    entropy_bytes = args.entropy.read_bytes()
    pipeline = QuantumOptimizationPipeline()
    result = pipeline.optimize_entropy_stream(
        entropy_bytes,
        context=args.context,
        force_correction=True,
    )

    if args.output:
        args.output.write_bytes(result.optimized_stream)

    validation_summary: Dict[str, Any] | None = None
    if args.validate:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(result.optimized_stream)
            tmp_path = Path(tmp.name)
        try:
            validation = QuantumValidationEngine(tmp_path)
            v_report = validation.evaluate(sample_bytes=min(len(result.optimized_stream), 262_144))
            validation_summary = {
                "passed": v_report.passed,
                "metrics": [asdict(metric) for metric in v_report.metrics],
            }
        finally:
            tmp_path.unlink(missing_ok=True)

    payload = {
        "original_alignment": result.original_alignment,
        "optimized_alignment": result.optimized_alignment,
        "improvement": result.improvement,
        "optimization_applied": result.optimization_applied,
        "validation_passed": result.validation_passed,
        "recommendations": result.recommendations,
        "effective_threshold": result.effective_threshold,
        "raw_variance": result.raw_variance,
        "artifact_detected": result.artifact_detected,
    }
    if validation_summary:
        payload["validation"] = validation_summary

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print("=== Fibonacci Alignment Optimization ===")
        print(f"Original alignment: {result.original_alignment:.6f}")
        print(f"Optimized alignment: {result.optimized_alignment:.6f}")
        print(f"Improvement: {result.improvement:.6f}")
        print(f"Optimization applied: {result.optimization_applied}")
        print(f"Validation passed: {result.validation_passed}")
        print(f"Effective threshold: {result.effective_threshold:.3f}")
        print(f"Raw variance: {result.raw_variance:.2f}")
        print(f"Artifact detected: {result.artifact_detected}")
        if result.recommendations:
            print("Recommendations: " + ", ".join(result.recommendations))
        if validation_summary:
            print("Validation metrics:")
            for metric in validation_summary["metrics"]:
                print(
                    f"- {metric['name']}: {metric['score']:.3f} "
                    f"(threshold {metric['threshold']}) -> {metric['status']}"
                )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
