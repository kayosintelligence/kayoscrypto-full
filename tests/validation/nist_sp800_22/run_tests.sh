#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
DATA_FILE="${ROOT_DIR}/data/dieharder_2gb.bin"
STS_DIR="${ROOT_DIR}/tools/sts-2.1.2/sts-2.1.2"

if [[ ! -f "${DATA_FILE}" ]]; then
  echo "[kayocrypto] data file not found: ${DATA_FILE}" >&2
  exit 1
fi

pushd "${STS_DIR}" >/dev/null
./assess 1000000 <<<'1'
popd >/dev/null
