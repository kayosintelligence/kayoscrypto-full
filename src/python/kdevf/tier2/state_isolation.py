"""State isolation tests (Tier 2)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, List

import numpy as np


@dataclass
class StateIsolationResult:
    """Stores metrics for a state isolation run."""

    test_id: str
    timestamp: datetime
    num_states: int
    correlation_score: float
    prediction_accuracy: float
    passed: bool
    evidence: List[str] = field(default_factory=list)


class StateIsolationTest:
    """Validate that consecutive states remain statistically independent."""

    def __init__(self, trng_callable: Callable[[bytes, int], bytes]) -> None:
        self.trng = trng_callable
        self.results: List[StateIsolationResult] = []

    def execute(
        self,
        seed: bytes,
        num_states: int = 1000,
        state_size: int = 256,
    ) -> StateIsolationResult:
        print("\n" + "=" * 60)
        print("STATE ISOLATION TEST")
        print("=" * 60)
        print(f"States: {num_states}")
        print(f"State size: {state_size} bytes")
        print("=" * 60 + "\n")

        evidence: List[str] = []
        states: List[np.ndarray] = []

        for idx in range(num_states):
            derived_seed = seed + idx.to_bytes(4, "big")
            state = self.trng(derived_seed, state_size)
            states.append(np.frombuffer(state, dtype=np.uint8))

        correlations: List[float] = []
        for idx in range(len(states) - 1):
            corr_matrix = np.corrcoef(states[idx], states[idx + 1])
            corr_value = abs(corr_matrix[0, 1])
            correlations.append(corr_value)

        avg_correlation = float(np.mean(correlations))
        max_correlation = float(np.max(correlations))
        evidence.append(f"Average correlation: {avg_correlation:.6f}")
        evidence.append(f"Max correlation: {max_correlation:.6f}")
        evidence.append("Threshold: avg < 0.1 and max < 0.2")

        prediction_accuracies: List[float] = []
        for idx in range(100, len(states) - 1):
            current = states[idx]
            nxt = states[idx + 1]
            predicted = (current > 127).astype(int)
            actual = (nxt > 127).astype(int)
            prediction_accuracies.append(float(np.mean(predicted == actual)))

        avg_prediction = float(np.mean(prediction_accuracies)) if prediction_accuracies else 0.5
        evidence.append(f"Average prediction accuracy: {avg_prediction:.4f}")
        evidence.append("Expected random baseline: 0.50 ± 0.05")

        correlation_ok = avg_correlation < 0.1 and max_correlation < 0.2
        prediction_ok = 0.45 <= avg_prediction <= 0.55
        passed = correlation_ok and prediction_ok

        evidence.append("Correlation OK" if correlation_ok else "Correlation ABOVE threshold")
        evidence.append("Prediction OK" if prediction_ok else "Prediction OUTSIDE threshold")

        result = StateIsolationResult(
            test_id=f"ISOL-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            timestamp=datetime.now(),
            num_states=num_states,
            correlation_score=avg_correlation,
            prediction_accuracy=avg_prediction,
            passed=passed,
            evidence=evidence,
        )
        self.results.append(result)

        print("\n" + "=" * 60)
        print(f"RESULT: {'PASS' if passed else 'FAIL'}")
        print("=" * 60 + "\n")
        return result
