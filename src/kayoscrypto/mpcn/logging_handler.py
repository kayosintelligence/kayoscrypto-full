"""Integracao com o modulo ``logging`` para registrar eventos na MPC-N."""
from __future__ import annotations

import logging
from pathlib import Path
from threading import Lock
from typing import Optional

from .context import MPCNContext, load_context, log_event


class MPCNLogHandler(logging.Handler):
    """Replica cada chamada do logger como evento MPC-N persistido."""

    def __init__(
        self,
        actor: str,
        *,
        state_path: Optional[Path] = None,
        action_prefix: str = "log",
        ctx: Optional[MPCNContext] = None,
    ) -> None:
        super().__init__()
        self.actor = actor
        self.state_path = state_path
        self.action_prefix = action_prefix
        self._ctx = ctx
        self._lock = Lock()

    def emit(self, record: logging.LogRecord) -> None:
        try:
            message = self.format(record)
            details = {
                "level": record.levelname,
                "logger": record.name,
                "message": message,
                "module": record.module,
                "path": record.pathname,
                "line": record.lineno,
            }
            if record.exc_info:
                details["exception"] = self.formatException(record.exc_info)
            extra_details = getattr(record, "mpcn_details", None)
            if isinstance(extra_details, dict):
                details.update(extra_details)
            action = getattr(record, "mpcn_action", f"{self.action_prefix}:{record.levelname.lower()}")
            with self._lock:
                context_obj = self._ctx or load_context(self.state_path)
                self._ctx = log_event(
                    actor=self.actor,
                    action=action,
                    details=details,
                    ctx=context_obj,
                    path=self.state_path,
                )
        except Exception:  # pragma: no cover - fallback para logging padrão
            self.handleError(record)


def attach_mpcn_logging(
    *,
    actor: str,
    logger: Optional[logging.Logger] = None,
    level: int = logging.INFO,
    state_path: Optional[Path] = None,
    action_prefix: str = "log",
) -> MPCNLogHandler:
    """Acopla o handler MPC-N ao logger informado e retorna a instancia."""

    target_logger = logger or logging.getLogger()
    handler = MPCNLogHandler(actor, state_path=state_path, action_prefix=action_prefix)
    handler.setLevel(level)
    target_logger.addHandler(handler)
    return handler


def detach_mpcn_logging(handler: MPCNLogHandler, *, logger: Optional[logging.Logger] = None) -> None:
    """Remove o handler do logger alvo e fecha seus recursos."""

    target_logger = logger or logging.getLogger()
    target_logger.removeHandler(handler)
    handler.close()


__all__ = ["MPCNLogHandler", "attach_mpcn_logging", "detach_mpcn_logging"]
