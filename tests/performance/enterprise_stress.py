#!/usr/bin/env python3
"""Testes de estresse para cargas enterprise (50-100 MB e alta concorrência)."""

import os
import sys
import time
import statistics
import hashlib
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, List, Type

import psutil
from Crypto.Cipher import AES, ChaCha20

# Garantir acesso ao core
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.core.kayoscrypto_ultimate import KayosCryptoUltimate

PASSWORD = os.getenv("KAYOS_PASSWORD", "")


@dataclass
class MetricBlock:
    name: str
    metrics: Dict[str, Any] = field(default_factory=dict)


class AlgorithmAdapter:
    def encrypt(self, data: bytes, password: str) -> Tuple[bytes, Dict[str, Any]]:
        raise NotImplementedError

    def decrypt(self, payload: bytes, password: str, metadata: Dict[str, Any]) -> bytes:
        raise NotImplementedError


class KayosAdapter(AlgorithmAdapter):
    def __init__(self) -> None:
        self.cipher = KayosCryptoUltimate(
            use_concentric=True,
            use_direction=True,
            use_quantum=True,
            use_ed25519=False,
        )

    def encrypt(self, data: bytes, password: str) -> Tuple[bytes, Dict[str, Any]]:
        result = self.cipher.encrypt(data, password)
        if isinstance(result, dict) and "quantum_salt" in result:
            return result["ciphertext"], {"quantum_salt": result["quantum_salt"]}
        return result, {}

    def decrypt(self, payload: bytes, password: str, metadata: Dict[str, Any]) -> bytes:
        if metadata.get("quantum_salt") is not None:
            package = {"ciphertext": payload, "quantum_salt": metadata["quantum_salt"]}
        else:
            package = payload
        return self.cipher.decrypt(package, password)


class AESAdapter(AlgorithmAdapter):
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


class ChaChaAdapter(AlgorithmAdapter):
    def _derive_key(self, password: str) -> bytes:
        return hashlib.sha256(password.encode()).digest()

    def encrypt(self, data: bytes, password: str) -> Tuple[bytes, Dict[str, Any]]:
        key = self._derive_key(password)
        nonce = os.urandom(12)
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


def _time_call(func, *args, **kwargs) -> Tuple[Any, float]:
    start = time.perf_counter()
    result = func(*args, **kwargs)
    return result, time.perf_counter() - start


def throughput_large_files(adapter: AlgorithmAdapter, sizes_mb: List[int]) -> MetricBlock:
    metrics: Dict[str, Dict[str, Any]] = {}
    for size in sizes_mb:
        data = os.urandom(size * 1024 * 1024)
        payload, enc_time = _time_call(adapter.encrypt, data, PASSWORD)
        if isinstance(payload, tuple):  # safety, though adapters return tuple
            ciphertext, meta = payload
        else:
            ciphertext, meta = payload, {}

        recovered, dec_time = _time_call(adapter.decrypt, ciphertext, PASSWORD, meta)
        metrics[f"{size}MB"] = {
            "encrypt_mb_s": (size / enc_time) if enc_time > 0 else 0,
            "decrypt_mb_s": (size / dec_time) if dec_time > 0 else 0,
            "integrity": recovered == data,
            "enc_time_s": enc_time,
            "dec_time_s": dec_time,
        }
        # liberar memória
        del data, ciphertext, recovered
    return MetricBlock("Throughput Grandes Cargas", metrics)


def memory_profile(adapter: AlgorithmAdapter, size_mb: int) -> MetricBlock:
    data = os.urandom(size_mb * 1024 * 1024)
    process = psutil.Process()
    before = process.memory_info().rss / 1024 / 1024
    payload, _ = _time_call(adapter.encrypt, data, PASSWORD)
    if isinstance(payload, tuple):
        ciphertext, meta = payload
    else:
        ciphertext, meta = payload, {}
    recovered, _ = _time_call(adapter.decrypt, ciphertext, PASSWORD, meta)
    after = process.memory_info().rss / 1024 / 1024
    metrics = {
        "mem_before_mb": before,
        "mem_after_mb": after,
        "mem_used_mb": after - before,
        "integrity": recovered == data,
    }
    del data, ciphertext, recovered
    return MetricBlock(f"Uso de Memoria {size_mb}MB", metrics)


def concurrent_load(adapter_cls: Type[AlgorithmAdapter], workers: int, payload_kb: int) -> MetricBlock:
    data = os.urandom(payload_kb * 1024)
    times: List[float] = []

    def worker(idx: int) -> float:
        adapter = adapter_cls()
        password = f"{PASSWORD}_{idx}"
        payload, enc_time = _time_call(adapter.encrypt, data, password)
        if isinstance(payload, tuple):
            ciphertext, meta = payload
        else:
            ciphertext, meta = payload, {}
        recovered, _ = _time_call(adapter.decrypt, ciphertext, password, meta)
        assert recovered == data
        return enc_time

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(worker, idx) for idx in range(workers)]
        for future in futures:
            times.append(future.result())

    metrics = {
        "workers": workers,
        "payload_kb": payload_kb,
        "avg_time_s": statistics.mean(times),
        "min_time_s": min(times),
        "max_time_s": max(times),
        "variation_pct": ((max(times) - min(times)) / statistics.mean(times) * 100) if times else 0,
    }
    del data
    return MetricBlock(f"Carga Concorrente ({workers} ops)", metrics)


def run_stress_suite():
    print("\n TESTE DE ESTRESSE ENTERPRISE (50-100 MB)")
    print("=" * 78)

    for name, adapter_cls in ALGORITHMS.items():
        print(f"\n▶  {name}")
        print("-" * 78)
        adapter = adapter_cls()

        tests = [
            throughput_large_files(adapter, [50, 100]),
            memory_profile(adapter, 100),
            concurrent_load(adapter_cls, workers=8, payload_kb=2048),
            concurrent_load(adapter_cls, workers=16, payload_kb=2048),
        ]

        for block in tests:
            print(f"\n{block.name}:")
            for key, value in block.metrics.items():
                if isinstance(value, float):
                    print(f"   {key}: {value:.2f}")
                elif isinstance(value, dict):
                    print(f"   {key}:")
                    for sub_key, sub_val in value.items():
                        if isinstance(sub_val, float):
                            print(f"      {sub_key}: {sub_val:.2f}")
                        else:
                            print(f"      {sub_key}: {sub_val}")
                else:
                    print(f"   {key}: {value}")

    print("\n Teste de estresse concluído.\n")


if __name__ == "__main__":
    run_stress_suite()
