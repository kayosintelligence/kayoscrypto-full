"""Quantum Assurance package for KayosCrypto."""
from __future__ import annotations

from typing import Dict, Protocol, runtime_checkable


@runtime_checkable
class QuantumHook(Protocol):
    """Interface for optional quantum assurance modules."""

    name: str

    def update(self, state: dict) -> None:
        """Update hook state with the latest cipher snapshot."""


_registry: Dict[str, QuantumHook] = {}


def register_quantum_hook(hook: QuantumHook) -> None:
    """Register a quantum assurance hook by its name."""
    _registry[hook.name] = hook


def get_quantum_hook(name: str) -> QuantumHook | None:
    """Return a registered hook by name."""
    return _registry.get(name)


def available_hooks() -> Dict[str, QuantumHook]:
    """Return all registered quantum hooks."""
    return dict(_registry)


try:  # Preload default hooks (side effects register them)
    from . import entropy_pool  # noqa: F401
    from . import resistance_manager  # noqa: F401
    from . import hybrid_hook  # noqa: F401
except ImportError:
    pass
