"""Converte uma matriz SATOR 5x5 em bits e extrai uma chave via HKDF-SHA256.

Fornece funções simples para: converter letras A-Z em 5 bits, concatenar e produzir
um digest derivado via HKDF (RFC5869) com SHA256.
"""
from hashlib import sha256
import hmac

SATOR = [
    list("SATOR"),
    list("AREPO"),
    list("TENET"),
    list("OPERA"),
    list("ROTAS"),
]

def letters_to_bits(matrix):
    """Converte 5x5 matrix de letras (A-Z) em bytes.

    Cada letra map para 5 bits: A->0, B->1, ... Z->25. Ordenação row-major.
    Retorna bytes (packed MSB-first across the stream).
    """
    bits = []
    for r in range(5):
        for c in range(5):
            ch = matrix[r][c]
            val = ord(ch) - ord('A')
            if val < 0 or val > 31:
                raise ValueError("Caracter fora do mapa A-Z: %r" % ch)
            # append 5 bits
            for b in range(4, -1, -1):
                bits.append((val >> b) & 1)

    # pack bits into bytes
    out = bytearray()
    acc = 0
    llen = 0
    for bit in bits:
        acc = (acc << 1) | bit
        llen += 1
        if llen == 8:
            out.append(acc)
            acc = 0
            llen = 0
    if llen > 0:
        acc = acc << (8 - llen)
        out.append(acc)
    return bytes(out)


def hkdf_extract(salt, ikm):
    if salt is None:
        salt = b"\x00" * 32
    return hmac.new(salt, ikm, sha256).digest()


def hkdf_expand(prk, info, length=32):
    # simple HKDF expand
    okm = b""
    t = b""
    i = 1
    while len(okm) < length:
        t = hmac.new(prk, t + (info or b"") + bytes([i]), sha256).digest()
        okm += t
        i += 1
    return okm[:length]


def sator_to_key(matrix, salt=None, info=b"sator-key", length=32):
    raw = letters_to_bits(matrix)
    prk = hkdf_extract(salt, raw)
    return hkdf_expand(prk, info, length)


def canonical_sator_bytes():
    return letters_to_bits(SATOR)


if __name__ == '__main__':
    print('SATOR -> bits demo')
    b = canonical_sator_bytes()
    print('Raw bytes (hex):', b.hex())
    key = sator_to_key(SATOR)
    print('Derived key (SHA256-HKDF) hex:', key.hex())
