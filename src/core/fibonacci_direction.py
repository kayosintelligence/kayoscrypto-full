import os
#!/usr/bin/env python3
"""
 FIBONACCI DIRECTION FIXED - Versão Determinística
====================================================

Implementação enxuta com rotações circulares determinísticas.
"""

import numpy as np
from hashlib import sha256

class FibonacciDirectionFixed:
    """
     Motor de Direção Fibonacci - VERSÃO CORRIGIDA
    
    Diferença da versão anterior:
    - Modo determinado APENAS pela chave (não pelos dados)
    - Sempre reversível porque key → mode é determinístico
    - Verso/Anverso aplicado de forma consistente
    """
    
    def __init__(self):
        self.fibonacci_seq = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
        self.golden_ratio = 1.618033988749895
    
    def determine_mode_from_key(self, key: bytes) -> str:
        """
        Determina modo (verso/anverso) APENAS da chave.
        
        Garantia: mesma chave → sempre mesmo modo
        """
        key_hash = sha256(key).digest()
        mode_byte = key_hash[0]
        
        # 50/50 chance de verso ou anverso
        return "verso" if (mode_byte % 2 == 0) else "anverso"
    
    def apply_direction(self, data: bytes, key: bytes, mode: str, reverse: bool = False) -> bytes:
        """Aplica direção Fibonacci usando apenas rotações circulares."""
        if len(data) < 2:
            return data

        key_hash = sha256(key).digest()
        intensity = (key_hash[1] % 100 + 1) / 100.0  # 0.01 a 1.00
        size = len(data)

        # Determina shifts baseados na sequência Fibonacci
        shifts = []
        for idx, fib in enumerate(self.fibonacci_seq):
            if fib >= size:
                break

            base_shift = int(round(fib * intensity * (idx + 1) * 2))  # Multiplicado por 2 para mais intensidade
            if base_shift == 0:
                continue

            if mode == "verso":
                shifts.append(base_shift)
            else:
                shifts.append(-base_shift)

        if not shifts:
            return data

        # Para reversão, aplica shifts em ordem inversa e com sinal invertido
        if reverse:
            shifts = [-s for s in reversed(shifts)]

        net_shift = sum(shifts) % size
        if net_shift == 0:
            return data

        rotated = np.roll(np.frombuffer(data, dtype=np.uint8), net_shift)
        return rotated.tobytes()


class KayosCryptoWithDirectionFixed:
    """
     KayosCrypto com Direcionamento Fibonacci CORRIGIDO
    
    Versão determinística e 100% reversível.
    """
    
    def __init__(self, use_direction: bool = True):
        from .kayoscrypto_final import KayosCryptoFinal
        
        self.core = KayosCryptoFinal()
        self.use_direction = use_direction
        
        if use_direction:
            self.direction_engine = FibonacciDirectionFixed()
    
    def encrypt(self, plaintext: bytes, password: str, level: int = 3) -> bytes:
        """Encrypt com direcionamento determinístico."""
        data = plaintext
        
        if self.use_direction:
            # Derivar modo da chave (sempre o mesmo para mesma senha)
            key = self.core._derive_key(password, len(data))
            mode = self.direction_engine.determine_mode_from_key(key)
            
            # Aplicar direcionamento
            data = self.direction_engine.apply_direction(data, key, mode, reverse=False)
        
        # Core processing
        return self.core.encrypt(data, password, level)
    
    def decrypt(self, ciphertext: bytes, password: str, level: int = 3) -> bytes:
        """Decrypt com reversão correta."""
        # Core processing primeiro
        data = self.core.decrypt(ciphertext, password, level)
        
        if self.use_direction:
            # Reverter direcionamento (mesma chave → mesmo modo)
            key = self.core._derive_key(password, len(data))
            mode = self.direction_engine.determine_mode_from_key(key)
            
            # Aplicar reversão (reverse=True inverte o modo automaticamente)
            data = self.direction_engine.apply_direction(data, key, mode, reverse=True)
        
        return data


# ════════════════════════════════════════════════════════════════════
# TESTES DE VALIDAÇÃO
# ════════════════════════════════════════════════════════════════════

def test_direction_fixed_reversibility():
    """ Teste de reversibilidade do sistema corrigido."""
    print("\n TESTE REVERSIBILIDADE - Fibonacci Direction FIXED")
    print("=" * 60)
    
    crypto = KayosCryptoWithDirectionFixed(use_direction=True)
    password = os.getenv("KAYOS_AUTH_PASSWORD", "default_insecure_password")
    
    test_cases = [
        (b"Hello World!", "simple"),
        (b"A" * 200, "repetitive"),
        (bytes(range(256)), "sequence"),
        (b"Mixed content 123!@#$%^&*()", "mixed"),
    ]
    
    all_passed = True
    
    for test_data, test_type in test_cases:
        encrypted = crypto.encrypt(test_data, password)
        decrypted = crypto.decrypt(encrypted, password)
        
        passed = test_data == decrypted
        status = " PASSOU" if passed else " FALHOU"
        
        print(f"   {test_type:12s} ({len(test_data):3d} bytes): {status}")
        
        if not passed:
            all_passed = False
            print(f"      Original:  {test_data[:20]}")
            print(f"      Decrypted: {decrypted[:20]}")
    
    print("\n" + "=" * 60)
    if all_passed:
        print(" TODOS OS TESTES PASSARAM - SISTEMA REVERSÍVEL!")
    else:
        print(" ALGUNS TESTES FALHARAM - VERIFICAR IMPLEMENTAÇÃO")
    
    return all_passed


def test_direction_fixed_avalanche():
    """ Teste de avalanche do sistema corrigido."""
    print("\n TESTE AVALANCHE - Fibonacci Direction FIXED")
    print("=" * 50)
    
    crypto = KayosCryptoWithDirectionFixed(use_direction=True)
    password = os.getenv("KAYOS_AUTH_PASSWORD", "default_insecure_password")
    
    original = bytearray(300)
    for i in range(300):
        original[i] = (i * 11) % 256
    
    modified = bytearray(original)
    modified[150] ^= 0x01  # 1 bit no meio
    
    enc_orig = crypto.encrypt(bytes(original), password)
    enc_mod = crypto.encrypt(bytes(modified), password)
    
    diff_bits = sum(bin(a ^ b).count('1') for a, b in zip(enc_orig, enc_mod))
    total_bits = len(enc_orig) * 8
    avalanche = (diff_bits / total_bits) * 100
    
    print(f" Resultado:")
    print(f"   Bits diferentes: {diff_bits}/{total_bits}")
    print(f"   Avalanche Effect: {avalanche:.2f}%")
    
    if avalanche > 45:
        status = " EXCELENTE"
    elif avalanche > 35:
        status = " BOM"
    else:
        status = "  REGULAR"
    
    print(f"   Status: {status}")
    
    return avalanche


if __name__ == "__main__":
    print("\n FIBONACCI DIRECTION FIXED - VALIDAÇÃO")
    print("=" * 70)
    
    # Testes
    reversibility_ok = test_direction_fixed_reversibility()
    avalanche_score = test_direction_fixed_avalanche()
    
    print("\n" + "=" * 70)
    print(" RESUMO FINAL:")
    print("=" * 70)
    print(f" Reversibilidade: {'PERFEITA' if reversibility_ok else 'PROBLEMAS'}")
    print(f" Avalanche: {avalanche_score:.2f}%")
    
    if reversibility_ok and avalanche_score > 35:
        print("\n FIBONACCI DIRECTION FIXED: APROVADO!")
        print(" Pronto para integração no sistema ULTIMATE")
    else:
        print("\n  Sistema requer ajustes adicionais")
