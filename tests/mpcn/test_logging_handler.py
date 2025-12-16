import json
import logging
import uuid
from pathlib import Path

from kayoscrypto.mpcn.logging_handler import MPCNLogHandler, attach_mpcn_logging, detach_mpcn_logging


def _make_logger() -> logging.Logger:
    logger = logging.getLogger(f"mpcn-test-{uuid.uuid4()}")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


def test_handler_persists_log_event(tmp_path: Path) -> None:
    state_path = tmp_path / "mpcn_state.json"
    logger = _make_logger()
    handler = MPCNLogHandler(actor="test_logger", state_path=state_path)
    logger.addHandler(handler)
    try:
        logger.info("Processando bloco %s", 42, extra={"mpcn_details": {"block": 42}})
    finally:
        logger.removeHandler(handler)
    data = json.loads(state_path.read_text())
    event = data["history"][-1]
    assert event["actor"] == "test_logger"
    assert event["action"] == "log:info"
    assert event["details"]["block"] == 42
    assert "Processando bloco" in event["details"]["message"]


def test_attach_detach_helpers(tmp_path: Path) -> None:
    state_path = tmp_path / "state.json"
    logger = _make_logger()
    handler = attach_mpcn_logging(actor="helper_logger", logger=logger, state_path=state_path)
    try:
           logger.warning("Falha prevista", extra={"mpcn_action": "pipeline:warn"})
    finally:
        detach_mpcn_logging(handler, logger=logger)
    data = json.loads(state_path.read_text())
    event = data["history"][-1]
    assert event["action"] == "pipeline:warn"
    assert event["details"]["level"] == "WARNING"
