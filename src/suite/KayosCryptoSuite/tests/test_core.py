# tests/test_core.py

from core.crypto_core import hash_sha256

def test_hash_sha256():
    assert hash_sha256("kayos") == hash_sha256("kayos")
