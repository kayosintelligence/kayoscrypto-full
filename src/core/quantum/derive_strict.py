"""Strict session material derivation with atomic MPC-N anchoring.

Fail-hard semantics: if MPC-N anchoring or entropy generation fails, this
module raises an exception so calling code cannot silently continue.

Usage:
    from core.quantum.derive_strict import derive_session_material_strict

    material = derive_session_material_strict(session_id="run-123", context_info={})
    key = material["key"]     # 32 bytes
    nonce = material["nonce"] # 16 bytes
"""
from __future__ import annotations

import hmac
import hashlib
import os
import time
from typing import Dict, Optional


def _hkdf_extract(salt: bytes, ikm: bytes) -> bytes:
    return hmac.new(salt, ikm, hashlib.sha512).digest()


def _hkdf_expand(prk: bytes, info: bytes, length: int) -> bytes:
    okm = b""
    t = b""
    counter = 1
    while len(okm) < length:
        t = hmac.new(prk, t + info + bytes([counter]), hashlib.sha512).digest()
        okm += t
        counter += 1
    return okm[:length]


def derive_session_material_strict(
    session_id: str,
    context_info: Optional[dict] = None,
    ikm_len: int = 64,
    salt_len: int = 64,
    out_len: int = 48,
) -> Dict[str, bytes]:
    """Derive session material from real entropy and anchor to MPC-N.

    - Generates a high-quality random "ikm" (internal key material) via
      `os.urandom(ikm_len)` (no fallback allowed).
    - Generates a random salt (salt_len bytes), publishes the salt (hex)
      to the MPC-N via `kayoscrypto.mpcn.context.log_event(...)`.
    - Uses HKDF-SHA512 to derive `out_len` bytes then splits into
      a 32-byte key and 16-byte nonce (48 bytes total by default).

    Raises RuntimeError on any failure to generate entropy or to anchor the
    event in the MPC-N guard (fail-hard semantics required by policy).
    """
    # generate real entropy IKM
    ikm = os.urandom(ikm_len)
    if len(ikm) < ikm_len:
        raise RuntimeError("Insufficient entropy from os.urandom()")

    salt = os.urandom(salt_len)
    if len(salt) < salt_len:
        raise RuntimeError("Insufficient entropy for salt")

    # derive
    prk = _hkdf_extract(salt, ikm)
    info = (session_id or "") .encode("utf-8") + b"|" + (repr(context_info or {}).encode("utf-8"))
    okm = _hkdf_expand(prk, info, out_len)
    if len(okm) < out_len:
        raise RuntimeError("HKDF failed to produce enough output")

    key = okm[:32]
    nonce = okm[32:48]

    # Anchor to MPC-N (must be present and succeed under strict policy)
    try:
        from kayoscrypto.mpcn.context import log_event  # type: ignore
    except Exception as e:  # pragma: no cover - environment-specific
        raise RuntimeError("MPC-N context unavailable (strict mode requires MPC-N)") from e

    details = {
        "session_id": session_id,
        "salt_hex": salt.hex(),
        "timestamp": time.time(),
    }
    if context_info:
        details["context"] = context_info

    try:
        # Expect implementation to raise on failure; treat falsy as failure
        res = log_event(actor="derive_strict", action="anchor", details=details)
    except Exception as e:  # pragma: no cover - dependent on MPC-N
        raise RuntimeError("Failed to publish anchor to MPC-N") from e

    if not res:
        raise RuntimeError("MPC-N anchoring returned falsy result")

    return {"key": key, "nonce": nonce, "salt": salt}
