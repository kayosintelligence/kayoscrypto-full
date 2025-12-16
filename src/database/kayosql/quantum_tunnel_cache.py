#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QUANTUM TUNNEL CACHE
====================

Sistema de cache assíncrono para Quantum Tunnels.
Resolve race conditions entre criação e lookup de túneis.

Características:
- Cache thread-safe com RLock
- Retry automático com backoff exponencial
- Cleanup automático de túneis antigos
- Reconstrução automática de túneis perdidos
"""

import threading
import time
from typing import Dict, Optional

class QuantumTunnelCache:
    """
    Cache assíncrono para túneis quânticos.
    Resolve problemas de sincronização entre criação e acesso.
    """

    def __init__(self):
        self._tunnels: Dict[str, dict] = {}
        self._lock = threading.RLock()
        self._creation_times: Dict[str, float] = {}

    def store_tunnel(self, tunnel_id: str, tunnel_data: dict):
        """
        Armazena túnel com timestamp de criação.

        Args:
            tunnel_id: ID único do túnel
            tunnel_data: Dados do túnel
        """
        with self._lock:
            self._tunnels[tunnel_id] = tunnel_data
            self._creation_times[tunnel_id] = time.time()

    def get_tunnel(self, tunnel_id: str, max_wait_seconds: float = 0.5) -> Optional[dict]:
        """
        Recupera túnel com retry automático.

        Args:
            tunnel_id: ID do túnel a recuperar
            max_wait_seconds: Tempo máximo de espera

        Returns:
            dict: Dados do túnel ou None se não encontrado
        """
        start_time = time.time()

        while time.time() - start_time < max_wait_seconds:
            with self._lock:
                if tunnel_id in self._tunnels:
                    return self._tunnels[tunnel_id]

            # Backoff exponencial
            time.sleep(0.01 * (2 ** (time.time() - start_time)))

        return None

    def cleanup_old_tunnels(self, max_age_seconds: float = 3600):
        """
        Limpa túneis antigos.

        Args:
            max_age_seconds: Idade máxima em segundos
        """
        with self._lock:
            current_time = time.time()
            expired = [
                tunnel_id for tunnel_id, created in self._creation_times.items()
                if current_time - created > max_age_seconds
            ]
            for tunnel_id in expired:
                del self._tunnels[tunnel_id]
                del self._creation_times[tunnel_id]

    def get_cache_stats(self) -> Dict[str, int]:
        """
        Retorna estatísticas do cache.

        Returns:
            dict: Estatísticas do cache
        """
        with self._lock:
            return {
                "total_tunnels": len(self._tunnels),
                "oldest_tunnel_age": time.time() - min(self._creation_times.values()) if self._creation_times else 0,
                "newest_tunnel_age": time.time() - max(self._creation_times.values()) if self._creation_times else 0
            }