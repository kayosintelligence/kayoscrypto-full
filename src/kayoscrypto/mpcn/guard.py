"""Mecanismos de guarda e alertas para a MPC-N.

Este módulo identifica sinais de esquecimento (contexto obsoleto, instruções
faltando, ausência de heartbeat) e registra alertas antes que os agentes
continuem trabalhando. Deve ser invocado no início de todo pipeline crítico.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from .context import MPCNContext, load_context, log_event


def _parse_timestamp(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class GuardianReport:
    """Resumo estruturado da verificação realizada pelo guardião."""

    status: str
    alerts: List[Dict[str, Any]]
    last_event_timestamp: Optional[str]
    stale_minutes: Optional[float]
    missing_instructions: List[str]
    ctx: MPCNContext

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "alerts": self.alerts,
            "last_event_timestamp": self.last_event_timestamp,
            "stale_minutes": self.stale_minutes,
            "missing_instructions": self.missing_instructions,
        }


class MPCNGuardAlert(RuntimeError):
    """Erro lançado quando o guardião detecta condição bloqueante."""

    def __init__(self, message: str, report: GuardianReport):
        super().__init__(message)
        self.report = report


def evaluate_guardian(
    *,
    actor: str,
    intent: str,
    required_instruction_ids: Optional[Sequence[str]] = None,
    max_inactive_minutes: int = 30,
    state_path: Optional[Path] = None,
    log_events: bool = True,
) -> GuardianReport:
    """Executa as verificações básicas do guardião.

    Retorna um GuardianReport com status:
      - "ok": nenhum alerta
      - "alerta": apenas avisos (ex.: inatividade moderada)
      - "erro": problemas críticos (instruções ausentes, histórico vazio)
    """

    ctx = load_context(state_path)
    now = _now()
    alerts: List[Dict[str, Any]] = []

    # Determinar último evento registrado
    last_dt: Optional[datetime] = None
    last_ts: Optional[str] = None
    for event in ctx.history:
        parsed = _parse_timestamp(getattr(event, "timestamp", None))
        if parsed and (last_dt is None or parsed > last_dt):
            last_dt = parsed
            last_ts = event.timestamp

    stale_minutes: Optional[float] = None
    if last_dt is None:
        alerts.append(
            {
                "tipo": "historico_vazio",
                "mensagem": "Nenhum evento registrado na MPC-N.",
                "gravidade": "erro",
            }
        )
    else:
        stale_minutes = (now - last_dt).total_seconds() / 60.0
        if stale_minutes > max_inactive_minutes:
            alerts.append(
                {
                    "tipo": "contexto_obsoleto",
                    "mensagem": f"Contexto parado há {stale_minutes:.1f} minutos.",
                    "gravidade": "alerta",
                    "limite_minutos": max_inactive_minutes,
                }
            )

    # Validar instruções obrigatórias
    missing: List[str] = []
    required = list(required_instruction_ids or [])
    if required:
        current_ids = {item.get("id") for item in ctx.instructions}
        for inst_id in required:
            if inst_id not in current_ids:
                missing.append(inst_id)
                alerts.append(
                    {
                        "tipo": "instrucao_ausente",
                        "mensagem": f"Instrução obrigatória {inst_id} não encontrada.",
                        "gravidade": "erro",
                        "instrucao": inst_id,
                    }
                )

    if any(alert.get("gravidade") == "erro" for alert in alerts):
        status = "erro"
    elif alerts:
        status = "alerta"
    else:
        status = "ok"

    timestamp_iso = now.isoformat()
    ctx.metadata["last_guard_check"] = timestamp_iso

    report = GuardianReport(
        status=status,
        alerts=alerts,
        last_event_timestamp=last_ts,
        stale_minutes=stale_minutes,
        missing_instructions=missing,
        ctx=ctx,
    )

    if log_events:
        details = {
            "intent": intent,
            "status": status,
            "max_inactive_minutes": max_inactive_minutes,
            "alert_count": len(alerts),
            "alerts": alerts,
        }
        log_event(actor=actor, action="mpcn_guard:check", details=details, ctx=ctx, path=state_path)

    return report


def enforce_guardian(
    *,
    actor: str,
    intent: str,
    required_instruction_ids: Optional[Sequence[str]] = None,
    max_inactive_minutes: int = 30,
    state_path: Optional[Path] = None,
    fail_on_warnings: bool = False,
) -> GuardianReport:
    """Executa o guardião e lança erro quando houver alertas bloqueantes."""

    report = evaluate_guardian(
        actor=actor,
        intent=intent,
        required_instruction_ids=required_instruction_ids,
        max_inactive_minutes=max_inactive_minutes,
        state_path=state_path,
        log_events=True,
    )

    should_fail = report.status == "erro" or (fail_on_warnings and report.status == "alerta")
    if should_fail:
        raise MPCNGuardAlert("MPC-N sinalizou condição impeditiva", report)
    return report


__all__ = ["GuardianReport", "MPCNGuardAlert", "evaluate_guardian", "enforce_guardian"]
