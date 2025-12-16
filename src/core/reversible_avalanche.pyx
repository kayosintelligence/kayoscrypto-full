# cython: language_level=3, boundscheck=False, wraparound=False, cdivision=True
"""
Implementação Cython do ReversibleAvalancheEngine para desempenho enterprise.
"""

from libc.stdint cimport uint8_t
from cython cimport boundscheck, wraparound, cdivision


def _normalize_rounds(int rounds):
    return 3 if rounds <= 0 else rounds


cpdef bytes reversible_mix(bytes data, bytes key, int rounds=3, bint reverse=False):
    """Mistura reversível de avalanche em Cython."""
    cdef Py_ssize_t length = len(data)
    if length < 2:
        return data

    cdef Py_ssize_t key_len = len(key)
    if key_len == 0:
        return data

    rounds = _normalize_rounds(rounds)

    cdef bytearray result = bytearray(data)
    cdef uint8_t[:] buf = result
    cdef const uint8_t[:] key_view = key

    cdef Py_ssize_t round_num
    cdef Py_ssize_t pos
    cdef Py_ssize_t key_idx
    cdef uint8_t prev_val
    cdef uint8_t mix

    if not reverse:
        for round_num in range(rounds):
            key_idx = (round_num * 11 + 1) % key_len
            prev_val = buf[0]
            for pos in range(1, length):
                mix = (<uint8_t>((prev_val + key_view[key_idx]) & 0xFF))
                prev_val = buf[pos] ^ mix
                buf[pos] = prev_val
                key_idx += 1
                if key_idx == key_len:
                    key_idx = 0

            if length > 1:
                key_idx = (round_num * 17 + length - 2) % key_len
                for pos in range(length - 2, -1, -1):
                    mix = (<uint8_t>((buf[pos + 1] + key_view[key_idx]) & 0xFF))
                    buf[pos] = buf[pos] ^ mix
                    if key_idx == 0:
                        key_idx = key_len - 1
                    else:
                        key_idx -= 1
    else:
        for round_num in range(rounds - 1, -1, -1):
            if length > 1:
                key_idx = (round_num * 17) % key_len
                for pos in range(length - 1):
                    mix = (<uint8_t>((buf[pos + 1] + key_view[key_idx]) & 0xFF))
                    buf[pos] = buf[pos] ^ mix
                    key_idx += 1
                    if key_idx == key_len:
                        key_idx = 0

                key_idx = (round_num * 11 + length - 1) % key_len
                for pos in range(length - 1, 0, -1):
                    mix = (<uint8_t>((buf[pos - 1] + key_view[key_idx]) & 0xFF))
                    buf[pos] = buf[pos] ^ mix
                    if key_idx == 0:
                        key_idx = key_len - 1
                    else:
                        key_idx -= 1

    return bytes(result)
