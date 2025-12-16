"""Geometry-driven utilities based on the Magen David (Star of David).

This module provides reusable building blocks to experiment with a hexagram
layer inside KayosCrypto:

* ``MagenDavidSymmetry`` exposes the twelve reversible operations of the
  dihedral group D6 (six rotations and six reflections).
* ``MagenDavidKeySchedule`` splits a master key across the six vertices and
  derives deterministic round keys following the symmetry operations.
* ``MagenSBox`` produces a bijective 256-entry substitution table organised in
  six hexagonal sectors plus the central hexagon.
* ``HexagramNetwork`` is a lightweight, reversible network that applies the
  symmetry driven diffusion over six data branches.

All helpers are pure Python and intentionally side-effect free to simplify
future integration and unit testing.
"""

from __future__ import annotations

import hashlib
import math
from typing import Iterable, List, Sequence


class MagenDavidSymmetry:
    """Implements the twelve operations of the dihedral group D6."""

    _REFLECTION_MAPS: List[List[int]] = [
        [0, 5, 4, 3, 2, 1],  # vertical axis
        [1, 0, 5, 4, 3, 2],  # 30° axis
        [2, 1, 0, 5, 4, 3],  # 60° axis
        [3, 2, 1, 0, 5, 4],  # horizontal axis
        [4, 3, 2, 1, 0, 5],  # 120° axis
        [5, 4, 3, 2, 1, 0],  # 150° axis
    ]

    _CAYLEY_TABLE: List[List[int]] = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        [1, 2, 3, 4, 5, 0, 7, 8, 9, 10, 11, 6],
        [2, 3, 4, 5, 0, 1, 8, 9, 10, 11, 6, 7],
        [3, 4, 5, 0, 1, 2, 9, 10, 11, 6, 7, 8],
        [4, 5, 0, 1, 2, 3, 10, 11, 6, 7, 8, 9],
        [5, 0, 1, 2, 3, 4, 11, 6, 7, 8, 9, 10],
        [6, 11, 10, 9, 8, 7, 0, 5, 4, 3, 2, 1],
        [7, 6, 11, 10, 9, 8, 1, 0, 5, 4, 3, 2],
        [8, 7, 6, 11, 10, 9, 2, 1, 0, 5, 4, 3],
        [9, 8, 7, 6, 11, 10, 3, 2, 1, 0, 5, 4],
        [10, 9, 8, 7, 6, 11, 4, 3, 2, 1, 0, 5],
        [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
    ]

    def rotate(self, data: Sequence, steps: int) -> List:
        """Rotate a 6-element sequence by multiples of 60 degrees."""

        if len(data) != 6:
            raise ValueError("rotation expects six elements")
        steps %= 6
        if steps == 0:
            return list(data)
        return list(data[-steps:] + data[:-steps])

    def reflect(self, data: Sequence, axis: int) -> List:
        """Reflect across one of the six symmetry axes."""

        if len(data) != 6:
            raise ValueError("reflection expects six elements")
        mapping = self._REFLECTION_MAPS[axis % 6]
        return [data[i] for i in mapping]

    def apply_operation(self, data: Sequence, op_id: int) -> List:
        """Apply rotation (0-5) or reflection (6-11)."""

        if op_id < 0 or op_id > 11:
            raise ValueError("operation id must be between 0 and 11")
        if op_id < 6:
            return self.rotate(data, op_id)
        return self.reflect(data, op_id - 6)

    def compose(self, op_a: int, op_b: int) -> int:
        """Return the operation id equivalent to op_a ∘ op_b."""

        return self._CAYLEY_TABLE[op_a][op_b]


def _split_six(data: bytes) -> List[bytes]:
    """Split a byte string into six contiguous segments."""

    length = len(data)
    base = length // 6
    remainder = length % 6
    segments = []
    offset = 0
    for idx in range(6):
        extra = 1 if idx < remainder else 0
        end = offset + base + extra
        segments.append(data[offset:end])
        offset = end
    return segments


def _xor_bytes(a: Iterable[int], b: Iterable[int]) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def _expand_bytes(seed: bytes, length: int) -> bytes:
    """Expand a seed deterministically to the desired length."""

    digest = seed
    output = bytearray()
    counter = 0
    while len(output) < length:
        counter_bytes = counter.to_bytes(2, "big")
        digest = hashlib.sha256(digest + counter_bytes).digest()
        output.extend(digest)
        counter += 1
    return bytes(output[:length])


class MagenDavidKeySchedule:
    """Derive round keys by walking the dihedral symmetry operations."""

    def __init__(self, master_key: bytes):
        if len(master_key) < 6:
            raise ValueError("master key must be at least six bytes")
        self.master_key = master_key
        self._symmetry = MagenDavidSymmetry()
        self._segments = _split_six(master_key)

    def generate_round_keys(self, num_rounds: int = 12) -> List[bytes]:
        rounds = max(1, num_rounds)
        round_keys: List[bytes] = []
        segments = list(self._segments)
        for round_idx in range(rounds):
            op_id = round_idx % 12
            transformed = self._symmetry.apply_operation(segments, op_id)
            combined = b"".join(transformed)
            round_key = hashlib.sha256(combined + round_idx.to_bytes(2, "big")).digest()
            round_keys.append(round_key)
            segments = _split_six(round_key)
        return round_keys


class MagenSBox:
    """Hexagon-inspired substitution box (bijective on 0..255)."""

    _CENTER_POSITIONS = [0, 42, 85, 128, 171, 213]

    def __init__(self, seed: bytes):
        if not seed:
            raise ValueError("seed must not be empty")
        self.seed = seed
        self.sbox = self._generate_hexagonal_sbox()

    def _generate_hexagonal_sbox(self) -> List[int]:
        sbox: List[int] = [0] * 256
        used = set()
        assigned = [False] * 256
        for idx, position in enumerate(self._CENTER_POSITIONS):
            value = self._hash_to_byte(b"CENTER" + idx.to_bytes(1, "big"))
            while value in used:
                value = (value + 1) % 256
            sbox[position] = value
            used.add(value)
            assigned[position] = True
        for sector in range(6):
            start = sector * 42
            end = min(start + 42, 256)
            for pos in range(start, end):
                if pos in self._CENTER_POSITIONS:
                    continue
                value = self._hash_to_byte(b"SECTOR" + sector.to_bytes(1, "big") + pos.to_bytes(2, "big"))
                while value in used:
                    value = (value + 1) % 256
                sbox[pos] = value
                used.add(value)
                assigned[pos] = True
        next_value = 0
        for pos in range(256):
            if assigned[pos]:
                continue
            while next_value in used:
                next_value = (next_value + 1) % 256
            sbox[pos] = next_value
            used.add(next_value)
            assigned[pos] = True
        return sbox

    def _hash_to_byte(self, suffix: bytes) -> int:
        digest = hashlib.sha256(self.seed + suffix).digest()
        return digest[0]

    def substitute(self, value: int) -> int:
        return self.sbox[value]

    def inverse(self) -> List[int]:
        inv = [0] * 256
        for idx, val in enumerate(self.sbox):
            inv[val] = idx
        return inv


class HexagramNetwork:
    """Six-branch reversible network driven by round keys."""

    def __init__(self, round_keys: Sequence[bytes]):
        if not round_keys:
            raise ValueError("round_keys must not be empty")
        self.round_keys = list(round_keys)

    def encrypt_block(self, block: bytes) -> bytes:
        vertices = [bytearray(seg) for seg in _split_six(block)]
        for round_idx, round_key in enumerate(self.round_keys):
            vertices = self._hexagram_round(vertices, round_key, round_idx)
        return b"".join(bytes(v) for v in vertices)

    def decrypt_block(self, block: bytes) -> bytes:
        vertices = [bytearray(seg) for seg in _split_six(block)]
        for round_idx, round_key in reversed(list(enumerate(self.round_keys))):
            vertices = self._hexagram_inverse_round(vertices, round_key, round_idx)
        return b"".join(bytes(v) for v in vertices)

    def _hexagram_round(self, vertices: List[bytearray], round_key: bytes, round_idx: int) -> List[bytearray]:
        top = vertices[:3]
        bottom = vertices[3:]
        mixed_bottom = []
        for branch, target in zip(top, bottom):
            mask = _expand_bytes(round_key + round_idx.to_bytes(2, "big") + bytes(branch), len(target))
            mixed_bottom.append(bytearray(_xor_bytes(target, mask)))
        new_vertices = top + mixed_bottom
        new_vertices = new_vertices[1:] + new_vertices[:1]
        return new_vertices

    def _hexagram_inverse_round(self, vertices: List[bytearray], round_key: bytes, round_idx: int) -> List[bytearray]:
        new_vertices = vertices[-1:] + vertices[:-1]
        top = new_vertices[:3]
        bottom = new_vertices[3:]
        restored_bottom: List[bytearray] = []
        for branch, target in zip(top, bottom):
            mask = _expand_bytes(round_key + round_idx.to_bytes(2, "big") + bytes(branch), len(target))
            restored_bottom.append(bytearray(_xor_bytes(target, mask)))
        return top + restored_bottom


def hexagram_vertices(radius: float = 1.0) -> List[tuple[float, float]]:
    """Return the six outer vertices of the hexagram on the unit circle."""

    points = []
    for idx in range(6):
        angle = math.radians(idx * 60.0)
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        points.append((x, y))
    return points


def central_hexagon_vertices(radius: float = 1.0) -> List[tuple[float, float]]:
    """Return the six vertices forming the inner hexagon."""

    inner_radius = radius / math.sqrt(3.0)
    points = []
    for idx in range(6):
        angle = math.radians(idx * 60.0 + 30.0)
        x = inner_radius * math.cos(angle)
        y = inner_radius * math.sin(angle)
        points.append((x, y))
    return points
