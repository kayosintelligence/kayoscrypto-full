"""Persistent cognitive memory (MPC-N) utilities for KayosCrypto.

This module provides a tiny structured layer that every agent can use to
load/save context and keep a verifiable trail of instructions, tasks, and
history.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

ROOT_DIR = Path(__file__).resolve().parents[3]
DEFAULT_STATE_PATH = ROOT_DIR / "mpcn_state.json"


@dataclass
class MPCNEvent:
    """Single timeline event recorded in the MPC-N state."""

    timestamp: str
    actor: str
    action: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "actor": self.actor,
            "action": self.action,
            "details": self.details,
        }

    @staticmethod
    def from_dict(payload: Dict[str, Any]) -> "MPCNEvent":
        return MPCNEvent(
            timestamp=payload.get("timestamp", ""),
            actor=payload.get("actor", "unknown"),
            action=payload.get("action", ""),
            details=payload.get("details", {}),
        )


@dataclass
class MPCNContext:
    """In-memory representation of the MPC-N state."""

    instructions: List[Dict[str, Any]] = field(default_factory=list)
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    history: List[MPCNEvent] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instructions": self.instructions,
            "tasks": self.tasks,
            "history": [event.to_dict() for event in self.history],
            "metadata": self.metadata,
        }

    @staticmethod
    def from_dict(payload: Dict[str, Any]) -> "MPCNContext":
        history = [MPCNEvent.from_dict(item) for item in payload.get("history", [])]
        return MPCNContext(
            instructions=list(payload.get("instructions", [])),
            tasks=list(payload.get("tasks", [])),
            history=history,
            metadata=dict(payload.get("metadata", {})),
        )

    def task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        for task in self.tasks:
            if task.get("id") == task_id:
                return task
        return None

    def active_instructions(self) -> Iterable[Dict[str, Any]]:
        for instruction in self.instructions:
            if instruction.get("status") in {"active", "critical"}:
                yield instruction


def _ensure_state_file(path: Path) -> None:
    if path.exists():
        return
    path.write_text(
        json.dumps(
            {
                "instructions": [],
                "tasks": [],
                "history": [
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "actor": "system",
                        "action": "mpcn_initialized",
                        "details": {"spec": "v1"},
                    }
                ],
                "metadata": {"version": 1, "mode": "unknown", "last_checkpoint": None},
            },
            indent=2,
        )
    )


def load_context(path: Optional[Path] = None) -> MPCNContext:
    """Load MPC-N state from disk, creating a default file when missing."""
    state_path = path or DEFAULT_STATE_PATH
    _ensure_state_file(state_path)
    data = json.loads(state_path.read_text())
    return MPCNContext.from_dict(data)


def save_context(ctx: MPCNContext, path: Optional[Path] = None) -> None:
    """Persist MPC-N state to disk in a deterministic order."""
    state_path = path or DEFAULT_STATE_PATH
    state_path.write_text(json.dumps(ctx.to_dict(), indent=2, sort_keys=False))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_event(
    *,
    actor: str,
    action: str,
    details: Optional[Dict[str, Any]] = None,
    ctx: Optional[MPCNContext] = None,
    path: Optional[Path] = None,
) -> MPCNContext:
    """Append an event to the history and persist immediately."""
    context_obj = ctx or load_context(path)
    context_obj.history.append(
        MPCNEvent(timestamp=_now(), actor=actor, action=action, details=details or {})
    )
    save_context(context_obj, path)
    return context_obj


def set_task_status(
    task_id: str,
    status: str,
    *,
    ctx: Optional[MPCNContext] = None,
    path: Optional[Path] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> MPCNContext:
    """Update task status while keeping the state consistent."""
    context_obj = ctx or load_context(path)
    task = context_obj.task_by_id(task_id)
    if task is None:
        task = {"id": task_id, "title": task_id, "status": status}
        context_obj.tasks.append(task)
    task["status"] = status
    if extra:
        task.update(extra)
    task["updated_at"] = _now()
    save_context(context_obj, path)
    return context_obj


def register_instruction(
    *,
    instruction: Dict[str, Any],
    ctx: Optional[MPCNContext] = None,
    path: Optional[Path] = None,
) -> MPCNContext:
    """Ensure an instruction exists (idempotent insert/update)."""
    context_obj = ctx or load_context(path)
    inst_id = instruction.get("id")
    existing = None
    for item in context_obj.instructions:
        if item.get("id") == inst_id:
            existing = item
            break
    payload = {**(existing or {}), **instruction, "updated_at": _now()}
    if existing is None:
        context_obj.instructions.append(payload)
    else:
        existing.clear()
        existing.update(payload)
    save_context(context_obj, path)
    return context_obj


__all__ = [
    "MPCNContext",
    "MPCNEvent",
    "DEFAULT_STATE_PATH",
    "load_context",
    "save_context",
    "log_event",
    "set_task_status",
    "register_instruction",
]
