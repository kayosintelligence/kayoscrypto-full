#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SATOR ORCHESTRATOR - Orquestrador Geométrico Multifacetado
==========================================================

Sistema de orquestração baseado no quadrante SATOR com grid 6-faces.
Integra todos os Ribs do KayosCrypto em uma estrutura geométrica unificada.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import hashlib

@dataclass
class FaceState:
    """Estado de uma face do grid multifacetado"""
    face_id: int  # 0-5 (cubo)
    is_verso: bool  # True = verso, False = anverso
    sator_grid: np.ndarray  # Grid 5x5 da face
    nucleus_srns: bytes  # Núcleo S.R.N.S da face
    fibonacci_mode: str  # 'verso' ou 'anverso'
    ezekiel_angles: Tuple[float, float, float]  # (x, y, z) angles
    star_david_hex: List[int]  # Aritmética hexagonal

class SatorOrchestrator:
    """
    Orquestrador SATOR - Grid Multifacetado 6-Faces

    Estrutura:
    - Face 0: Superior (Norte)
    - Face 1: Inferior (Sul)
    - Face 2: Frontal (Leste)
    - Face 3: Traseira (Oeste)
    - Face 4: Esquerda (vertical)
    - Face 5: Direita (vertical)

    Cada face tem verso/anverso e núcleo S.R.N.S vertical.
    """

    def __init__(self):
        self.faces: Dict[int, Dict[bool, FaceState]] = {}
        self.sator_base = np.array([
            ['S', 'A', 'T', 'O', 'R'],
            ['A', 'R', 'E', 'P', 'O'],
            ['T', 'E', 'N', 'E', 'T'],
            ['O', 'P', 'E', 'R', 'A'],
            ['R', 'O', 'T', 'A', 'S']
        ])

        # Núcleo S.R.N.S (SATOR ROTAS invertido)
        self.srns_nucleus = b'S.R.N.S'

        # Aritmética da Estrela de Davi (hexagonal)
        self.star_david_primes = [2, 3, 5, 7, 11, 13]  # 6 pontos

        self._initialize_faces()

    def _initialize_faces(self):
        """Inicializa as 6 faces com verso/anverso"""
        for face_id in range(6):
            for is_verso in [False, True]:  # anverso, verso
                # Criar grid SATOR rotacionado para cada face
                rotation_angle = (face_id * 60 + (180 if is_verso else 0)) % 360
                sator_grid = self._rotate_sator_grid(rotation_angle)

                # Núcleo S.R.N.S específico da face
                face_nucleus = self._generate_face_nucleus(face_id, is_verso)

                # Modo Fibonacci baseado na face
                fib_mode = 'verso' if face_id % 2 == 0 else 'anverso'

                # Ângulos Ezekiel (equilibrados para evitar colapsos)
                ezekiel_angles = self._calculate_ezekiel_angles(face_id, is_verso)

                # Aritmética Star of David
                hex_arithmetic = self._generate_star_david_hex(face_id, is_verso)

                face_state = FaceState(
                    face_id=face_id,
                    is_verso=is_verso,
                    sator_grid=sator_grid,
                    nucleus_srns=face_nucleus,
                    fibonacci_mode=fib_mode,
                    ezekiel_angles=ezekiel_angles,
                    star_david_hex=hex_arithmetic
                )

                if face_id not in self.faces:
                    self.faces[face_id] = {}
                self.faces[face_id][is_verso] = face_state

    def _rotate_sator_grid(self, angle: float) -> np.ndarray:
        """Rotaciona o grid SATOR geometricamente"""
        # Implementação simplificada - rotação por ângulos retos
        rotations = int(angle // 90) % 4
        grid = self.sator_base.copy()

        for _ in range(rotations):
            grid = np.rot90(grid)

        return grid

    def _generate_face_nucleus(self, face_id: int, is_verso: bool) -> bytes:
        """Gera núcleo S.R.N.S específico para cada face"""
        base = self.srns_nucleus
        # Modificar baseado na face e orientação
        face_modifier = bytes([face_id + (128 if is_verso else 0)])
        return base + face_modifier

    def _calculate_ezekiel_angles(self, face_id: int, is_verso: bool) -> Tuple[float, float, float]:
        """Calcula ângulos Ezekiel equilibrados para evitar colapsos gimbal"""
        # Usar ângulos que evitam lock gimbal (não múltiplos de 90°)
        base_angles = [37.5, 52.5, 67.5]  # Ângulos Ezekiel históricos aproximados

        # Modificar por face para distribuição equilibrada
        face_offset = face_id * 15  # 15° por face
        verso_offset = 7.5 if is_verso else 0

        return (
            (base_angles[0] + face_offset + verso_offset) * np.pi / 180,
            (base_angles[1] + face_offset + verso_offset) * np.pi / 180,
            (base_angles[2] + face_offset + verso_offset) * np.pi / 180
        )

    def _generate_star_david_hex(self, face_id: int, is_verso: bool) -> List[int]:
        """Gera aritmética da Estrela de Davi (hexagonal)"""
        # Usar números primos hexagonais e operações da estrela
        base_primes = self.star_david_primes.copy()

        # Modificar baseado na face
        for i in range(len(base_primes)):
            base_primes[i] = (base_primes[i] * (face_id + 1) + (1 if is_verso else 0)) % 256

        return base_primes

    def orchestrate_encryption(self, data: bytes, password: str,
                              fibonacci_engine, ezekiel_engine, core_engine) -> bytes:
        """
        Orquestra a criptografia através do grid multifacetado SATOR

        Args:
            data: Dados a criptografar
            password: Senha
            fibonacci_engine: Engine Fibonacci Direction
            ezekiel_engine: Engine Ezekiel Concentric
            core_engine: Engine Core

        Returns:
            Dados criptografados
        """
        # Derivar chave mestre
        master_key = hashlib.sha256(password.encode()).digest()

        # Processar através de todas as faces em ordem específica
        processed_data = data

        # Ordem de processamento: Norte->Sul->Leste->Oeste->Cima->Baixo
        face_order = [0, 1, 2, 3, 4, 5]  # N, S, E, W, U, D

        for face_id in face_order:
            for is_verso in [False, True]:  # anverso primeiro, depois verso
                face_state = self.faces[face_id][is_verso]

                # Aplicar núcleo S.R.N.S
                processed_data = self._apply_srns_nucleus(processed_data, face_state.nucleus_srns)

                # Aplicar direcionamento Fibonacci
                mode = face_state.fibonacci_mode
                processed_data = fibonacci_engine.apply_direction(
                    processed_data, master_key, mode, reverse=False
                )

                # Aplicar rotação Ezekiel (equilibrada)
                angles = face_state.ezekiel_angles
                processed_data = self._apply_ezekiel_rotation(
                    processed_data, angles, ezekiel_engine, reverse=False
                )

                # Aplicar aritmética Star of David
                processed_data = self._apply_star_david_arithmetic(
                    processed_data, face_state.star_david_hex
                )

        # Finalizar com sistema core
        processed_data = core_engine.encrypt(processed_data, password, level=3)

        return processed_data

    def orchestrate_decryption(self, data: bytes, password: str,
                              fibonacci_engine, ezekiel_engine, core_engine) -> bytes:
        """
        Orquestra a descriptografia em ordem reversa
        """
        # Derivar chave mestre
        master_key = hashlib.sha256(password.encode()).digest()

        # Iniciar com sistema core
        processed_data = core_engine.decrypt(data, password, level=3)

        # Ordem reversa: Baixo->Cima->Oeste->Leste->Sul->Norte
        face_order_reverse = [5, 4, 3, 2, 1, 0]  # D, U, W, E, S, N

        for face_id in face_order_reverse:
            for is_verso in [True, False]:  # verso primeiro (reverso), depois anverso
                face_state = self.faces[face_id][is_verso]

                # Reverter aritmética Star of David
                processed_data = self._apply_star_david_arithmetic(
                    processed_data, face_state.star_david_hex, reverse=True
                )

                # Reverter rotação Ezekiel
                angles = face_state.ezekiel_angles
                processed_data = self._apply_ezekiel_rotation(
                    processed_data, angles, ezekiel_engine, reverse=True
                )

                # Reverter direcionamento Fibonacci
                mode = face_state.fibonacci_mode
                processed_data = fibonacci_engine.apply_direction(
                    processed_data, master_key, mode, reverse=True
                )

                # Reverter núcleo S.R.N.S
                processed_data = self._apply_srns_nucleus(processed_data, face_state.nucleus_srns, reverse=True)

        return processed_data

    def _apply_srns_nucleus(self, data: bytes, nucleus: bytes, reverse: bool = False) -> bytes:
        """Aplica transformação baseada no núcleo S.R.N.S"""
        if reverse:
            # XOR reverso
            return bytes(b ^ n for b, n in zip(data, nucleus * (len(data) // len(nucleus) + 1)))
        else:
            # XOR direto
            return bytes(b ^ n for b, n in zip(data, nucleus * (len(data) // len(nucleus) + 1)))

    def _apply_ezekiel_rotation(self, data: bytes, angles: Tuple[float, float, float],
                               ezekiel_engine, reverse: bool) -> bytes:
        """Aplica rotação Ezekiel com ângulos equilibrados"""
        # Usar ângulo médio para evitar colapsos
        avg_angle = sum(angles) / len(angles)
        return ezekiel_engine.apply_concentric_rotation(data, avg_angle, reverse=reverse)

    def _apply_star_david_arithmetic(self, data: bytes, hex_values: List[int], reverse: bool = False) -> bytes:
        """Aplica aritmética da Estrela de Davi (hexagonal)"""
        result = bytearray(data)

        for i in range(len(result)):
            # Operação hexagonal: combinação dos 6 valores
            hex_op = sum(hex_values) % 256
            if reverse:
                result[i] = (result[i] - hex_op) % 256
            else:
                result[i] = (result[i] + hex_op) % 256

        return bytes(result)

    def get_orchestrator_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do orquestrador"""
        return {
            'total_faces': len(self.faces),
            'faces_with_verso_anverso': sum(len(orientations) for orientations in self.faces.values()),
            'sator_base_integrity': self._verify_sator_integrity(),
            'equilibrium_status': self._check_rotational_equilibrium()
        }

    def _verify_sator_integrity(self) -> bool:
        """Verifica integridade palindrômica do SATOR"""
        # O quadrado SATOR tem propriedades especiais:
        # 1. Pode ser lido em todas as direções (horizontal, vertical, diagonal)
        # 2. Diagonais são palíndromos
        # 3. Estrutura geométrica mantém simetria

        # Verificar diagonal principal (sempre palíndromo no SATOR)
        diagonal = ''.join(self.sator_base[i, i] for i in range(5))
        if diagonal != diagonal[::-1]:
            return False

        # Verificar diagonal secundária (sempre palíndromo no SATOR)
        diagonal_sec = ''.join(self.sator_base[i, 4-i] for i in range(5))
        if diagonal_sec != diagonal_sec[::-1]:
            return False

        # Verificar que o grid tem a estrutura correta do SATOR
        expected_sator = np.array([
            ['S', 'A', 'T', 'O', 'R'],
            ['A', 'R', 'E', 'P', 'O'],
            ['T', 'E', 'N', 'E', 'T'],
            ['O', 'P', 'E', 'R', 'A'],
            ['R', 'O', 'T', 'A', 'S']
        ])

        return np.array_equal(self.sator_base, expected_sator)

    def _check_rotational_equilibrium(self) -> str:
        """Verifica equilíbrio rotacional (sem colapsos gimbal)"""
        # Verificar se ângulos são distribuídos equilibradamente
        all_angles = []
        for face_states in self.faces.values():
            for face_state in face_states.values():
                all_angles.extend(face_state.ezekiel_angles)

        # Calcular variância - baixa variância = equilíbrio
        variance = np.var(all_angles)
        if variance < 0.1:
            return "EQUILIBRADO"
        elif variance < 0.5:
            return "MODERADAMENTE_EQUILIBRADO"
        else:
            return "DESQUILIBRADO"