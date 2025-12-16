#!/usr/bin/env python3
"""Script simples para executar encrypt/decrypt para profiling."""

import os
import sys
import json

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.core.kayoscrypto_ultimate import KayosCryptoUltimate

PASSWORD = os.getenv("KAYOS_PASSWORD", "")
DATA_SIZE_MB = int(os.environ.get("KAYOS_PROFILE_MB", "10"))
PERM_STRATEGY = os.environ.get("KAYOS_PERM_STRATEGY", "random")
PERM_BLOCK = int(os.environ.get("KAYOS_PERM_BLOCK", "4096"))
CORE_PROFILING = os.environ.get("KAYOS_PROFILE_CORE", "0") == "1"
PERM_CACHE_ENABLED = os.environ.get("KAYOS_PERM_CACHE_ENABLED", "1") not in {"0", "false", "False"}
PERM_CACHE_SIZE = int(os.environ.get("KAYOS_PERM_CACHE_SIZE", "16"))
PERM_CACHE_BYTES = int(os.environ.get("KAYOS_PERM_CACHE_BYTES", str(134_217_728)))
PERM_CACHE_SAMPLES = int(os.environ.get("KAYOS_PERM_CACHE_SAMPLES", "0"))


def run():
    data = os.urandom(DATA_SIZE_MB * 1024 * 1024)
    cipher = KayosCryptoUltimate(
        use_concentric=True,
        use_direction=True,
        use_quantum=True,
        use_ed25519=True,
        core_permutation_strategy=PERM_STRATEGY,
        core_permutation_block_size=PERM_BLOCK,
        core_profiling=CORE_PROFILING,
        core_permutation_cache_enabled=PERM_CACHE_ENABLED,
        core_permutation_cache_size=PERM_CACHE_SIZE,
        core_permutation_cache_bytes=PERM_CACHE_BYTES,
    )
    result = cipher.encrypt(data, PASSWORD)
    if isinstance(result, dict) and "quantum_salt" in result:
        package = {"ciphertext": result["ciphertext"], "quantum_salt": result["quantum_salt"]}
    else:
        package = result
    recovered = cipher.decrypt(package, PASSWORD)
    assert recovered == data

    stats = cipher.get_permutation_cache_stats()
    if PERM_CACHE_SAMPLES > 0:
        snapshots = [stats]
        for _ in range(PERM_CACHE_SAMPLES):
            next_pkg = cipher.encrypt(data, PASSWORD)
            if isinstance(next_pkg, dict) and "quantum_salt" in next_pkg:
                pkg = {"ciphertext": next_pkg["ciphertext"], "quantum_salt": next_pkg["quantum_salt"]}
            else:
                pkg = next_pkg
            cipher.decrypt(pkg, PASSWORD)
            snapshots.append(cipher.get_permutation_cache_stats())
        print("[CACHE_SAMPLES] " + json.dumps(snapshots, sort_keys=True))
    else:
        print("[CACHE] " + json.dumps(stats, sort_keys=True))


if __name__ == "__main__":
    run()
