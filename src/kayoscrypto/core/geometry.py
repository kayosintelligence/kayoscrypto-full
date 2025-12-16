"""KAYOS HYPER-SATOR 6D GEOMETRY DEFINITION

Constante de genesis usada para ancoragem no HKDF / registro.
"""
SATOR_GENESIS_HASH = bytes.fromhex(
    "58f21e174a20717ea7f7d3f8ad0c90cea032c85c5e9c5bcb3203610807777ce4"
)

SATOR_CONTEXT_INFO = b"Kayos/SATOR-6D/v1/Genesis"

def get_geometric_salt() -> bytes:
    """Retorna a semente geométrica (SHA256) para uso como salt/info."""
    return SATOR_GENESIS_HASH
