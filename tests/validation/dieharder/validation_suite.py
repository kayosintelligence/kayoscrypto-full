#!/usr/bin/env python3
"""Helper to run focused Dieharder suites against prepared datasets."""
from __future__ import annotations

import argparse
import logging
import subprocess
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from kayoscrypto.mpcn import attach_mpcn_logging, detach_mpcn_logging
RESULTS = ROOT / "results"
DATA_DEFAULT = ROOT / "data" / "dieharder_2gb.bin"
LOGGER = logging.getLogger("kayos.dieharder")

TEST_MAP = {
    "lagged": "203",
    "byte": "205",
    "monobit2": "209",
}


def run_dieharder(test: str, data: Path, out: Path) -> None:
    details = {
        "test": test,
        "dieharder_id": TEST_MAP[test],
        "data": str(data),
        "output": str(out),
    }
    LOGGER.info(
        " Executando Dieharder %s",
        test,
        extra={"mpcn_details": details, "mpcn_action": "diagnostics.dieharder"},
    )
    code = subprocess.call([
        "dieharder",
        "-d",
        TEST_MAP[test],
        "-g",
        "201",
        "-f",
        str(data),
    ], stdout=out.open("w"))
    if code != 0:
        LOGGER.error(
            " Dieharder %s falhou",
            test,
            extra={
                "mpcn_details": {**details, "exit_code": code},
                "mpcn_action": "diagnostics.dieharder",
            },
        )
        raise SystemExit(f"dieharder test {test} failed with exit code {code}")
    LOGGER.info(
        " Dieharder %s finalizado",
        test,
        extra={
            "mpcn_details": {**details, "exit_code": code},
            "mpcn_action": "diagnostics.dieharder",
        },
    )


def _configure_logging() -> None:
    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO, format="%(message)s")


def main() -> None:
    _configure_logging()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "test", choices=sorted(TEST_MAP.keys()), help="Dieharder test alias"
    )
    parser.add_argument("--data", type=Path, default=DATA_DEFAULT, help="Binary dataset")
    parser.add_argument("--results", type=Path, default=RESULTS, help="Output directory")
    args = parser.parse_args()

    handler = attach_mpcn_logging(
        actor="dieharder_wrapper",
        logger=LOGGER,
        action_prefix="diagnostics.dieharder",
    )
    try:
        args.results.mkdir(parents=True, exist_ok=True)
        outfile = args.results / f"dieharder_{args.test}.log"
        run_dieharder(args.test, args.data, outfile)
        LOGGER.info(
            "Saved log to %s",
            outfile,
            extra={
                "mpcn_details": {"output": str(outfile), "test": args.test},
                "mpcn_action": "diagnostics.dieharder",
            },
        )
    finally:
        detach_mpcn_logging(handler, logger=LOGGER)


if __name__ == "__main__":
    main()
