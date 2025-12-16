"""
Sistema de Criptografia Quântica Multidimensional
Integrando Sator 3D, Rodas de Ezequiel e Fibonacci Espiral
"""

import numpy as np
from math import gcd, sqrt
import base64
import hashlib
import uuid
from datetime import date
import json

class QuantumSatorCube:
    """
    Hipercubo Sator 3D com 6 faces (verso/anverso) 
    integrando Rodas de Ezequiel e Fibonacci Espiral
    """
    
    def __init__(self):
        self.faces = 6
        self.sator_3d = self._create_sator_3d_cube()
        self.fibonacci_spiral = self._generate_fibonacci_spiral()
        self.ezekiel_wheels = self._create_ezekiel_wheels()
        
    def _create_sator_3d_cube(self):
        """Cria o quadrado Sator em 3D com 6 faces"""
        sator_2d = [
            ['S', 'A', 'T', 'O', 'R'],
            ['A', 'R', 'E', 'P', 'O'], 
            ['T', 'E', 'N', 'E', 'T'],
            ['O', 'P', 'E', 'R', 'A'],
            ['R', 'O', 'T', 'A', 'S']
        ]
        
        cube = {}
        cube['front'] = sator_2d
        cube['back'] = [list(reversed(row)) for row in reversed(sator_2d)]
        cube['left'] = self._rotate_face_3d(sator_2d, 'left')
        cube['right'] = self._rotate_face_3d(sator_2d, 'right') 
        cube['top'] = self._rotate_face_3d(sator_2d, 'top')
        cube['bottom'] = self._rotate_face_3d(sator_2d, 'bottom')
        
        return cube
    
    def _rotate_face_3d(self, face, direction):
        """Roda a face do cubo na direção especificada"""
        if direction == 'left':
            return [list(reversed(col)) for col in zip(*face)]
        elif direction == 'right':
            return [list(col) for col in zip(*reversed(face))]
        elif direction == 'top':
            return [list(row) for row in reversed(face)]
        elif direction == 'bottom':
            return face
            
        return face

    def _generate_fibonacci_spiral(self, n=25):
        """Gera espiral de Fibonacci para coordenadas quânticas"""
        spiral = []
        a, b = 0, 1
        
        for i in range(n):
            angle = 2 * np.pi * i * (b / (a + b if a + b > 0 else 1))
            radius = sqrt(a + b)
            x = radius * np.cos(angle)
            y = radius * np.sin(angle) 
            z = a % 4
            spiral.append((x, y, z, a))
            a, b = b, a + b
            
        return spiral

    def _create_ezekiel_wheels(self):
        """Cria o sistema de rodas dentro de rodas de Ezequiel"""
        wheels = {}
        wheels['outer'] = {'diameter': 144, 'spokes': 12, 'rotation': int(360/12)}
        wheels['inner'] = {'diameter': 108, 'spokes': 7, 'rotation': int(360/7)}
        wheels['middle'] = {'diameter': 72, 'spokes': 5, 'rotation': int(360/5)}
        return wheels

    def generate_quantum_key(self, seed_data):
        """Gera chave quântica usando Sator 3D + Ezequiel + Fibonacci"""
        sator_encoded = self._encode_via_sator_3d(seed_data)
        wheel_encoded = self._apply_ezekiel_wheels(sator_encoded)
        fib_mapped = self._map_to_fibonacci_spiral(wheel_encoded)
        hypercube_key = self._create_hypercube(fib_mapped)
        return hypercube_key

    def _encode_via_sator_3d(self, data):
        """Codifica dados através das 6 faces do Sator 3D"""
        encoded = []
        
        for char in str(data):
            char_code = ord(char)
            for face_name, face in self.sator_3d.items():
                row = char_code % 5
                col = (char_code // 5) % 5
                if row < 5 and col < 5:
                    sator_char = face[row][col]
                    char_code = (char_code + ord(sator_char)) % 256
            encoded.append(char_code)
            
        return bytes(encoded)

    def _apply_ezekiel_wheels(self, data):
        """Aplica o sistema de rodas de Ezequiel"""
        wheel_encoded = bytearray()
        
        for byte in data:
            # CORREÇÃO: Converter valores para int antes do XOR
            outer_rotation = int(self.ezekiel_wheels['outer']['rotation'])
            inner_spokes = int(self.ezekiel_wheels['inner']['spokes'])
            middle_diameter = int(self.ezekiel_wheels['middle']['diameter'])
            
            byte = (byte + outer_rotation) % 256
            byte = (byte * inner_spokes) % 256
            byte = (byte ^ middle_diameter) % 256  # Agora ambos são int
            wheel_encoded.append(byte)
            
        return bytes(wheel_encoded)

    def _map_to_fibonacci_spiral(self, data):
        """Mapeia dados para coordenadas da espiral Fibonacci"""
        fib_bytes = bytearray()
        
        for i, byte in enumerate(data):
            if i < len(self.fibonacci_spiral):
                x, y, z, fib_val = self.fibonacci_spiral[i]
                # CORREÇÃO: Converter floats para int
                new_byte = (byte + int(abs(x) * 100) + int(abs(y) * 100) + int(z * 10) + int(fib_val)) % 256
                fib_bytes.append(new_byte)
            else:
                fib_bytes.append(byte)
                
        return bytes(fib_bytes)

    def _create_hypercube(self, data):
        """Cria estrutura final de hipercubo 4D"""
        hypercube = {'vertices': [], 'edges': [], 'faces': [], 'cells': []}
        
        for i in range(16):
            vertex = []
            for j in range(4):
                bit = (i >> j) & 1
                vertex.append(bit)
                if j < len(data):
                    # CORREÇÃO: Garantir que são int para operação bit a bit
                    vertex[-1] = (vertex[-1] + int(data[j % len(data)])) % 2
            hypercube['vertices'].append(vertex)
            
        return hypercube

class QuantumLicenseBuilder:
    """Construtor de licenças usando criptografia quântica multidimensional"""
    
    def __init__(self):
        self.quantum_cube = QuantumSatorCube()
        
    def build_quantum_license(self, user_data, level, expiration_date):
        """Constrói licença usando arquitetura quântica"""
        try:
            seed = f"{user_data}{level}{expiration_date}"
            quantum_key = self.quantum_cube.generate_quantum_key(seed)
            
            quantum_payload = {
                "license_id": self._generate_quantum_id(),
                "user_data": user_data,
                "level": level, 
                "expiration_date": expiration_date.isoformat() if hasattr(expiration_date, 'isoformat') else expiration_date,
                "quantum_signature": self._create_quantum_signature(quantum_key),
                "hypercube_coordinates": quantum_key['vertices'][:8],
                "fibonacci_sequence": [int(f[3]) for f in self.quantum_cube.fibonacci_spiral[:12]],  # CORREÇÃO: converter para int
                "ezekiel_wheel_positions": {
                    'outer': int(self.quantum_cube.ezekiel_wheels['outer']['rotation']),
                    'inner': int(self.quantum_cube.ezekiel_wheels['inner']['rotation']), 
                    'middle': int(self.quantum_cube.ezekiel_wheels['middle']['rotation'])
                },
                "sator_3d_faces": list(self.quantum_cube.sator_3d.keys())
            }
            
            return quantum_payload
            
        except Exception as e:
            print(f"[QuantumBuilder] Erro na construção: {e}")
            raise

    def _generate_quantum_id(self):
        """Gera ID único baseado em mecânica quântica"""
        base_id = str(uuid.uuid4())
        quantum_states = [
            hashlib.sha256(base_id.encode()).hexdigest()[:8],
            hashlib.sha512(base_id.encode()).hexdigest()[:8],
            hashlib.sha3_512(base_id.encode()).hexdigest()[:8]
        ]
        quantum_id = ''.join(quantum_states)[:32]
        return quantum_id

    def _create_quantum_signature(self, quantum_key):
        """Cria assinatura quântica usando o hipercubo"""
        try:
            signature = []
            for vertex in quantum_key['vertices'][:4]:
                vertex_sum = sum(int(v) for v in vertex) % 256  # CORREÇÃO: converter para int
                signature.append(vertex_sum)
            return base64.b64encode(bytes(signature)).decode()
        except Exception as e:
            print(f"[QuantumSignature] Erro: {e}")
            return "error"

    def validate_quantum_license(self, license_data, original_seed):
        """Valida licença quântica recriando a assinatura"""
        try:
            quantum_key = self.quantum_cube.generate_quantum_key(original_seed)
            expected_signature = self._create_quantum_signature(quantum_key)
            
            return license_data.get('quantum_signature') == expected_signature
        except Exception as e:
            print(f"[QuantumValidation] Erro: {e}")
            return False
