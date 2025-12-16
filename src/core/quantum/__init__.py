#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KayosCrypto Quantum Module

Módulo de resistência pós-quântica e entropia geométrica.
"""

__version__ = "6.0.0-alpha"
__author__ = "KAYOS Systems"

# Importações dos 4 Ribs implementados
from .resistance_manager import QuantumResistanceManager
from .entropy_pool import GeometricEntropyPool
from .certification_tracker import CertificationTracker
from .palindrome_signatures import PalindromeSignatureSystem

__all__ = [
    'QuantumResistanceManager',
    'GeometricEntropyPool',
    'CertificationTracker',
    'PalindromeSignatureSystem',
]
