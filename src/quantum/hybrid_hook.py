from __future__ import annotations

from typing import Any, Dict

from . import register_quantum_hook

try:  # Optional dependency: hybrid key exchange rib
    from core.hybrid_key_exchange import HybridKeyExchange
except ImportError:  # pragma: no cover - environment without hybrid rib
    HybridKeyExchange = None  # type: ignore[assignment]


class HybridTelemetryHook:
    """Expose HybridKeyExchange readiness as a quantum assurance hook."""

    name = "hybrid"

    def __init__(self) -> None:
        self._engine: HybridKeyExchange | None = None  # type: ignore[assignment]
        self._error: str | None = None

    def _ensure_engine(self) -> None:
        if self._engine is not None or self._error is not None:
            return
        if HybridKeyExchange is None:
            self._error = "hybrid_engine_missing"
            return
        try:
            self._engine = HybridKeyExchange(
                use_kyber=True,
                use_ecdh=True,
                use_fibonacci=True,
            )
        except Exception as exc:  # pragma: no cover - instantiation failures
            self._error = str(exc)
            self._engine = None

    def update(self, state: Dict[str, Any]) -> None:
        self._ensure_engine()

        info: Dict[str, Any] = {}
        if self._error:
            info["status"] = "unavailable"
            info["detail"] = self._error
        elif self._engine is None:
            info["status"] = "uninitialized"
        else:
            stats = self._engine.get_stats()
            snapshot = state.get("quantum_snapshot")
            key_bits = None
            if isinstance(snapshot, dict):
                key_bytes = snapshot.get("key_bytes")
                if isinstance(key_bytes, (bytes, bytearray)):
                    key_bits = len(key_bytes) * 8
            info.update(
                status="ready",
                algorithms={
                    "kyber": self._engine.use_kyber,
                    "ecdh": self._engine.use_ecdh,
                    "fibonacci": self._engine.use_fibonacci,
                },
                stats=stats,
            )
            if key_bits is not None:
                info["key_bits_detected"] = key_bits
        state[self.name] = info


register_quantum_hook(HybridTelemetryHook())
