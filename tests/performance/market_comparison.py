#!/usr/bin/env python3
"""Comparativo de performance KayosCrypto vs algoritmos de mercado."""

import os
import sys
import time
import statistics
import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple

import psutil
from Crypto.Cipher import AES, ChaCha20

# Garantir acesso ao core do KayosCrypto
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.core.kayoscrypto_ultimate import KayosCryptoUltimate


@dataclass
class TestResult:
    name: str
    metrics: Dict[str, Any] = field(default_factory=dict)


class KayosAdapter:
    """Adapter para KayosCryptoUltimate (config enterprise)."""

    def __init__(self) -> None:
        self.cipher = KayosCryptoUltimate(
            use_concentric=True,
            use_direction=True,
            use_quantum=True,
            use_ed25519=False,
        )

    def encrypt(self, data: bytes, password: str) -> Tuple[Any, Dict[str, Any]]:
        result = self.cipher.encrypt(data, password)
        if isinstance(result, dict) and "quantum_salt" in result:
            return result["ciphertext"], {"quantum_salt": result["quantum_salt"]}
        return result, {}

    def decrypt(self, payload: Any, password: str, metadata: Dict[str, Any]) -> bytes:
        if metadata.get("quantum_salt") is not None:
            package = {"ciphertext": payload, "quantum_salt": metadata["quantum_salt"]}
        else:
            package = payload
        return self.cipher.decrypt(package, password)


class AESAdapter:
    """Adapter para AES-256 em modo CTR."""

    def _derive_key(self, password: str) -> bytes:
        return hashlib.sha256(password.encode()).digest()

    def encrypt(self, data: bytes, password: str) -> Tuple[bytes, Dict[str, Any]]:
        key = self._derive_key(password)
        cipher = AES.new(key, AES.MODE_CTR)
        ciphertext = cipher.encrypt(data)
        return ciphertext, {"nonce": cipher.nonce}

    def decrypt(self, payload: bytes, password: str, metadata: Dict[str, Any]) -> bytes:
        key = self._derive_key(password)
        cipher = AES.new(key, AES.MODE_CTR, nonce=metadata["nonce"])
        return cipher.decrypt(payload)


class ChaChaAdapter:
    """Adapter para ChaCha20."""

    def _derive_key(self, password: str) -> bytes:
        # ChaCha20 requer chave de 32 bytes.
        return hashlib.sha256(password.encode()).digest()

    def encrypt(self, data: bytes, password: str) -> Tuple[bytes, Dict[str, Any]]:
        key = self._derive_key(password)
        nonce = os.urandom(12)  # 96 bits
        cipher = ChaCha20.new(key=key, nonce=nonce)
        ciphertext = cipher.encrypt(data)
        return ciphertext, {"nonce": nonce}

    def decrypt(self, payload: bytes, password: str, metadata: Dict[str, Any]) -> bytes:
        key = self._derive_key(password)
        cipher = ChaCha20.new(key=key, nonce=metadata["nonce"])
        return cipher.decrypt(payload)


ALGORITHMS = {
    "KayosCryptoUltimate": KayosAdapter,
    "AES-256-CTR": AESAdapter,
    "ChaCha20": ChaChaAdapter,
}

PASSWORD = os.getenv("KAYOS_PASSWORD", "")


def _time_operation(func, *args, **kwargs) -> Tuple[Any, float]:
    start = time.time()
    result = func(*args, **kwargs)
    elapsed = time.time() - start
    return result, elapsed


def throughput_real_world(adapter) -> TestResult:
    data_samples = {
        "Texto": b"Lorem ipsum dolor sit amet " * 1000,
        "JSON": b'{"data": ' + (b"x" * 24000) + b"}",
        "Binario": bytes((i % 256 for i in range(50000))),
    }

    metrics = {}
    encrypt_speeds = []

    for label, data in data_samples.items():
        payload, encrypt_time = _time_operation(adapter.encrypt, data, PASSWORD)

        if isinstance(payload, tuple):
            ciphertext, meta = payload
        else:
            ciphertext, meta = payload, {}

        recovered, decrypt_time = _time_operation(adapter.decrypt, ciphertext, PASSWORD, meta)

        integrity_ok = recovered == data
        size_kb = len(data) / 1024
        encrypt_speed = size_kb / encrypt_time if encrypt_time > 0 else 0
        decrypt_speed = size_kb / decrypt_time if decrypt_time > 0 else 0

        encrypt_speeds.append(encrypt_speed)
        metrics[label] = {
            "size_kb": size_kb,
            "encrypt_kb_s": encrypt_speed,
            "decrypt_kb_s": decrypt_speed,
            "integrity": integrity_ok,
        }

    metrics["average_encrypt_kb_s"] = sum(encrypt_speeds) / len(encrypt_speeds)
    return TestResult("Throughput Dados Reais", metrics)


def memory_usage(adapter) -> TestResult:
    data = os.urandom(1 * 1024 * 1024)  # 1 MB
    process = psutil.Process()
    before = process.memory_info().rss / 1024 / 1024
    payload, _ = _time_operation(adapter.encrypt, data, PASSWORD)
    if isinstance(payload, tuple):
        ciphertext, meta = payload
    else:
        ciphertext, meta = payload, {}
    recovered, _ = _time_operation(adapter.decrypt, ciphertext, PASSWORD, meta)
    after = process.memory_info().rss / 1024 / 1024

    return TestResult(
        "Uso de Memoria 1MB",
        {
            "mem_before_mb": before,
            "mem_after_mb": after,
            "mem_used_mb": after - before,
            "integrity": recovered == data,
        },
    )


def concurrent_performance(adapter, workers: int = 4) -> TestResult:
    data = b"Carga concorrente" * 200
    times = []

    for idx in range(workers):
        payload, elapsed = _time_operation(adapter.encrypt, data, f"{PASSWORD}_{idx}")
        times.append(elapsed)

        if isinstance(payload, tuple):
            ciphertext, meta = payload
        else:
            ciphertext, meta = payload, {}

        recovered, _ = _time_operation(adapter.decrypt, ciphertext, f"{PASSWORD}_{idx}", meta)
        assert recovered == data

    avg = statistics.mean(times)
    return TestResult(
        f"Performance Concorrente ({workers} ops)",
        {
            "avg_time_s": avg,
            "min_time_s": min(times),
            "max_time_s": max(times),
            "variation_pct": ((max(times) - min(times)) / avg * 100) if avg > 0 else 0,
        },
    )


def throughput_large(adapter, size_mb: int = 5) -> TestResult:
    data = os.urandom(size_mb * 1024 * 1024)

    payload, enc_time = _time_operation(adapter.encrypt, data, PASSWORD)
    if isinstance(payload, tuple):
        ciphertext, meta = payload
    else:
        ciphertext, meta = payload, {}

    recovered, dec_time = _time_operation(adapter.decrypt, ciphertext, PASSWORD, meta)

    enc_speed = size_mb / enc_time if enc_time > 0 else 0
    dec_speed = size_mb / dec_time if dec_time > 0 else 0

    return TestResult(
        f"Throughput {size_mb}MB",
        {
            "encrypt_mb_s": enc_speed,
            "decrypt_mb_s": dec_speed,
            "integrity": recovered == data,
        },
    )


def run_benchmark():
    print("\n COMPARATIVO DE PERFORMANCE - KAYOSCRYPTO VS MERCADO")
    print("=" * 70)

    for name, adapter_cls in ALGORITHMS.items():
        print(f"\n▶  {name}")
        print("-" * 70)
        adapter = adapter_cls()

        results = [
            throughput_real_world(adapter),
            memory_usage(adapter),
            concurrent_performance(adapter, workers=4),
            throughput_large(adapter, size_mb=5),
        ]

        for result in results:
            print(f"\n{result.name}:")
            for key, value in result.metrics.items():
                if isinstance(value, float):
                    print(f"   {key}: {value:.2f}")
                else:
                    print(f"   {key}: {value}")

    print("\nBenchmark concluído.\n")


if __name__ == "__main__":
    run_benchmark()
