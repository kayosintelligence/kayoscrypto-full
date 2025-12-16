#!/usr/bin/env python3
"""
 EZEKIEL CONCENTRIC WHEELS - Extensão Avançada
==================================================

"Roda dentro de roda" - Implementação real do conceito de Ezequiel
como extensão SEGURA do KayosCrypto existente.

Características:
 Rodas concêntricas independentes mas conectadas
 Cada roda com movimento Fibonacci único
 100% reversível por design
 Compatível com sistema atual
"""

import numpy as np
import hashlib
from typing import List

class EzekielConcentricEngine:
    """
     Motor de Rodas Concêntricas de Ezequiel
    
    Filosofia:
    - Roda Principal: Direção Fibonacci primária
    - Sub-Roda Alpha: Contra-rotação áurea  
    - Sub-Roda Beta: Espiral complementar
    
    Cada roda opera independentemente mas em ressonância,
    criando padrões complexos mantendo reversibilidade.
    """
    
    def __init__(self):
        self.golden_ratio = 1.618033988749895
        self.fibonacci_seq = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
        
    def apply_concentric_rotation(self, data: bytes, base_angle: float, 
                                reverse: bool = False) -> bytes:
        """
        Aplica giro concentrico de 3 rodas com mixing layer.
        
        Args:
            data: Dados a transformar
            base_angle: Angulo base para sincronizacao
            reverse: Se True, aplica rotacao inversa
            
        Returns:
            Dados transformados pelas rodas concentricas
        """
        if len(data) < 2:
            return data

        result = np.frombuffer(data, dtype=np.uint8).copy()
        
        if not reverse:
            # Forward direction
            # ════════════════════════════════════════════════════
            # MIXING LAYER INICIAL - Propaga mudancas entre bytes
            # ════════════════════════════════════════════════════
            result = self._mixing_layer(result, int(base_angle * 1000) % 256, False)

            # ════════════════════════════════════════════════════
            # RODA PRINCIPAL - Fibonacci Direto
            # ════════════════════════════════════════════════════
            main_shift = self._calculate_fibonacci_shift(result.size, base_angle)
            result = self._apply_wheel_rotation(result, main_shift, 0, False)

            # ════════════════════════════════════════════════════
            # SUB-RODA ALPHA - Contra-rotacao Aurea
            # ════════════════════════════════════════════════════
            alpha_angle = -base_angle * self.golden_ratio
            alpha_shift = self._calculate_golden_shift(result.size, alpha_angle)
            result = self._apply_wheel_rotation(result, alpha_shift, 1, False)

            # ════════════════════════════════════════════════════
            # SUB-RODA BETA - Espiral Complementar  
            # ════════════════════════════════════════════════════
            beta_angle = base_angle * 2.0 + np.pi/4  # 45 offset
            beta_shift = self._calculate_spiral_shift(result.size, beta_angle)
            result = self._apply_wheel_rotation(result, beta_shift, 2, False)
            
            # ════════════════════════════════════════════════════
            # MIXING LAYER FINAL - Segunda propagacao
            # ════════════════════════════════════════════════════
            result = self._mixing_layer(result, int(base_angle * 1000) % 256, False)
        else:
            # Reverse direction - ordem inversa
            # Mixing layer final primeiro (reverso)
            result = self._mixing_layer(result, int(base_angle * 1000) % 256, True)
            
            # Rodas em ordem inversa
            beta_angle = base_angle * 2.0 + np.pi/4
            beta_shift = self._calculate_spiral_shift(result.size, beta_angle)
            result = self._apply_wheel_rotation(result, beta_shift, 2, True)
            
            alpha_angle = -base_angle * self.golden_ratio
            alpha_shift = self._calculate_golden_shift(result.size, alpha_angle)
            result = self._apply_wheel_rotation(result, alpha_shift, 1, True)
            
            main_shift = self._calculate_fibonacci_shift(result.size, base_angle)
            result = self._apply_wheel_rotation(result, main_shift, 0, True)
            
            # Mixing layer inicial (reverso)
            result = self._mixing_layer(result, int(base_angle * 1000) % 256, True)

        return result.tobytes()
    
    def _mixing_layer(self, data: np.ndarray, seed: int, reverse: bool) -> np.ndarray:
        """
        Mixing layer para propagar mudancas entre bytes adjacentes.
        
        Usa Feistel-like structure que e perfeitamente reversivel.
        """
        if len(data) < 4:
            return data
        
        result = data.copy().astype(np.int32)  # Usar int32 para evitar overflow
        n = len(result)
        
        # Determinar numero de rounds baseado em Fibonacci
        rounds = 3  # Numero fixo de rounds
        
        if not reverse:
            # Forward mixing
            for r in range(rounds):
                for i in range(n):
                    # Feistel-like: XOR com funcao do vizinho
                    neighbor = (i + self.fibonacci_seq[r % len(self.fibonacci_seq)]) % n
                    # Funcao F simples: rotacao + XOR com seed
                    f_val = ((result[neighbor] << (r + 1)) | (result[neighbor] >> (8 - r - 1))) & 0xFF
                    f_val = (f_val + seed + r) & 0xFF
                    result[i] = (result[i] ^ f_val) & 0xFF
        else:
            # Reverse mixing - ordem inversa dos rounds
            for r in range(rounds - 1, -1, -1):
                for i in range(n - 1, -1, -1):  # Tambem inverte direcao do loop
                    neighbor = (i + self.fibonacci_seq[r % len(self.fibonacci_seq)]) % n
                    f_val = ((result[neighbor] << (r + 1)) | (result[neighbor] >> (8 - r - 1))) & 0xFF
                    f_val = (f_val + seed + r) & 0xFF
                    result[i] = (result[i] ^ f_val) & 0xFF
        
        return result.astype(np.uint8)
    
    def _calculate_fibonacci_shift(self, size: int, angle: float) -> int:
        """Calcula deslocamento baseado em sequência Fibonacci.
        
        GROVER OPTIMIZATION: Aumentar intensidade para melhorar avalanche.
        """
        fib_index = int(abs(angle * 100)) % len(self.fibonacci_seq)
        shift = self.fibonacci_seq[fib_index] * 4  # Aumentado de 3 para 4
        return shift % size if size > 0 else 0
    
    def _calculate_golden_shift(self, size: int, angle: float) -> int:
        """Calcula deslocamento baseado em razão áurea.
        
        GROVER OPTIMIZATION: Aumentar intensidade para melhorar avalanche.
        """
        golden_effect = int(abs(angle * self.golden_ratio * 1000)) % size
        return (golden_effect * 3) % size if size > 0 else 0  # Aumentado de 2 para 3
    
    def _calculate_spiral_shift(self, size: int, angle: float) -> int:
        """Calcula deslocamento em espiral complementar.
        
        GROVER OPTIMIZATION: Aumentar intensidade para melhorar avalanche.
        """
        spiral = (np.sin(angle) * 500 + np.cos(angle * 2) * 300) * 2.0  # Aumentado de 1.5 para 2.0
        return int(abs(spiral)) % size if size > 0 else 0
    
    def _apply_wheel_rotation(self, data: bytearray, shift: int, 
                            wheel_level: int, reverse: bool) -> bytearray:
        """
        Aplica rotacao de roda individual com difusao adicional.
        
        Cada roda tem caracteristica unica baseada em seu nivel.
        Usa rotacoes de bits alem de rotacao de array para melhorar avalanche.
        """
        if len(data) == 0:
            return data

        effective_shift = (-shift if reverse else shift) % len(data)
        
        if not reverse:
            # Forward: bit rotation, then array roll
            data = self._bit_diffusion(data, wheel_level, shift)
            if effective_shift != 0:
                data = np.roll(data, effective_shift)
        else:
            # Reverse: array roll first, then reverse bit rotation
            if effective_shift != 0:
                data = np.roll(data, effective_shift)
            data = self._bit_diffusion_reverse(data, wheel_level, shift)
        
        return data
    
    def _bit_diffusion(self, data: np.ndarray, wheel_level: int, shift: int) -> np.ndarray:
        """
        Aplica rotacao de bits para melhorar difusao (avalanche effect).
        
        Rotacao circular de bits e perfeitamente reversivel.
        """
        if len(data) < 2:
            return data
        
        result = data.copy()
        
        # Quantidade de rotacao baseada em wheel_level e Fibonacci
        fib_idx = (wheel_level + 1) % len(self.fibonacci_seq)
        rotation_amount = self.fibonacci_seq[fib_idx] % 8  # 0-7 bits
        
        if rotation_amount == 0:
            rotation_amount = 1  # Garantir pelo menos 1 bit de rotacao
        
        # Rotacao circular de bits para esquerda (cada byte)
        result = ((result << rotation_amount) | (result >> (8 - rotation_amount))) & 0xFF
        
        return result.astype(np.uint8)
    
    def _bit_diffusion_reverse(self, data: np.ndarray, wheel_level: int, shift: int) -> np.ndarray:
        """
        Reverte a rotacao de bits.
        """
        if len(data) < 2:
            return data
        
        result = data.copy()
        
        # Mesma quantidade de rotacao
        fib_idx = (wheel_level + 1) % len(self.fibonacci_seq)
        rotation_amount = self.fibonacci_seq[fib_idx] % 8
        
        if rotation_amount == 0:
            rotation_amount = 1
        
        # Rotacao circular de bits para direita (reverso)
        result = ((result >> rotation_amount) | (result << (8 - rotation_amount))) & 0xFF
        
        return result.astype(np.uint8)


class KayosCryptoEvolved:
    """
     KAYOSCRYPTO EVOLVED - Com Rodas Concêntricas
    
    Extensão do KayosCryptoFinal com as novas rodas de Ezequiel.
    Mantém compatibilidade total com versão anterior.
    """
    
    def __init__(self, use_concentric: bool = True):
        from .kayoscrypto_final import KayosCryptoFinal
        
        self.core = KayosCryptoFinal()
        self.use_concentric = use_concentric
        
        if use_concentric:
            self.ezekiel_advanced = EzekielConcentricEngine()
    
    def encrypt(self, plaintext: bytes, password: str, level: int = 3) -> bytes:
        """
         Encrypt evoluído com rodas concêntricas.
        
        Se use_concentric=True, aplica rodas avançadas de Ezequiel
        antes do processamento normal (como camada extra).
        """
        data = plaintext
        
        # ════════════════════════════════════════════════════
        # CAMADA EXTRA: Rodas Concêntricas (se ativado)
        # ════════════════════════════════════════════════════
        if self.use_concentric:
            key = self.core._derive_key(password, len(data))
            base_angle = self._key_to_angle(key)
            
            # Aplicar rodas concêntricas como pré-processamento
            data = self.ezekiel_advanced.apply_concentric_rotation(
                data, base_angle, reverse=False
            )
        
        # ════════════════════════════════════════════════════
        # PROCESSAMENTO NORMAL (sistema existente)
        # ════════════════════════════════════════════════════
        return self.core.encrypt(data, password, level)
    
    def decrypt(self, ciphertext: bytes, password: str, level: int = 3) -> bytes:
        """
         Decrypt evoluído - reversão perfeita.
        
        Reverte rodas concêntricas APÓS o processamento normal,
        mantendo a ordem inversa correta.
        """
        # ════════════════════════════════════════════════════
        # PROCESSAMENTO NORMAL PRIMEIRO (sistema existente)
        # ════════════════════════════════════════════════════
        data = self.core.decrypt(ciphertext, password, level)
        
        # ════════════════════════════════════════════════════
        # CAMADA EXTRA: Reverter Rodas Concêntricas (se ativado)
        # ════════════════════════════════════════════════════
        if self.use_concentric:
            key = self.core._derive_key(password, len(data))
            base_angle = self._key_to_angle(key)
            
            # Reverter rodas concêntricas como pós-processamento
            data = self.ezekiel_advanced.apply_concentric_rotation(
                data, base_angle, reverse=True
            )
        
        return data
    
    def _key_to_angle(self, key: bytes) -> float:
        """Converte chave em ângulo para sincronização."""
        key_int = int.from_bytes(key[:8], 'big')
        return (key_int % 360) * np.pi / 180.0


# ════════════════════════════════════════════════════════════════════
# TESTES DE COMPATIBILIDADE E DESEMPENHO
# ════════════════════════════════════════════════════════════════════

def test_concentric_compatibility():
    """ Teste que o sistema evoluído é compatível com o original."""
    print("\n TESTE COMPATIBILIDADE - Rodas Concêntricas")
    print("="*60)
    
    # Sistema original
    crypto_original = KayosCryptoFinal()
    
    # Sistema evoluído (com rodas concêntricas)
    crypto_evolved = KayosCryptoEvolved(use_concentric=True)
    
    # Sistema evoluído (sem rodas - deve ser idêntico ao original)
    crypto_compat = KayosCryptoEvolved(use_concentric=False)
    
    test_data = b"Teste de compatibilidade entre versoes " + os.urandom(50)
    password = os.getenv("KAYOS_AUTH_PASSWORD", "default_insecure_password")
    
    print(f" Dados de teste: {len(test_data)} bytes")
    
    # Teste 1: Evoluído COM rodas vs Original
    enc_original = crypto_original.encrypt(test_data, password)
    enc_evolved = crypto_evolved.encrypt(test_data, password)
    
    # Devem ser DIFERENTES (rodas adicionam complexidade)
    different = enc_original != enc_evolved
    print(f" Com rodas vs Original: {' DIFERENTE' if different else ' IGUAL'}")
    
    # Teste 2: Evoluído SEM rodas vs Original (devem ser IDÊNTICOS)
    enc_compat = crypto_compat.encrypt(test_data, password)
    identical = enc_original == enc_compat
    print(f" Sem rodas vs Original: {' IDENTICO' if identical else ' DIFERENTE'}")
    
    # Teste 3: Reversibilidade do sistema evoluído
    dec_evolved = crypto_evolved.decrypt(enc_evolved, password)
    reversible = (test_data == dec_evolved)
    print(f" Reversibilidade Evoluido: {' PERFEITA' if reversible else ' FALHA'}")
    
    return different and identical and reversible


def test_concentric_avalanche():
    """ Teste de avalanche effect com rodas concêntricas."""
    print("\n TESTE AVALANCHE - Com Rodas Concêntricas")
    print("="*60)
    
    crypto = KayosCryptoEvolved(use_concentric=True)
    password = os.getenv("KAYOS_AUTH_PASSWORD", "default_insecure_password")
    
    # Dados de teste
    original = bytearray(256)
    for i in range(256):
        original[i] = (i * 7) % 256
    
    modified = bytearray(original)
    modified[0] ^= 0x01  # 1 bit diferente
    
    # Criptografar ambos
    enc_orig = crypto.encrypt(bytes(original), password)
    enc_mod = crypto.encrypt(bytes(modified), password)
    
    # Calcular avalanche
    diff_bits = sum(bin(a ^ b).count('1') for a, b in zip(enc_orig, enc_mod))
    total_bits = len(enc_orig) * 8
    avalanche = (diff_bits / total_bits) * 100
    
    print(f" Resultado Avalanche:")
    print(f"   Bits diferentes: {diff_bits}/{total_bits}")
    print(f"   Avalanche Effect: {avalanche:.2f}%")
    
    if avalanche > 45:
        print("    EXCELENTE! (>45%)")
    elif avalanche > 35:
        print("    BOM! (>35%)")
    else:
        print("     REGULAR (<35%)")
    
    return avalanche


if __name__ == "__main__":
    import os
    from .kayoscrypto_final import KayosCryptoFinal
    
    print("\n KAYOSCRYPTO EVOLVED - Rodas Concentricas de Ezequiel")
    print("="*70)
    
    # Executar testes
    compat_ok = test_concentric_compatibility()
    avalanche_score = test_concentric_avalanche()
    
    print("\n" + "="*70)
    print(" RESULTADOS EVOLUCAO:")
    print(f"   Compatibilidade: {' PERFEITA' if compat_ok else ' PROBLEMAS'}")
    print(f"   Avalanche: {avalanche_score:.2f}%")
    print(f"   Status: {' EVOLUCAO SUCESSO' if compat_ok else ' AJUSTES NECESSARIOS'}")
