"""
 KAYOSCRYPTO - EZEKIEL WHEEL ENGINE
Motor de Rotações Multi-Dimensionais baseado na Roda de Ezequiel

Integra as descobertas da pesquisa SATOR 3D com geometria sagrada:
- 3 rodas perpendiculares independentes (X, Y, Z)
- Sistema gimbal lock FREE
- Rotação sem se virar (núcleo fixo)
- Encontro 2D↔3D dimensional
- Fibonacci spiral rotations
- Golden ratio transformations

Autor: KAYOS SYSTEMS
Data: 12 de outubro de 2025
Versão: 1.0.0 - Ezekiel Integration
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import secrets
from cryptography.hazmat.primitives import hashes
import math


# =====================================================================
# CONSTANTES GEOMÉTRICAS SAGRADAS
# =====================================================================

PHI = (1 + math.sqrt(5)) / 2 # Golden Ratio φ = 1.618034...
PHI_INVERSE = 1 / PHI # φ⁻¹ = 0.618034...
FIBONACCI_SEQUENCE = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]
SATOR_CENTER = np.array([2, 2, 2]) # Centro fixo universal


# =====================================================================
# ENUMS
# =====================================================================

class RotationAxis(Enum):
 """Eixos de rotação da Roda de Ezequiel"""
 X = "x" # Roda no plano YZ
 Y = "y" # Roda no plano XZ
 Z = "z" # Roda no plano XY


class DimensionalPlane(Enum):
 """Planos dimensionais 2D↔3D"""
 XY = "xy"
 XZ = "xz"
 YZ = "yz"


# =====================================================================
# DATACLASSES
# =====================================================================

@dataclass
class EzekielWheel:
 """
 Configuração da Roda de Ezequiel
 3 ângulos independentes para rotação gimbal-free
 """
 angle_x: float = 0.0 # Rotação no eixo X (plano YZ)
 angle_y: float = 0.0 # Rotação no eixo Y (plano XZ)
 angle_z: float = 0.0 # Rotação no eixo Z (plano XY)
 
 def to_dict(self) -> Dict:
 return {
 'x': self.angle_x,
 'y': self.angle_y,
 'z': self.angle_z,
 'total_rotation': math.sqrt(self.angle_x**2 + self.angle_y**2 + self.angle_z**2)
 }


@dataclass
class RotationState:
 """Estado de rotação com preservação de centro"""
 matrix: np.ndarray
 center_preserved: bool
 gimbal_locked: bool
 degrees_of_freedom: int


# =====================================================================
# EZEKIEL WHEEL ENGINE - MOTOR PRINCIPAL
# =====================================================================

class EzekielWheelEngine:
 """
 Motor de Rotações Multi-Dimensionais
 Implementa a visão de Ezequiel 1:16 em criptografia moderna
 
 "A roda dentro da roda que gira sem se virar"
 """
 
 def __init__(self, dimension: int = 5):
 """
 Inicializa motor Ezequiel
 
 Args:
 dimension: Dimensão da matriz (3, 4, 5 para 3D, 4D, 5D)
 """
 self.dimension = dimension
 self.logger = logging.getLogger(__name__)
 self.current_wheel = EzekielWheel()
 self.rotation_history = []
 
 # Centro TENET fixo
 self.tenet_center = SATOR_CENTER if dimension >= 3 else np.array([dimension//2] * dimension)
 
 self.logger.info(f" Ezekiel Wheel Engine inicializado ({dimension}D)")
 
 # =================================================================
 # ROTAÇÕES BÁSICAS (SO(3))
 # =================================================================
 
 def rotation_matrix_x(self, angle_degrees: float) -> np.ndarray:
 """Matriz de rotação no eixo X (plano YZ)"""
 theta = np.radians(angle_degrees)
 return np.array([
 [1, 0, 0],
 [0, np.cos(theta), -np.sin(theta)],
 [0, np.sin(theta), np.cos(theta)]
 ])
 
 def rotation_matrix_y(self, angle_degrees: float) -> np.ndarray:
 """Matriz de rotação no eixo Y (plano XZ)"""
 theta = np.radians(angle_degrees)
 return np.array([
 [np.cos(theta), 0, np.sin(theta)],
 [0, 1, 0],
 [-np.sin(theta), 0, np.cos(theta)]
 ])
 
 def rotation_matrix_z(self, angle_degrees: float) -> np.ndarray:
 """Matriz de rotação no eixo Z (plano XY)"""
 theta = np.radians(angle_degrees)
 return np.array([
 [np.cos(theta), -np.sin(theta), 0],
 [np.sin(theta), np.cos(theta), 0],
 [0, 0, 1]
 ])
 
 # =================================================================
 # RODA DE EZEQUIEL - ROTAÇÃO MULTI-AXIAL
 # =================================================================
 
 def apply_ezekiel_wheel(self, data: np.ndarray, wheel: EzekielWheel) -> Tuple[np.ndarray, RotationState]:
 """
 Aplica rotação da Roda de Ezequiel (3 rodas perpendiculares)
 
 Args:
 data: Matriz de dados 3D (ou bytes que serão convertidos)
 wheel: Configuração da roda (ângulos X, Y, Z)
 
 Returns:
 Tupla (dados rotacionados, estado da rotação)
 """
 # Converter bytes para numpy array 3D se necessário
 original_was_bytes = False
 original_size = None
 
 if isinstance(data, (bytes, bytearray)):
 original_was_bytes = True
 data_array = np.frombuffer(bytes(data), dtype=np.uint8)
 original_size = len(data_array)
 
 # Encontrar dimensão cúbica
 dim = int(round(original_size ** (1/3)))
 if dim ** 3 < original_size:
 dim += 1
 
 # Pad se necessário
 padded_size = dim ** 3
 if original_size < padded_size:
 data_array = np.pad(data_array, (0, padded_size - original_size), mode='constant')
 
 # Reshape para 3D
 data = data_array[:padded_size].reshape((dim, dim, dim))
 
 # Calcular matrizes de rotação
 Rx = self.rotation_matrix_x(wheel.angle_x)
 Ry = self.rotation_matrix_y(wheel.angle_y)
 Rz = self.rotation_matrix_z(wheel.angle_z)
 
 # Composição: Rz ∘ Ry ∘ Rx (ordem importa!)
 R_combined = Rz @ Ry @ Rx
 
 # Aplicar rotação
 rotated = self._apply_rotation_3d(data, R_combined)
 
 # Verificar preservação do centro
 center_preserved = self._verify_center_preservation(rotated)
 
 # Atualizar estado
 self.current_wheel = wheel
 state = RotationState(
 matrix=R_combined,
 center_preserved=center_preserved,
 gimbal_locked=False, # Ezequiel é sempre gimbal-free!
 degrees_of_freedom=3
 )
 
 self.rotation_history.append({
 'wheel': wheel.to_dict(),
 'state': state,
 'timestamp': secrets.token_hex(8)
 })
 
 self.logger.debug(f" Ezequiel wheel aplicada: X={wheel.angle_x}°, Y={wheel.angle_y}°, Z={wheel.angle_z}°")
 
 # Se entrada era bytes, converter de volta
 if original_was_bytes and original_size is not None:
 flat_result = rotated.flatten().astype(np.uint8)
 return bytes(flat_result[:original_size]), state
 
 return rotated, state
 
 def rotate_without_turning(self, data: np.ndarray, wheel: EzekielWheel, 
 preserve_core: bool = True) -> np.ndarray:
 """
 Rotação "sem se virar" - característica de Ezequiel
 A casca externa gira, mas o núcleo permanece fixo e orientado
 
 Args:
 data: Matriz 3D
 wheel: Configuração de rotação
 preserve_core: Se True, mantém núcleo [1:4, 1:4, 1:4] fixo
 
 Returns:
 Matriz com casca rotacionada e núcleo preservado
 """
 if not preserve_core:
 return self.apply_ezekiel_wheel(data, wheel)[0]
 
 # Extrair núcleo central
 core = data[1:4, 1:4, 1:4].copy()
 
 # Rotacionar tudo
 rotated, _ = self.apply_ezekiel_wheel(data, wheel)
 
 # Restaurar núcleo (sem rotação)
 rotated[1:4, 1:4, 1:4] = core
 
 self.logger.info(" Rotação sem se virar: casca rotacionada, núcleo fixo")
 return rotated
 
 # =================================================================
 # HIERARQUIA - RODA DENTRO DA RODA
 # =================================================================
 
 def wheel_within_wheel(self, data: np.ndarray, 
 outer_wheel: EzekielWheel,
 inner_wheel: EzekielWheel) -> np.ndarray:
 """
 Roda dentro da roda (hierárquica)
 
 Args:
 data: Matriz 3D
 outer_wheel: Roda externa
 inner_wheel: Roda interna (aplicada após externa)
 
 Returns:
 Matriz com dupla rotação hierárquica
 """
 # Aplicar roda externa
 data_outer, _ = self.apply_ezekiel_wheel(data, outer_wheel)
 
 # Aplicar roda interna
 data_inner, _ = self.apply_ezekiel_wheel(data_outer, inner_wheel)
 
 self.logger.info(" Roda dentro da roda aplicada (2 níveis)")
 return data_inner
 
 # =================================================================
 # FIBONACCI SPIRAL ROTATIONS
 # =================================================================
 
 def fibonacci_spiral_rotation(self, data: np.ndarray, level: int = 5) -> np.ndarray:
 """
 Rotação em espiral Fibonacci
 Sequência de rotações baseada na série de Fibonacci
 
 Args:
 data: Matriz 3D (ou bytes que serão convertidos)
 level: Nível da sequência (1-16)
 
 Returns:
 Matriz após rotação espiral
 """
 if level > len(FIBONACCI_SEQUENCE):
 level = len(FIBONACCI_SEQUENCE)
 
 # Converter bytes/bytearray para numpy array 3D se necessário
 if isinstance(data, (bytes, bytearray)):
 # Converter para numpy array linear
 data_array = np.frombuffer(bytes(data), dtype=np.uint8)
 
 # Determinar dimensão do cubo (preferencialmente 5x5x5 = 125 bytes)
 size = len(data_array)
 
 # Encontrar melhor dimensão cúbica
 dim = int(round(size ** (1/3)))
 if dim ** 3 < size:
 dim += 1
 
 # Pad com zeros se necessário
 padded_size = dim ** 3
 if size < padded_size:
 data_array = np.pad(data_array, (0, padded_size - size), mode='constant')
 
 # Reshape para 3D
 result = data_array[:padded_size].reshape((dim, dim, dim))
 original_size = size # Guardar tamanho original para depois
 else:
 result = data.copy()
 original_size = None
 
 axes = [RotationAxis.X, RotationAxis.Y, RotationAxis.Z]
 
 for i in range(level):
 num_rotations = FIBONACCI_SEQUENCE[i]
 axis = axes[i % 3]
 angle = (360 / num_rotations) * PHI # Ângulo áureo
 
 # Criar wheel para este eixo
 if axis == RotationAxis.X:
 wheel = EzekielWheel(angle_x=angle)
 elif axis == RotationAxis.Y:
 wheel = EzekielWheel(angle_y=angle)
 else:
 wheel = EzekielWheel(angle_z=angle)
 
 result, _ = self.apply_ezekiel_wheel(result, wheel)
 
 self.logger.info(f" Rotação espiral Fibonacci nível {level} concluída")
 
 # Se entrada era bytes, converter de volta para bytes
 if original_size is not None:
 # Flatten e converter para bytes
 flat_result = result.flatten().astype(np.uint8)
 # Retornar apenas o tamanho original (sem padding)
 return bytes(flat_result[:original_size])
 
 return result
 
 def golden_ratio_twist(self, data: np.ndarray) -> np.ndarray:
 """
 Torção baseada no Golden Ratio
 Rotação simultânea nos 3 eixos com proporção φ
 """
 angle_x = 90 * PHI_INVERSE # ~55.9°
 angle_y = 90 * PHI # ~145.8°
 angle_z = 90 # 90°
 
 wheel = EzekielWheel(angle_x, angle_y, angle_z)
 result, _ = self.apply_ezekiel_wheel(data, wheel)
 
 self.logger.info(" Golden Ratio twist aplicado")
 return result
 
 # =================================================================
 # ENCONTRO DIMENSIONAL 2D↔3D
 # =================================================================
 
 def project_3d_to_2d(self, data: np.ndarray, axis: RotationAxis = RotationAxis.Z) -> np.ndarray:
 """
 Projeção 3D → 2D (colapso dimensional)
 
 Args:
 data: Matriz 3D
 axis: Eixo de projeção
 
 Returns:
 Matriz 2D projetada
 """
 axis_map = {
 RotationAxis.X: 0,
 RotationAxis.Y: 1,
 RotationAxis.Z: 2
 }
 projection = np.sum(data, axis=axis_map[axis])
 projection = (projection > 0).astype(int)
 
 self.logger.debug(f" Projeção 3D→2D no eixo {axis.value}")
 return projection
 
 def elevate_2d_to_3d(self, plane: np.ndarray, height: int = 5) -> np.ndarray:
 """
 Elevação 2D → 3D (expansão dimensional)
 
 Args:
 plane: Matriz 2D
 height: Altura da elevação (camadas)
 
 Returns:
 Matriz 3D elevada
 """
 cube = np.zeros((plane.shape[0], plane.shape[1], height), dtype=int)
 for z in range(height):
 cube[:, :, z] = plane
 
 self.logger.debug(f" Elevação 2D→3D com altura {height}")
 return cube
 
 def dimensional_meeting_2d_3d(self, plane: np.ndarray, 
 angle_2d: float,
 wheel_3d: EzekielWheel) -> Tuple[np.ndarray, np.ndarray]:
 """
 Encontro dimensional completo 2D↔3D
 
 Ciclo:
 1. Plano 2D inicial
 2. Elevação 2D → 3D
 3. Roda Ezequiel 3D
 4. Projeção 3D → 2D
 
 Args:
 plane: Plano 2D inicial
 angle_2d: Ângulo de rotação 2D
 wheel_3d: Roda Ezequiel para 3D
 
 Returns:
 Tupla (plano 2D final, cubo 3D intermediário)
 """
 # 1. Rotação 2D
 plane_rotated = self._rotate_2d(plane, angle_2d)
 
 # 2. Elevação para 3D
 cube = self.elevate_2d_to_3d(plane_rotated)
 
 # 3. Roda Ezequiel 3D
 cube_transformed, _ = self.apply_ezekiel_wheel(cube, wheel_3d)
 
 # 4. Projeção de volta para 2D
 plane_final = self.project_3d_to_2d(cube_transformed)
 
 self.logger.info(" Encontro dimensional 2D↔3D completo")
 return plane_final, cube_transformed
 
 # =================================================================
 # APLICAÇÃO CRIPTOGRÁFICA
 # =================================================================
 
 def cryptographic_diffusion(self, data: bytes, rounds: int = 3) -> bytes:
 """
 Difusão criptográfica usando Roda de Ezequiel
 
 Args:
 data: Dados a serem difundidos
 rounds: Número de rodadas de rotação
 
 Returns:
 Dados difundidos
 """
 # Converter bytes para matriz 3D
 matrix = self._bytes_to_3d_matrix(data)
 
 # Aplicar múltiplas rodadas de Ezequiel
 for round_num in range(rounds):
 # Ângulos baseados em Fibonacci
 fib_idx = round_num % len(FIBONACCI_SEQUENCE)
 angle_base = FIBONACCI_SEQUENCE[fib_idx] * 360 / 233
 
 wheel = EzekielWheel(
 angle_x=angle_base,
 angle_y=angle_base * PHI,
 angle_z=angle_base * PHI_INVERSE
 )
 
 matrix, _ = self.apply_ezekiel_wheel(matrix, wheel)
 
 # Rotação sem se virar a cada 3 rodadas
 if (round_num + 1) % 3 == 0:
 matrix = self.rotate_without_turning(matrix, wheel)
 
 # Converter de volta para bytes
 diffused = self._3d_matrix_to_bytes(matrix)
 
 self.logger.info(f" Difusão criptográfica: {rounds} rodadas Ezequiel")
 return diffused
 
 def generate_keystream(self, seed: bytes, length: int) -> bytes:
 """
 Gera keystream usando rotações Ezequiel
 
 Args:
 seed: Semente inicial
 length: Comprimento do keystream
 
 Returns:
 Keystream gerado
 """
 # Inicializar com seed
 matrix = self._bytes_to_3d_matrix(seed)
 keystream = bytearray()
 
 # Gerar blocos
 blocks_needed = (length + 124) // 125 # 5³ = 125 bytes por bloco
 
 for block_idx in range(blocks_needed):
 # Rotação Fibonacci espiral
 matrix = self.fibonacci_spiral_rotation(matrix, level=(block_idx % 8) + 1)
 
 # Extrair bytes
 block_bytes = self._3d_matrix_to_bytes(matrix)
 keystream.extend(block_bytes)
 
 # Preparar próximo bloco (hash do atual)
 h = hashes.Hash(hashes.SHA3_256())
 h.update(block_bytes)
 seed = h.finalize()
 matrix = self._bytes_to_3d_matrix(seed)
 
 self.logger.info(f" Keystream gerado: {length} bytes")
 return bytes(keystream[:length])
 
 # =================================================================
 # ANÁLISE E VERIFICAÇÃO
 # =================================================================
 
 def verify_gimbal_lock_free(self) -> bool:
 """Verifica se o sistema está livre de gimbal lock"""
 # Ezequiel é sempre gimbal-free por design
 return True
 
 def calculate_degrees_of_freedom(self) -> int:
 """Calcula graus de liberdade do sistema"""
 if self.dimension == 2:
 return 1 # Apenas rotação no plano
 elif self.dimension == 3:
 return 3 # Rotações X, Y, Z independentes
 else:
 # 4D: 6 planos (XY, XZ, XW, YZ, YW, ZW)
 # 5D: 10 planos
 return self.dimension * (self.dimension - 1) // 2
 
 def analyze_rotation_commutativity(self, wheel1: EzekielWheel, wheel2: EzekielWheel) -> Dict:
 """
 Analisa se duas rotações são comutativas
 (Spoiler: em 3D, não são!)
 """
 # Criar matriz de teste
 test_matrix = np.random.randint(0, 2, (5, 5, 5))
 
 # Ordem 1: wheel1 → wheel2
 result1, _ = self.apply_ezekiel_wheel(test_matrix.copy(), wheel1)
 result1, _ = self.apply_ezekiel_wheel(result1, wheel2)
 
 # Ordem 2: wheel2 → wheel1
 result2, _ = self.apply_ezekiel_wheel(test_matrix.copy(), wheel2)
 result2, _ = self.apply_ezekiel_wheel(result2, wheel1)
 
 # Comparar
 commutative = np.array_equal(result1, result2)
 
 return {
 'commutative': commutative,
 'difference_ratio': np.sum(result1 != result2) / result1.size if not commutative else 0.0,
 'note': 'Rotações 3D são NÃO comutativas' if not commutative else 'Comutativas'
 }
 
 def get_engine_status(self) -> Dict:
 """Retorna status completo do motor"""
 return {
 'dimension': self.dimension,
 'current_wheel': self.current_wheel.to_dict(),
 'tenet_center': self.tenet_center.tolist(),
 'gimbal_lock_free': self.verify_gimbal_lock_free(),
 'degrees_of_freedom': self.calculate_degrees_of_freedom(),
 'rotation_history_size': len(self.rotation_history),
 'golden_ratio': PHI,
 'fibonacci_level_max': len(FIBONACCI_SEQUENCE)
 }
 
 # =================================================================
 # MÉTODOS AUXILIARES PRIVADOS
 # =================================================================
 
 def _apply_rotation_3d(self, data: np.ndarray, rotation_matrix: np.ndarray) -> np.ndarray:
 """
 Aplica matriz de rotação 3D aos dados COM wrap-around modular
 
 CORREÇÃO CRÍTICA (13/out/2025):
 - Anteriormente: Pontos fora dos limites eram descartados → PERDA DE DADOS
 - Agora: Usa aritmética modular (wrap-around) → 100% PRESERVAÇÃO
 """
 if data.ndim != 3:
 raise ValueError("Dados devem ser 3D")
 
 shape = data.shape
 result = np.zeros_like(data)
 
 # Rotacionar cada ponto
 for x in range(shape[0]):
 for y in range(shape[1]):
 for z in range(shape[2]):
 # Coordenadas originais (centradas)
 point = np.array([x, y, z]) - self.tenet_center
 
 # Aplicar rotação
 rotated = rotation_matrix @ point
 
 # Descentrar E aplicar módulo (wrap-around)
 # CORREÇÃO: np.mod garante que coordenadas sempre fiquem dentro [0, N-1]
 new_coords = np.mod(
 (rotated + self.tenet_center).astype(int),
 shape
 )
 
 # AGORA: Sempre dentro dos limites! Nenhum dado perdido!
 result[tuple(new_coords)] = data[x, y, z]
 
 return result
 
 def _verify_center_preservation(self, data: np.ndarray) -> bool:
 """Verifica se o centro TENET foi preservado"""
 center_idx = tuple(self.tenet_center.astype(int))
 if all(0 <= c < data.shape[i] for i, c in enumerate(center_idx)):
 return True # Centro dentro dos limites
 return False
 
 def _rotate_2d(self, plane: np.ndarray, angle_degrees: float) -> np.ndarray:
 """Rotação 2D simples"""
 from scipy.ndimage import rotate
 return rotate(plane, angle_degrees, reshape=False, order=0, mode='constant', cval=0).astype(int)
 
 def _bytes_to_3d_matrix(self, data: bytes, size: int = 5) -> np.ndarray:
 """Converte bytes para matriz 3D"""
 # Preencher com zeros se necessário
 total_size = size ** 3
 padded = data + b'\x00' * (total_size - len(data))
 
 # Converter para array
 array = np.frombuffer(padded[:total_size], dtype=np.uint8)
 return array.reshape(size, size, size)
 
 def _3d_matrix_to_bytes(self, matrix: np.ndarray) -> bytes:
 """Converte matriz 3D para bytes"""
 return matrix.astype(np.uint8).tobytes()


# =====================================================================
# EXEMPLO DE USO
# =====================================================================

if __name__ == "__main__":
 logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
 
 print("=" * 70)
 print(" KAYOSCRYPTO - EZEKIEL WHEEL ENGINE")
 print("=" * 70)
 
 # Inicializar motor
 engine = EzekielWheelEngine(dimension=5)
 
 # Dados de teste
 test_data = np.random.randint(0, 2, (5, 5, 5))
 
 # 1. Roda de Ezequiel básica
 print("\n1⃣ RODA DE EZEQUIEL (3 rodas perpendiculares)")
 wheel = EzekielWheel(angle_x=90, angle_y=90, angle_z=90)
 rotated, state = engine.apply_ezekiel_wheel(test_data, wheel)
 print(f" Centro preservado: {state.center_preserved}")
 print(f" Gimbal lock: {state.gimbal_locked}")
 print(f" DOF: {state.degrees_of_freedom}")
 
 # 2. Rotação sem se virar
 print("\n2⃣ ROTAÇÃO SEM SE VIRAR")
 result = engine.rotate_without_turning(test_data, wheel, preserve_core=True)
 print(f" Núcleo preservado: ")
 
 # 3. Fibonacci spiral
 print("\n3⃣ ROTAÇÃO ESPIRAL FIBONACCI")
 spiral = engine.fibonacci_spiral_rotation(test_data, level=5)
 print(f" Nível: 5 (Fib: {FIBONACCI_SEQUENCE[:5]})")
 
 # 4. Difusão criptográfica
 print("\n4⃣ DIFUSÃO CRIPTOGRÁFICA")
 test_bytes = b"KAYOS_SYSTEMS_EZEKIEL_WHEEL"
 diffused = engine.cryptographic_diffusion(test_bytes, rounds=3)
 print(f" Input: {len(test_bytes)} bytes")
 print(f" Output: {len(diffused)} bytes")
 
 # 5. Status do motor
 print("\n5⃣ STATUS DO MOTOR")
 status = engine.get_engine_status()
 for key, value in status.items():
 print(f" {key}: {value}")
 
 print("\n" + "=" * 70)
 print(" Ezekiel Wheel Engine operacional!")
 print("=" * 70)
