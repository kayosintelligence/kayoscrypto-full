#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes unitários para o validador NIST SP 800-22 parcial."""

import os

import pytest

from .nist_sp800_22_validator import NIST_SP800_22_Validator


def test_run_all_tests_returns_expected_keys():
    """Valida que os quatro testes atualmente suportados são executados."""
    data = os.urandom(256)  # 2048 bits
    validator = NIST_SP800_22_Validator(data, alpha=0.01)
    results = validator.run_all_tests()

    expected_keys = {
        "frequency_monobit",
        "runs",
        "block_frequency",
        "longest_run",
    }
    assert expected_keys.issubset(results.keys())


@pytest.mark.parametrize(
    "pattern",
    [b"\x00", b"\xff", b"\x0f\xf0"],
)
def test_deterministic_patterns_fail_expanded_tests(pattern: bytes):
    """Padrões determinísticos devem falhar nos testes expandidos."""
    data = pattern * 256  # 2048 bits, múltiplo dos tamanhos de bloco
    validator = NIST_SP800_22_Validator(data, alpha=0.01)
    results = validator.run_all_tests()

    failing_tests = [
        name
        for name in ("frequency_monobit", "runs", "block_frequency", "longest_run")
        if not results[name]["passed"]
    ]
    assert failing_tests, "Padrão determinístico deve falhar em pelo menos um teste NIST"
    assert (
        not results["block_frequency"]["passed"]
        or not results["longest_run"]["passed"]
    ), "Padrão determinístico deve falhar em testes expandidos"