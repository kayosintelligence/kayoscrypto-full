"""Convenience hooks for plugging MPC-N into scripts and agents."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from .context import (
    MPCNContext,
    load_context,
    log_event,
    save_context,
    set_task_status,
)


def bootstrap_session(
    *,
    actor: str,
    intent: str,
    details: Optional[Dict[str, Any]] = None,
    state_path: Optional[Path] = None,
) -> MPCNContext:
    """Load context, log a session_start event, and return the context."""
    ctx = load_context(state_path)
    log_event(actor=actor, action=f"session_start:{intent}", details=details or {}, ctx=ctx)
    return ctx


def complete_session(
    *,
    actor: str,
    intent: str,
    outcome: str,
    details: Optional[Dict[str, Any]] = None,
    ctx: Optional[MPCNContext] = None,
    state_path: Optional[Path] = None,
) -> MPCNContext:
    """Log the end of a session and persist the latest state."""
    context_obj = ctx or load_context(state_path)
    log_event(
        actor=actor,
        action=f"session_end:{intent}",
        details={"outcome": outcome, **(details or {})},
        ctx=context_obj,
        path=state_path,
    )
    save_context(context_obj, state_path)
    return context_obj


def heartbeat(
    *,
    actor: str,
    action: str,
    details: Optional[Dict[str, Any]] = None,
    ctx: Optional[MPCNContext] = None,
    state_path: Optional[Path] = None,
) -> MPCNContext:
    """Lightweight helper to log intermediate progress."""
    return log_event(actor=actor, action=action, details=details, ctx=ctx, path=state_path)


def track_task(
    *,
    task_id: str,
    status: str,
    actor: str,
    details: Optional[Dict[str, Any]] = None,
    state_path: Optional[Path] = None,
) -> MPCNContext:
    """Update a task record while emitting a heartbeat event."""
    ctx = set_task_status(task_id, status, path=state_path, extra=details)
    log_event(
        actor=actor,
        action=f"task_update:{task_id}",
        details={"status": status, **(details or {})},
        ctx=ctx,
        path=state_path,
    )
    return ctx


__all__ = ["bootstrap_session", "complete_session", "heartbeat", "track_task"]
