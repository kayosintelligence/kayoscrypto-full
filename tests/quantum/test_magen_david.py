#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for the Magen David utilities."""

from __future__ import annotations

import os
import sys
from pathlib import Path
import importlib.util
import types

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = PROJECT_ROOT / "src" / "core" / "quantum" / "magen_david.py"


def _load_magen_david_module():
    """Load the magen_david module without triggering heavy package imports."""

    # Set up lightweight package placeholders to satisfy the module's dotted path.
    core_pkg = types.ModuleType("core")
    core_pkg.__path__ = [str(PROJECT_ROOT / "src" / "core")]  # type: ignore[attr-defined]
    sys.modules.setdefault("core", core_pkg)

    quantum_pkg = types.ModuleType("core.quantum")
    quantum_pkg.__path__ = [str(PROJECT_ROOT / "src" / "core" / "quantum")]  # type: ignore[attr-defined]
    sys.modules.setdefault("core.quantum", quantum_pkg)

    spec = importlib.util.spec_from_file_location("core.quantum.magen_david", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise ImportError("Unable to load magen_david module specification")
    module = importlib.util.module_from_spec(spec)
    sys.modules["core.quantum.magen_david"] = module
    spec.loader.exec_module(module)
    return module


magen_david = _load_magen_david_module()

HexagramNetwork = magen_david.HexagramNetwork
MagenDavidKeySchedule = magen_david.MagenDavidKeySchedule
MagenDavidSymmetry = magen_david.MagenDavidSymmetry
MagenSBox = magen_david.MagenSBox
central_hexagon_vertices = magen_david.central_hexagon_vertices
hexagram_vertices = magen_david.hexagram_vertices


def test_symmetry_operations_preserve_elements():
    symmetry = MagenDavidSymmetry()
    data = list(range(6))
    seen = set()
    for op_id in range(12):
        transformed = tuple(symmetry.apply_operation(data, op_id))
        assert len(transformed) == 6
        assert set(transformed) == set(data)
        seen.add(transformed)
    assert len(seen) == 12


def test_symmetry_composition_matches_table():
    symmetry = MagenDavidSymmetry()
    data = list(range(6))
    composed = symmetry.compose(1, 2)
    direct = symmetry.apply_operation(symmetry.apply_operation(data, 1), 2)
    table = symmetry.apply_operation(data, composed)
    assert tuple(direct) == tuple(table)


def test_key_schedule_generates_round_keys():
    schedule = MagenDavidKeySchedule(os.urandom(48))
    round_keys = schedule.generate_round_keys(12)
    assert len(round_keys) == 12
    assert all(len(key) == 32 for key in round_keys)
    assert len({key for key in round_keys}) == 12


def test_sbox_is_bijective_and_invertible():
    seed = b'magen_test_seed'
    sbox = MagenSBox(seed)
    assert len(set(sbox.sbox)) == 256
    inverse = sbox.inverse()
    for value in range(256):
        assert inverse[sbox.substitute(value)] == value


def test_hexagram_network_roundtrip():
    key_material = os.urandom(48)
    schedule = MagenDavidKeySchedule(key_material)
    round_keys = schedule.generate_round_keys(6)
    network = HexagramNetwork(round_keys)
    block = os.urandom(96)
    encrypted = network.encrypt_block(block)
    decrypted = network.decrypt_block(encrypted)
    assert decrypted == block


def test_vertex_generators_return_six_points():
    outer = hexagram_vertices()
    inner = central_hexagon_vertices()
    assert len(outer) == len(inner) == 6
    assert all(isinstance(point[0], float) for point in outer)
    assert all(isinstance(point[0], float) for point in inner)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
