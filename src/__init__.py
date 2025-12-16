"""KayosCrypto - Sistema de Criptografia Enterprise"""
__version__ = "5.0.1"

try:
    from .core.kayoscrypto_ultimate import KayosCryptoUltimate
except ImportError:
    from core.kayoscrypto_ultimate import KayosCryptoUltimate

__all__ = ['KayosCryptoUltimate']
