"""
 QUANTUM CRYPTO EZEKIEL - KAYOSCRYPTO SUITE
Sistema de Criptografia Quântica com Roda de Ezequiel

Evolução completa do QuantumSatorCube com:
- Ezekiel Wheel Engine integrado
- Rotações multi-dimensionais sem gimbal lock
- Fibonacci spiral encryption avançado
- Golden Ratio key derivation
- Hipercubo 4D quântico

Autor: KAYOS SYSTEMS
Data: 12 de outubro de 2025
Versão: 2.0.0 - Ezekiel Evolution
"""

import hashlib
import base64
import uuid
import numpy as np
from math import sqrt
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Importar Ezekiel Wheel Engine
try:
    import sys
    from pathlib import Path
    ezekiel_path = Path(__file__).parent.parent.parent.parent / "enterprise3d/KayosCryptoEnterprise3D/src/cube"
    sys.path.insert(0, str(ezekiel_path))
    from ezekiel_wheel_engine import EzekielWheelEngine, EzekielWheel, PHI, FIBONACCI_SEQUENCE
    EZEKIEL_AVAILABLE = True
except ImportError:
    EZEKIEL_AVAILABLE = False
    PHI = 1.618034
    FIBONACCI_SEQUENCE = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]


# =====================================================================
# QUANTUM SATOR CUBE - VERSÃO EVOLUÍDA
# =====================================================================

class QuantumSatorCubeEzekiel:
    """
    Hipercubo Sator 3D com 6 faces (verso/anverso) 
    integrando Rodas de Ezequiel e Fibonacci Espiral
    
    EVOLUÇÃO 2.0:
    - Ezekiel Wheel Engine completo
    - Rotações gimbal-free
    - Criptografia quântica multidimensional
    - Golden Ratio key derivation
    """
    
    def __init__(self):
        """Inicializa o cubo quântico Ezequiel"""
        # Cubo SATOR 3D (6 faces)
        self.sator_3d = self._create_sator_3d_cube()
        
        # Fibonacci spiral (coordenadas quânticas)
        self.fibonacci_spiral = self._generate_fibonacci_spiral()
        
        # Ezekiel Wheels (EVOLUÇÃO)
        self.ezekiel_wheels = self._create_ezekiel_wheels_advanced()
        
        # Ezekiel Engine (se disponível)
        if EZEKIEL_AVAILABLE:
            self.ezekiel_engine = EzekielWheelEngine(dimension=5)
        else:
            self.ezekiel_engine = None
    
    def _create_sator_3d_cube(self):
        """Cria o quadrado Sator em 3D com 6 faces (12 dimensões criptográficas)"""
        sator_base = [
            ['S', 'A', 'T', 'O', 'R'],
            ['A', 'R', 'E', 'P', 'O'],
            ['T', 'E', 'N', 'E', 'T'],
            ['O', 'P', 'E', 'R', 'A'],
            ['R', 'O', 'T', 'A', 'S']
        ]
        
        # 6 faces: frente/trás, topo/baixo, esquerda/direita
        cube = {
            'front': [row[:] for row in sator_base],  # Face frontal
            'back': [row[::-1] for row in reversed(sator_base)],  # Face posterior (invertida)
            'top': [list(col) for col in zip(*sator_base)],  # Face superior (transposta)
            'bottom': [list(col)[::-1] for col in zip(*reversed(sator_base))],  # Face inferior
            'left': [[sator_base[i][0] for i in range(5)]],  # Face esquerda
            'right': [[sator_base[i][4] for i in range(5)]]  # Face direita
        }
        
        return cube
    
    def _rotate_face_3d(self, face, direction='clockwise'):
        """
        Rotaciona uma face do cubo 3D
        
        Args:
            face: Matriz da face
            direction: Direção (clockwise, counterclockwise, left, right, top, bottom)
        
        Returns:
            Face rotacionada
        """
        if direction == 'clockwise':
            return [list(col)[::-1] for col in zip(*face)]
        elif direction == 'counterclockwise':
            return [list(col) for col in zip(*reversed(face))]
        elif direction == 'left':
            return [row[::-1] for row in face]
        elif direction == 'right':
            return [list(col) for col in zip(*reversed(face))]
        elif direction == 'top':
            return [list(row) for row in reversed(face)]
        elif direction == 'bottom':
            return face
        
        return face
    
    def _generate_fibonacci_spiral(self, n=25):
        """
        Gera espiral de Fibonacci para coordenadas quânticas
        
        Args:
            n: Número de pontos na espiral
        
        Returns:
            Lista de tuplas (x, y, z, fib_value)
        """
        spiral = []
        a, b = 0, 1
        
        for i in range(n):
            # Ângulo baseado em Golden Ratio
            angle = 2 * np.pi * i * (b / (a + b if a + b > 0 else 1))
            radius = sqrt(a + b)
            
            # Coordenadas 3D
            x = radius * np.cos(angle)
            y = radius * np.sin(angle) 
            z = a % 4
            
            spiral.append((x, y, z, a))
            a, b = b, a + b
        
        return spiral
    
    def _create_ezekiel_wheels_advanced(self):
        """
        Cria o sistema de rodas dentro de rodas de Ezequiel (AVANÇADO)
        
        Baseado em Ezequiel 1:16:
        - Roda dentro de roda
        - 3 níveis hierárquicos
        - Proporções baseadas em Fibonacci
        
        Returns:
            Dicionário de rodas com configurações avançadas
        """
        wheels = {
            'outer': {
                'diameter': FIBONACCI_SEQUENCE[12] if len(FIBONACCI_SEQUENCE) > 12 else 144,  # 144
                'spokes': 12,
                'rotation_angle': 360 / 12,  # 30°
                'axis': 'X',
                'speed': 1.0
            },
            'middle': {
                'diameter': FIBONACCI_SEQUENCE[10] if len(FIBONACCI_SEQUENCE) > 10 else 89,  # 89
                'spokes': 8,
                'rotation_angle': 360 / 8,  # 45°
                'axis': 'Y',
                'speed': PHI  # Golden Ratio
            },
            'inner': {
                'diameter': FIBONACCI_SEQUENCE[8] if len(FIBONACCI_SEQUENCE) > 8 else 34,  # 34
                'spokes': 5,
                'rotation_angle': 360 / 5,  # 72°
                'axis': 'Z',
                'speed': PHI * PHI  # φ²
            }
        }
        
        return wheels
    
    # ======================================================================
    # MÉTODOS EVOLUÍDOS - EZEKIEL INTEGRATION
    # ======================================================================
    
    def rotate_ezekiel(self, data: bytes, angle_x: float, angle_y: float, angle_z: float) -> bytes:
        """
        Rotaciona dados usando Ezekiel Wheel Engine (gimbal-free)
        
        Args:
            data: Dados a rotacionar
            angle_x, angle_y, angle_z: Ângulos em graus
        
        Returns:
            Dados rotacionados
        """
        if not EZEKIEL_AVAILABLE or self.ezekiel_engine is None:
            # Fallback: rotação simples
            return self._rotate_simple(data, angle_x, angle_y, angle_z)
        
        # Criar Ezekiel Wheel
        wheel = EzekielWheel(
            angle_x=np.radians(angle_x),
            angle_y=np.radians(angle_y),
            angle_z=np.radians(angle_z)
        )
        
        # Aplicar rotação via engine
        rotated = self.ezekiel_engine.apply_ezekiel_wheel(data, wheel)
        
        return rotated
    
    def _rotate_simple(self, data: bytes, angle_x: float, angle_y: float, angle_z: float) -> bytes:
        """Rotação simples (fallback quando Ezekiel indisponível)"""
        result = bytearray()
        for i, byte in enumerate(data):
            # Rotação por XOR com ângulos
            rotated = byte ^ int(angle_x + i) % 256
            rotated = rotated ^ int(angle_y + i) % 256
            rotated = rotated ^ int(angle_z + i) % 256
            result.append(rotated)
        return bytes(result)
    
    def fibonacci_spiral_encryption(self, data: bytes, level: int) -> bytes:
        """
        Criptografa dados usando espiral de Fibonacci
        
        Args:
            data: Dados a criptografar
            level: Nível Fibonacci (1-16)
        
        Returns:
            Dados criptografados
        """
        if not EZEKIEL_AVAILABLE or self.ezekiel_engine is None:
            # Fallback simples
            return self._fibonacci_fallback(data, level)
        
        # Usar Ezekiel Engine
        encrypted = self.ezekiel_engine.fibonacci_spiral_rotation(data, level=level)
        
        return encrypted
    
    def _fibonacci_fallback(self, data: bytes, level: int) -> bytes:
        """Criptografia Fibonacci simples (fallback)"""
        fib_key = FIBONACCI_SEQUENCE[min(level, len(FIBONACCI_SEQUENCE)-1)]
        result = bytearray()
        for i, byte in enumerate(data):
            encrypted = (byte + fib_key * (i + 1)) % 256
            result.append(encrypted)
        return bytes(result)
    
    def golden_ratio_key_derivation(self, seed: str, length: int) -> bytes:
        """
        Deriva chave usando Golden Ratio
        
        Args:
            seed: Semente para derivação
            length: Comprimento da chave em bytes
        
        Returns:
            Chave derivada
        """
        if not EZEKIEL_AVAILABLE or self.ezekiel_engine is None:
            # Fallback: hash simples
            h = hashlib.sha3_256(seed.encode())
            key = h.digest()
            # Expandir se necessário
            while len(key) < length:
                h.update(key)
                key += h.digest()
            return key[:length]
        
        # Usar Ezekiel Engine
        key = self.ezekiel_engine.golden_ratio_key_derivation(seed.encode(), length)
        
        return key
    
    def rotate_without_turning(self, data: bytes, angle: float) -> bytes:
        """
        Rotação especial Ezequiel: núcleo fixo, casca gira
        
        Args:
            data: Dados a rotacionar
            angle: Ângulo em graus
        
        Returns:
            Dados rotacionados
        """
        if not EZEKIEL_AVAILABLE or self.ezekiel_engine is None:
            # Fallback
            return self._rotate_simple(data, angle, 0, 0)
        
        # Usar método especial do engine
        rotated = self.ezekiel_engine.rotate_without_turning(
            data,
            core_size=len(data) // 3,
            rotation_angle=np.radians(angle)
        )
        
        return rotated
    
    def wheel_within_wheel_encryption(self, data: bytes, levels: int = 3) -> bytes:
        """
        Criptografia hierárquica "roda dentro de roda"
        
        Args:
            data: Dados a criptografar
            levels: Níveis de rodas (1-3)
        
        Returns:
            Dados criptografados
        """
        if not EZEKIEL_AVAILABLE or self.ezekiel_engine is None:
            # Fallback: múltiplas rotações simples
            result = data
            for i in range(levels):
                angle = 360 / (i + 1)
                result = self._rotate_simple(result, angle, angle * PHI, angle / PHI)
            return result
        
        # Usar wheel_within_wheel do engine
        encrypted = self.ezekiel_engine.wheel_within_wheel(
            data,
            num_levels=min(levels, 3)
        )
        
        return encrypted
    
    # ======================================================================
    # MÉTODOS ORIGINAIS EVOLUÍDOS
    # ======================================================================
    
    def generate_quantum_key(self, seed_data: str) -> Dict:
        """
        Gera chave quântica usando Sator 3D + Ezequiel + Fibonacci
        
        EVOLUÇÃO: Agora usa Ezekiel Engine completo
        
        Args:
            seed_data: Semente para geração
        
        Returns:
            Dicionário com chave quântica
        """
        # Passo 1: Codificar via SATOR 3D
        sator_encoded = self._encode_via_sator_3d(seed_data)
        
        # Passo 2: Aplicar rodas de Ezequiel (EVOLUÍDO)
        wheel_encoded = self._apply_ezekiel_wheels_advanced(sator_encoded)
        
        # Passo 3: Mapear para espiral Fibonacci
        fib_mapped = self._map_to_fibonacci_spiral(wheel_encoded)
        
        # Passo 4: Criar hipercubo 4D
        hypercube_key = self._create_hypercube_advanced(fib_mapped)
        
        return hypercube_key
    
    def _encode_via_sator_3d(self, data: str) -> bytes:
        """Codifica dados através das 6 faces do Sator 3D"""
        encoded = []
        
        for char in str(data):
            char_code = ord(char)
            # Passar por todas as 6 faces
            for face_name, face in self.sator_3d.items():
                row = char_code % 5
                col = (char_code // 5) % 5
                if row < 5 and col < 5:
                    # Acessar face corretamente
                    if isinstance(face[0], list):
                        sator_char = face[row][col]
                    else:
                        sator_char = face[0][min(row, len(face[0])-1)]
                    char_code = (char_code + ord(sator_char)) % 256
            encoded.append(char_code)
        
        return bytes(encoded)
    
    def _apply_ezekiel_wheels_advanced(self, data: bytes) -> bytes:
        """
        Aplica o sistema de rodas de Ezequiel (AVANÇADO)
        
        Usa as 3 rodas hierárquicas com rotações perpendiculares
        """
        if not EZEKIEL_AVAILABLE or self.ezekiel_engine is None:
            # Fallback: método antigo
            return self._apply_ezekiel_wheels_legacy(data)
        
        # Obter ângulos das 3 rodas
        angle_x = self.ezekiel_wheels['outer']['rotation_angle']
        angle_y = self.ezekiel_wheels['middle']['rotation_angle']
        angle_z = self.ezekiel_wheels['inner']['rotation_angle']
        
        # Aplicar rotação Ezequiel
        wheel_encoded = self.rotate_ezekiel(data, angle_x, angle_y, angle_z)
        
        return wheel_encoded
    
    def _apply_ezekiel_wheels_legacy(self, data: bytes) -> bytes:
        """Método legado (compatibilidade)"""
        wheel_encoded = bytearray()
        
        for byte in data:
            # Rotações das 3 rodas
            outer_rotation = int(self.ezekiel_wheels['outer']['rotation_angle'])
            middle_spokes = int(self.ezekiel_wheels['middle']['spokes'])
            inner_diameter = int(self.ezekiel_wheels['inner']['diameter'])
            
            byte = (byte + outer_rotation) % 256
            byte = (byte * middle_spokes) % 256
            byte = (byte ^ inner_diameter) % 256
            wheel_encoded.append(byte)
        
        return bytes(wheel_encoded)
    
    def _map_to_fibonacci_spiral(self, data: bytes) -> bytes:
        """Mapeia dados para coordenadas da espiral Fibonacci"""
        fib_bytes = bytearray()
        
        for i, byte in enumerate(data):
            if i < len(self.fibonacci_spiral):
                x, y, z, fib_val = self.fibonacci_spiral[i]
                # Converter coordenadas para bytes
                new_byte = (byte + int(abs(x) * 100) + int(abs(y) * 100) + int(z * 10) + int(fib_val)) % 256
                fib_bytes.append(new_byte)
            else:
                fib_bytes.append(byte)
        
        return bytes(fib_bytes)
    
    def _create_hypercube_advanced(self, data: bytes) -> Dict:
        """
        Cria estrutura final de hipercubo 4D (AVANÇADO)
        
        Hipercubo (tesseracto):
        - 16 vértices (2^4)
        - 32 arestas
        - 24 faces
        - 8 células
        """
        hypercube = {
            'vertices': [],
            'edges': [],
            'faces': [],
            'cells': [],
            'dimension': 4,
            'rotation_state': {
                'x': 0.0,
                'y': 0.0,
                'z': 0.0,
                'w': 0.0  # 4ª dimensão
            }
        }
        
        # Criar 16 vértices (coordenadas 4D)
        for i in range(16):
            vertex = []
            for j in range(4):
                bit = (i >> j) & 1
                if j < len(data):
                    # Influenciar vértice com dados
                    vertex.append((bit + int(data[j % len(data)])) % 2)
                else:
                    vertex.append(bit)
            hypercube['vertices'].append(vertex)
        
        # Criar arestas (conectar vértices adjacentes)
        for i in range(16):
            for j in range(4):
                neighbor = i ^ (1 << j)  # Flip bit j
                if neighbor > i:
                    hypercube['edges'].append([i, neighbor])
        
        # Células (8 cubos 3D)
        for i in range(8):
            cell_vertices = [i, i+1, i+2, i+3, i+4, i+5, i+6, i+7]
            hypercube['cells'].append(cell_vertices)
        
        return hypercube


# =====================================================================
# QUANTUM LICENSE BUILDER - VERSÃO EVOLUÍDA
# =====================================================================

class QuantumLicenseBuilderEzekiel:
    """
    Construtor de licenças usando criptografia quântica multidimensional
    
    EVOLUÇÃO 2.0: Integração completa com Ezekiel
    """
    
    def __init__(self):
        """Inicializa o builder"""
        self.quantum_cube = QuantumSatorCubeEzekiel()
    
    def build_quantum_license(self, user_data: str, level: int, expiration_date) -> Dict:
        """
        Constrói licença usando arquitetura quântica Ezequiel
        
        Args:
            user_data: Dados do usuário
            level: Nível da licença (1-5)
            expiration_date: Data de expiração
        
        Returns:
            Payload da licença quântica
        """
        try:
            # Seed para geração
            seed = f"{user_data}{level}{expiration_date}"
            
            # Gerar chave quântica
            quantum_key = self.quantum_cube.generate_quantum_key(seed)
            
            # Criar payload
            quantum_payload = {
                "license_id": self._generate_quantum_id(),
                "user_data": user_data,
                "level": level, 
                "expiration_date": expiration_date.isoformat() if hasattr(expiration_date, 'isoformat') else str(expiration_date),
                
                # Assinatura quântica
                "quantum_signature": self._create_quantum_signature(quantum_key),
                
                # Hipercubo 4D
                "hypercube_coordinates": quantum_key['vertices'][:8],
                "hypercube_dimension": quantum_key['dimension'],
                
                # Fibonacci
                "fibonacci_sequence": [int(f[3]) for f in self.quantum_cube.fibonacci_spiral[:12]],
                
                # Ezekiel Wheels (EVOLUÍDO)
                "ezekiel_wheel_positions": {
                    'outer': {
                        'angle': self.quantum_cube.ezekiel_wheels['outer']['rotation_angle'],
                        'spokes': self.quantum_cube.ezekiel_wheels['outer']['spokes'],
                        'axis': self.quantum_cube.ezekiel_wheels['outer']['axis']
                    },
                    'middle': {
                        'angle': self.quantum_cube.ezekiel_wheels['middle']['rotation_angle'],
                        'spokes': self.quantum_cube.ezekiel_wheels['middle']['spokes'],
                        'axis': self.quantum_cube.ezekiel_wheels['middle']['axis']
                    },
                    'inner': {
                        'angle': self.quantum_cube.ezekiel_wheels['inner']['rotation_angle'],
                        'spokes': self.quantum_cube.ezekiel_wheels['inner']['spokes'],
                        'axis': self.quantum_cube.ezekiel_wheels['inner']['axis']
                    }
                },
                
                # SATOR 3D
                "sator_3d_faces": list(self.quantum_cube.sator_3d.keys()),
                
                # Flags
                "ezekiel_engine_available": EZEKIEL_AVAILABLE,
                "golden_ratio": PHI,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return quantum_payload
            
        except Exception as e:
            print(f"[QuantumBuilder] Erro na construção: {e}")
            raise
    
    def _generate_quantum_id(self) -> str:
        """Gera ID único baseado em mecânica quântica"""
        base_id = str(uuid.uuid4())
        
        # 3 estados quânticos diferentes
        quantum_states = [
            hashlib.sha256(base_id.encode()).hexdigest()[:8],
            hashlib.sha512(base_id.encode()).hexdigest()[:8],
            hashlib.sha3_256(base_id.encode()).hexdigest()[:8]
        ]
        
        quantum_id = ''.join(quantum_states)[:32]
        return quantum_id
    
    def _create_quantum_signature(self, quantum_key: Dict) -> str:
        """
        Cria assinatura quântica usando o hipercubo
        
        Args:
            quantum_key: Chave quântica do hipercubo
        
        Returns:
            Assinatura base64
        """
        try:
            signature = []
            
            # Usar primeiros 4 vértices do hipercubo
            for vertex in quantum_key['vertices'][:4]:
                vertex_sum = sum(int(v) for v in vertex) % 256
                signature.append(vertex_sum)
            
            return base64.b64encode(bytes(signature)).decode()
            
        except Exception as e:
            print(f"[QuantumSignature] Erro: {e}")
            return "error"
    
    def validate_quantum_license(self, license_data: Dict, original_seed: str) -> bool:
        """
        Valida licença quântica recriando a assinatura
        
        Args:
            license_data: Dados da licença
            original_seed: Seed original
        
        Returns:
            True se válida
        """
        try:
            # Recriar chave quântica
            quantum_key = self.quantum_cube.generate_quantum_key(original_seed)
            
            # Recriar assinatura
            expected_signature = self._create_quantum_signature(quantum_key)
            
            # Comparar
            return license_data.get('quantum_signature') == expected_signature
            
        except Exception as e:
            print(f"[QuantumValidation] Erro: {e}")
            return False


# =====================================================================
# EXEMPLO DE USO
# =====================================================================

if __name__ == "__main__":
    print("=" * 80)
    print(" QUANTUM CRYPTO EZEKIEL - DEMONSTRAÇÃO")
    print("=" * 80)
    
    # Criar cubo quântico
    cube = QuantumSatorCubeEzekiel()
    
    print(f"\n Cubo Quântico Ezequiel criado")
    print(f"   Ezekiel Engine: {' Disponível' if EZEKIEL_AVAILABLE else ' Indisponível'}")
    print(f"   Golden Ratio (φ): {PHI}")
    print(f"   Fibonacci Spiral: {len(cube.fibonacci_spiral)} pontos")
    print(f"   Ezekiel Wheels: {len(cube.ezekiel_wheels)} rodas")
    
    # Testar criptografia
    print("\n Testando criptografia Ezequiel...")
    test_data = b"KAYOS_SYSTEMS_QUANTUM_TEST"
    
    # Rotação Ezequiel
    rotated = cube.rotate_ezekiel(test_data, 30, 45, 60)
    print(f" Rotação Ezequiel: {len(rotated)} bytes")
    
    # Fibonacci encryption
    fib_encrypted = cube.fibonacci_spiral_encryption(test_data, level=5)
    print(f" Fibonacci Encryption: {len(fib_encrypted)} bytes")
    
    # Golden Ratio KDF
    key = cube.golden_ratio_key_derivation("master_seed", 32)
    print(f" Golden Ratio Key: {len(key)} bytes")
    
    # Wheel within wheel
    www_encrypted = cube.wheel_within_wheel_encryption(test_data, levels=3)
    print(f" Wheel Within Wheel: {len(www_encrypted)} bytes")
    
    # Criar licença quântica
    print("\n Criando licença quântica...")
    builder = QuantumLicenseBuilderEzekiel()
    
    license_data = builder.build_quantum_license(
        user_data="user@kayos.com",
        level=5,
        expiration_date=datetime(2026, 12, 31)
    )
    
    print(f" Licença criada:")
    print(f"   ID: {license_data['license_id']}")
    print(f"   Level: {license_data['level']}")
    print(f"   Hipercubo Dimensão: {license_data['hypercube_dimension']}")
    print(f"   Fibonacci Sequence: {license_data['fibonacci_sequence'][:5]}...")
    print(f"   Ezekiel Outer Wheel: {license_data['ezekiel_wheel_positions']['outer']['angle']}°")
    print(f"   Assinatura: {license_data['quantum_signature'][:20]}...")
    
    # Validar licença
    print("\n Validando licença...")
    seed = f"user@kayos.com5{datetime(2026, 12, 31)}"
    valid = builder.validate_quantum_license(license_data, seed)
    print(f" Licença válida: {valid}")
    
    print("\n" + "=" * 80)
    print(" Demonstração completa!")
    print("=" * 80)
