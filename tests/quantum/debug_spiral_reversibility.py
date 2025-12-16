#!/usr/bin/env python3
"""Debug: Por que transformação palindrômica não é reversível?"""

import numpy as np
import hashlib
from nacl.signing import SigningKey

# Testar reversibilidade da transformação
def spiral_read(matrix, clockwise=True):
    """Cópia do método _spiral_read"""
    side = matrix.shape[0]
    result = []
    
    top, bottom = 0, side - 1
    left, right = 0, side - 1
    
    if clockwise:
        while top <= bottom and left <= right:
            for i in range(left, right + 1):
                result.append(matrix[top, i])
            top += 1
            for i in range(top, bottom + 1):
                result.append(matrix[i, right])
            right -= 1
            if top <= bottom:
                for i in range(right, left - 1, -1):
                    result.append(matrix[bottom, i])
                bottom -= 1
            if left <= right:
                for i in range(bottom, top - 1, -1):
                    result.append(matrix[i, left])
                left += 1
    else:
        while top <= bottom and left <= right:
            for i in range(top, bottom + 1):
                result.append(matrix[i, left])
            left += 1
            for i in range(left, right + 1):
                result.append(matrix[bottom, i])
            bottom -= 1
            if left <= right:
                for i in range(right, left - 1, -1):
                    result.append(matrix[top, i])
                top += 1
            if top <= bottom:
                for i in range(bottom, top - 1, -1):
                    result.append(matrix[i, right])
                right -= 1
    
    return np.array(result, dtype=np.uint8)

print("="*80)
print("TESTE: Reversibilidade de Transformação Spiral")
print("="*80)

# Gerar Ed25519 signature real
signing_key = SigningKey.generate()
message = b"Test"
signed = signing_key.sign(message)
ed25519_sig = signed.signature  # 64 bytes

print(f"\n1. Ed25519 Signature Original:")
print(f"   {ed25519_sig.hex()[:32]}... (64 bytes)")

# Transformação forward
arr = np.frombuffer(ed25519_sig, dtype=np.uint8)
matrix = arr.reshape((8, 8))
transformed_forward = spiral_read(matrix, clockwise=True)
forward_bytes = transformed_forward.tobytes()

print(f"\n2. Após Spiral Forward (clockwise):")
print(f"   {forward_bytes.hex()[:32]}... (64 bytes)")

# Transformação backward (tentativa de reverter)
matrix2 = transformed_forward.reshape((8, 8))
transformed_backward = spiral_read(matrix2, clockwise=False)
backward_bytes = transformed_backward.tobytes()

print(f"\n3. Após Spiral Backward (anti-clockwise):")
print(f"   {backward_bytes.hex()[:32]}... (64 bytes)")

# Comparar
print(f"\n4. Comparação:")
print(f"   Original == Backward: {ed25519_sig == backward_bytes}")
print(f"   Match rate: {sum(a == b for a, b in zip(ed25519_sig, backward_bytes)) / len(ed25519_sig) * 100:.1f}%")

if ed25519_sig != backward_bytes:
    print(f"\n PROBLEMA: Spiral não é perfeitamente reversível!")
    print(f"   Primeiros 10 bytes:")
    print(f"   Original: {ed25519_sig[:10].hex()}")
    print(f"   Backward: {backward_bytes[:10].hex()}")
    
    # Encontrar onde diverge
    for i, (a, b) in enumerate(zip(ed25519_sig, backward_bytes)):
        if a != b:
            print(f"\n   Primeira divergência no byte {i}: {a} != {b}")
            break

print("\n"+"="*80)
print("CONCLUSÃO")
print("="*80)
print("""
Spiral read/write NÃO é uma transformação reversível!

Problema:
- spiral_read(clockwise=True) → spiral_read(clockwise=False) ≠ original
- Ordem de leitura é diferente da ordem de escrita

Solução:
OPÇÃO A: Usar transformação trivial reversível (ex: XOR com padrão)
OPÇÃO B: Mapear índices corretamente (spiral_write + spiral_read)
OPÇÃO C: Não transformar Ed25519 signature (manter 64 bytes puros)

Recomendação: OPÇÃO C - manter Ed25519 signature pura, propriedade
palindrômica apenas na estrutura (forward = signature, backward = signature[::-1])
""")
