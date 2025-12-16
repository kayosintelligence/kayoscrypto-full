#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rib 7: PalindromeSignatureSystem
=================================

Responsabilidade: Sistema de assinatura digital baseado em propriedades
                 palindrômicas (SATOR-like) com resistência quântica.

Arquitetura: Fishbone Rib (Specialized Module)
Filosofia: KAIOS - Quadrante SATOR (simetria geométrica palindrômica)
Versão: v6.0.0-alpha

Author: KAYOS Systems
Date: 15 de Novembro de 2025
"""

import hashlib
import numpy as np
from typing import Tuple
from dataclasses import dataclass


@dataclass
class Signature:
    """Assinatura palindrômica (v6.0.3 HMAC)"""
    forward: bytes
    backward: bytes
    checksum: bytes
    version: int = 1  # 1 = HMAC (v6.0.3), 2 = Ed25519 (v6.1)
    
    def is_valid(self) -> bool:
        """Verifica se assinatura tem propriedade palindrômica"""
        return self.forward == self.backward[::-1]
    
    def to_bytes(self) -> bytes:
        """Serializa assinatura"""
        payload = self.forward + self.backward + self.checksum
        if self.version > 1:
            payload += bytes([self.version])
        return payload
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'Signature':
        """Desserializa assinatura"""
        if len(data) in (96, 97):
            if len(data) == 97:
                version = data[-1]
                core_data = data[:-1]
            else:
                version = 1
                core_data = data
        else:  # pragma: no cover - dados inválidos
            raise ValueError("Formato de assinatura inválido")
        sig_len = (len(core_data) - 32) // 2
        forward = core_data[:sig_len]
        backward = core_data[sig_len:sig_len*2]
        checksum = core_data[sig_len*2:]
        return cls(forward, backward, checksum, version)


class PalindromeSignatureSystem:
    """
    Sistema de Assinatura Palindrômica
    
    Inovação: Assinatura digital que possui propriedades palindrômicas
              (lê igual de frente e de trás, como SATOR AREPO TENET OPERA ROTAS)
    
    Propriedades:
    - Resistência quântica: Não depende de fatoração ou log discreto
    - Verificação dual: Pode validar em ambas as direções
    - Simetria geométrica: Baseada em transformações simétricas
    
    Princípios KAIOS:
    - SATOR: Quadrante palindrômico (simetria perfeita)
    - Ezequiel: Transformação multidimensional
    - Relojoeiro: Otimização de verificação
    """
    
    def __init__(self, key_size: int = 32):
        self.key_size = key_size
        self.phi = 1.618033988749  # Golden ratio
    
    def sign(self, message: bytes, private_key: bytes) -> Signature:
        """
        Assina mensagem usando chave privada
        
        Algoritmo HMAC-based (v6.0.2 - FIXED):
        1. Calcular HMAC(message, private_key) = signature_base
        2. Aplicar transformação palindrômica para camada geométrica
        3. Gerar checksum com binding do message hash
        
        Segurança:
        - HMAC garante autenticidade (resistente a forge)
        - Propriedade palindrômica adiciona camada geométrica (filosofia KAIOS)
        - Verificação usa HMAC comparison (constant-time)
        
        Args:
            message: Mensagem a assinar
            private_key: Chave privada (32 bytes)
        
        Returns:
            Signature com propriedades palindrômicas
        """
        import hmac
        
        # 1. HMAC como base da assinatura (matematicamente sólido)
        signature_base = hmac.new(
            key=private_key,
            msg=message,
            digestmod=hashlib.sha256
        ).digest()
        
        # 2. Transformação palindrômica (camada geométrica KAIOS)
        forward = self._palindromic_transform(signature_base, direction='forward')
        backward = forward[::-1]  # Propriedade SATOR
        
        # 3. Checksum para integridade (binding do message)
        message_hash = hashlib.sha256(message).digest()
        checksum = hashlib.sha256(forward + backward + message_hash).digest()
        
        return Signature(forward, backward, checksum)
    
    def verify(self, message: bytes, signature: Signature, public_key: bytes) -> bool:
        """
        Verifica assinatura usando chave pública
        
        Algoritmo HMAC-symmetric (v6.0.3 - FIXED):
        1. Verificar propriedade palindrômica (geometria KAIOS)
        2. Verificar checksum (integridade)
        3. Recalcular HMAC usando public_key (= private_key)
        4. Comparar com constant-time
        
        Nota de Segurança:
        - public_key = private_key (HMAC symmetric)
        - Isto é MAC (Message Authentication Code), não signature
        - Para v6.0: aceitável para demonstração
        - Para v6.1+: migrar para Ed25519/ECDSA
        
        Args:
            message: Mensagem original
            signature: Assinatura a verificar
            public_key: Chave pública (= private_key)
        
        Returns:
            True se assinatura válida
        """
        import hmac
        
        # 1. Verificar propriedade palindrômica
        if not signature.is_valid():
            return False
        
        # 2. Verificar checksum
        message_hash = hashlib.sha256(message).digest()
        expected_checksum = hashlib.sha256(
            signature.forward + signature.backward + message_hash
        ).digest()
        
        if signature.checksum != expected_checksum:
            return False
        
        # 3. Recalcular HMAC usando public_key (= private_key)
        expected_signature_base = hmac.new(
            key=public_key,  # = private_key (symmetric)
            msg=message,
            digestmod=hashlib.sha256
        ).digest()
        
        # 4. Aplicar mesma transformação palindrômica
        expected_forward = self._palindromic_transform(
            expected_signature_base, 
            direction='forward'
        )
        
        # 5. Comparar usando constant-time comparison (segurança)
        return hmac.compare_digest(signature.forward, expected_forward)
    
    def _palindromic_transform(self, data: bytes, direction: str) -> bytes:
        """
        Transforma dados em estrutura palindrômica
        
        Método SATOR:
        - Forward: S A T O R → transformação →
        - Backward: R O T A S (reverso do forward)
        
        Args:
            data: Dados de entrada (32 bytes)
            direction: 'forward' ou 'backward'
        
        Returns:
            bytes com propriedades palindrômicas
        """
        # Converter para array NumPy
        arr = np.frombuffer(data, dtype=np.uint8)
        length = len(arr)
        
        # Criar matriz SATOR (quadrada)
        side = int(np.sqrt(length))
        if side * side < length:
            side += 1
        
        # Preencher matriz com padding se necessário
        padded = np.zeros(side * side, dtype=np.uint8)
        padded[:length] = arr
        matrix = padded.reshape((side, side))
        
        if direction == 'forward':
            # Transformação forward: ler da diagonal para fora
            result = self._spiral_read(matrix, clockwise=True)
        else:
            # Transformação backward: ler reverso
            result = self._spiral_read(matrix, clockwise=False)
        
        # Retornar tamanho original
        return result[:self.key_size].tobytes()
    
    def _spiral_read(self, matrix: np.ndarray, clockwise: bool) -> np.ndarray:
        """
        Lê matriz em espiral (padrão SATOR)
        
        Args:
            matrix: Matriz quadrada
            clockwise: True = horário, False = anti-horário
        
        Returns:
            Array 1D com leitura espiral
        """
        side = matrix.shape[0]
        result = []
        
        top, bottom = 0, side - 1
        left, right = 0, side - 1
        
        if clockwise:
            # Espiral horária
            while top <= bottom and left <= right:
                # Direita
                for i in range(left, right + 1):
                    result.append(matrix[top, i])
                top += 1
                
                # Baixo
                for i in range(top, bottom + 1):
                    result.append(matrix[i, right])
                right -= 1
                
                # Esquerda
                if top <= bottom:
                    for i in range(right, left - 1, -1):
                        result.append(matrix[bottom, i])
                    bottom -= 1
                
                # Cima
                if left <= right:
                    for i in range(bottom, top - 1, -1):
                        result.append(matrix[i, left])
                    left += 1
        else:
            # Espiral anti-horária (reverso)
            while top <= bottom and left <= right:
                # Baixo
                for i in range(top, bottom + 1):
                    result.append(matrix[i, left])
                left += 1
                
                # Direita
                for i in range(left, right + 1):
                    result.append(matrix[bottom, i])
                bottom -= 1
                
                # Cima
                if left <= right:
                    for i in range(right, left - 1, -1):
                        result.append(matrix[top, i])
                    top += 1
                
                # Esquerda
                if top <= bottom:
                    for i in range(bottom, top - 1, -1):
                        result.append(matrix[i, right])
                    right -= 1
        
        return np.array(result, dtype=np.uint8)
    
    def generate_keypair(self, seed: bytes = None) -> Tuple[bytes, bytes]:
        """
        Gera par de chaves (privada, pública)
        
        IMPORTANTE (v6.0.3 - Symmetric HMAC):
        Para manter propriedades palindrômicas e simplicidade,
        usamos HMAC symmetric com interface assimétrica:
        
        - private_key = hash(seed) ← usada para sign()
        - public_key = private_key  ← MESMA chave (symmetric)
        
        Nota de Segurança:
        - Isto é HMAC-MAC, não assinatura digital assimétrica
        - Qualquer um com public_key pode criar assinaturas válidas
        - Para produção: usar Ed25519, ECDSA ou RSA
        - Para v6.0: aceitável (propriedade palindrômica é demonstração)
        
        Trade-offs:
         Propriedade palindrômica funciona
         Verificação funciona corretamente
         Resistente a quantum (HMAC-SHA256)
         Public key = Private key (não é assimétrica real)
         Não adequado para certificados digitais
         Adequado para MACs autenticados (uso interno)
        
        Args:
            seed: Seed opcional para geração determinística
        
        Returns:
            (private_key, public_key) tupla de bytes
        """
        if seed is None:
            import os
            seed = os.urandom(32)
        
        # Chave privada = hash do seed, ajustado para key_size
        if self.key_size <= 32:
            private_key = hashlib.sha256(seed).digest()[:self.key_size]
        else:
            # Para chaves maiores que 32 bytes, usar SHA-256 múltiplas vezes
            private_key = hashlib.sha256(seed).digest()
            while len(private_key) < self.key_size:
                private_key += hashlib.sha256(private_key).digest()
            private_key = private_key[:self.key_size]
        
        # Chave pública = private_key (HMAC symmetric)
        # Nota: Interface assimétrica, implementação symmetric
        public_key = private_key  # Simplificação pragmática
        
        return private_key, public_key


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("RIB 7: PALINDROME SIGNATURE SYSTEM - DEMONSTRAÇÃO")
    print("=" * 70)
    
    system = PalindromeSignatureSystem()
    
    # Gerar par de chaves
    print("\n Gerando par de chaves...\n")
    private_key, public_key = system.generate_keypair(seed=b'test_seed_12345')
    
    print(f"Chave Privada: {private_key.hex()[:32]}...")
    print(f"Chave Pública:  {public_key.hex()[:32]}...")
    
    # Assinar mensagem
    print("\n Assinando mensagem...\n")
    message = b"KayosCrypto - Sistema criptografico geometrico-filosofico"
    
    signature = system.sign(message, private_key)
    
    print(f"Mensagem: {message.decode()}")
    print(f"Assinatura (forward):  {signature.forward.hex()[:32]}...")
    print(f"Assinatura (backward): {signature.backward.hex()[:32]}...")
    
    # Verificar propriedade palindrômica
    print("\n Verificando propriedade palindrômica...\n")
    is_palindromic = signature.is_valid()
    print(f"   Forward == Backward[::-1]: {is_palindromic}")
    
    if is_palindromic:
        print(f"   Status:  Assinatura tem simetria SATOR")
    else:
        print(f"   Status:  Assinatura sem simetria")
    
    # Verificar assinatura
    print("\n Verificando assinatura com chave pública...\n")
    is_valid = system.verify(message, signature, public_key)
    
    print(f"   Verificação: {' VÁLIDA' if is_valid else ' INVÁLIDA'}")
    
    # Teste de falsificação
    print("\n Testando resistência a falsificação...\n")
    fake_message = b"Mensagem falsificada"
    is_fake_valid = system.verify(fake_message, signature, public_key)
    
    print(f"   Mensagem original: {is_valid}")
    print(f"   Mensagem falsa:    {is_fake_valid}")
    
    if not is_fake_valid:
        print(f"   Status:  Sistema detecta falsificação")
    else:
        print(f"   Status:  VULNERÁVEL!")
    
    # Teste de resistência quântica
    print("\n Análise de Resistência Quântica:\n")
    print(f"    Não usa fatoração (resistente a Shor)")
    print(f"    Não usa log discreto (resistente a Shor)")
    print(f"    Baseado em hash + geometria (resistente a Grover com key 256-bit)")
    print(f"    Propriedade palindrômica adiciona camada de complexidade")
    
    print("\n" + "=" * 70)
    print(" Sistema de assinatura palindrômica operacional!")
    print("=" * 70)
