"""ChaCha20-based whitening utilities for entropy streams."""
from __future__ import annotations

import os
from typing import BinaryIO, Generator, Optional, Tuple

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms


class ChaCha20Whitener:
    """Apply ChaCha20 as a cryptographic whitening layer."""

    def __init__(self, key: Optional[bytes] = None, nonce: Optional[bytes] = None) -> None:
        backend = default_backend()
        self.key = key or os.urandom(32)
        self.nonce = nonce or os.urandom(16)

        if len(self.key) != 32:
            raise ValueError("ChaCha20 key must be 32 bytes")
        if len(self.nonce) != 16:
            raise ValueError("ChaCha20 nonce must be 16 bytes")

        cipher = Cipher(algorithms.ChaCha20(self.key, self.nonce), mode=None, backend=backend)
        self._encryptor = cipher.encryptor()

    def whiten_chunk(self, chunk: bytes) -> bytes:
        """Whiten a single chunk of bytes."""
        if not chunk:
            return b""
        return self._encryptor.update(chunk)

    def whiten_stream(self, source: BinaryIO, chunk_size: int = 4096) -> Generator[bytes, None, None]:
        """Yield whitened chunks from a file-like object."""
        while True:
            chunk = source.read(chunk_size)
            if not chunk:
                break
            yield self.whiten_chunk(chunk)


def create_whitened_file(
    input_path: str,
    output_path: str,
    key: Optional[bytes] = None,
    nonce: Optional[bytes] = None,
) -> Tuple[bytes, bytes]:
    """Whiten an entire file, returning the key/nonce used."""
    whitener = ChaCha20Whitener(key=key, nonce=nonce)
    with open(input_path, "rb") as src, open(output_path, "wb") as dst:
        for chunk in whitener.whiten_stream(src):
            dst.write(chunk)
    return whitener.key, whitener.nonce
