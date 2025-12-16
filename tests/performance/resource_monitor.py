#!/usr/bin/env python3
"""Monitoramento contínuo de CPU/memória/threads durante benchmarks."""

import os
import sys
import time
import threading
from typing import Callable, Dict, Any

import psutil

# Garantir acesso ao core
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.core.kayoscrypto_ultimate import KayosCryptoUltimate

PASSWORD = os.getenv("KAYOS_PASSWORD", "")


def monitor_resources(stop_event: threading.Event, interval: float = 0.5) -> Dict[str, Any]:
    process = psutil.Process()
    samples = []
    start_time = time.time()

    while not stop_event.is_set():
        cpu = psutil.cpu_percent(interval=None)
        mem = process.memory_info().rss / (1024 * 1024)
        threads = process.num_threads()
        timestamp = time.time() - start_time
        samples.append({
            "timestamp": timestamp,
            "cpu_percent": cpu,
            "memory_mb": mem,
            "threads": threads,
        })
        time.sleep(interval)

    return {
        "samples": samples,
        "summary": {
            "max_cpu_percent": max((s["cpu_percent"] for s in samples), default=0),
            "max_memory_mb": max((s["memory_mb"] for s in samples), default=0),
            "max_threads": max((s["threads"] for s in samples), default=0),
        }
    }


def run_with_monitor(task: Callable[[], Any], interval: float = 0.5) -> Dict[str, Any]:
    stop_event = threading.Event()
    monitor_result = {}

    def monitor_thread():
        nonlocal monitor_result
        monitor_result = monitor_resources(stop_event, interval=interval)

    t = threading.Thread(target=monitor_thread)
    t.start()
    start = time.time()
    task_result = task()
    elapsed = time.time() - start
    stop_event.set()
    t.join()

    return {
        "task_result": task_result,
        "elapsed": elapsed,
        "monitor": monitor_result,
    }


def run_monitored_encrypt(size_mb: int) -> Dict[str, Any]:
    data = os.urandom(size_mb * 1024 * 1024)
    cipher = KayosCryptoUltimate(
        use_concentric=True,
        use_direction=True,
        use_quantum=True,
        use_ed25519=False,
    )

    def task():
        result = cipher.encrypt(data, PASSWORD)
        if isinstance(result, dict) and "quantum_salt" in result:
            package = {"ciphertext": result["ciphertext"], "quantum_salt": result["quantum_salt"]}
        else:
            package = result
        recovered = cipher.decrypt(package, PASSWORD)
        assert recovered == data
        return "ok"

    report = run_with_monitor(task)
    report["size_mb"] = size_mb
    return report


def run_all_monitors():
    print("\n MONITORAMENTO DE RECURSOS - KAYOSCRYPTO")
    print("=" * 70)
    scenarios = [50, 100]
    reports = []
    for size in scenarios:
        print(f"\n▶  Carga {size} MB")
        report = run_monitored_encrypt(size)
        reports.append(report)
        monitor = report["monitor"]
        summary = monitor.get("summary", {})
        print(f"   Tempo total: {report['elapsed']:.2f}s")
        print(f"   CPU pico   : {summary.get('max_cpu_percent', 0):.1f}%")
        print(f"   Memória pico: {summary.get('max_memory_mb', 0):.1f} MB")
        print(f"   Threads pico: {summary.get('max_threads', 0)}")
        print(f"   Amostras   : {len(monitor.get('samples', []))}")
    print("\n Monitoramento concluído.\n")
    return reports


if __name__ == "__main__":
    run_all_monitors()
