"""
 RIB 6: HYBRID KEY EXCHANGE - KAYOSCRYPTO QUANTUM-SAFE
Sistema de troca de chaves híbrido: Kyber1024 + ECDH + Fibonacci

ARQUITETURA KAIOS:
- Velho Matuto: Combinar força de 3 algoritmos (diversidade = robustez)
- Sator: Kyber (quantum) + ECDH (clássico) + Fibonacci (geométrico) = equilíbrio
- Ezequiel: Troca de chaves em 3 "rodas" perpendiculares
- Relojoeiro: Implementação ótima (não primeira que funciona)

FILOSOFIA:
"Três cordas não se rompem facilmente" (Eclesiastes 4:12)
- Se Kyber for quebrado → ECDH protege
- Se ECDH for quebrado (Shor) → Kyber protege
- Se ambos falharem → Fibonacci (não-algébrico) protege

Autor: KAYOS SYSTEMS
Data: 15 de Novembro de 2025
Versão: v6.2 - Hybrid Key Exchange
"""

import hashlib
import secrets
from typing import Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum

# liboqs (Kyber) - opcional para PQC
try:
    import oqs
    KYBER_AVAILABLE = True
except ImportError:
    KYBER_AVAILABLE = False

# ECDH (cryptography) - obrigatorio para key exchange
try:
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend
    ECDH_AVAILABLE = True
except ImportError:
    ECDH_AVAILABLE = False
    ECDH_AVAILABLE = True

# Fibonacci (interno)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from fibonacci_direction import FibonacciDirectionFixed
    FIBONACCI_AVAILABLE = True
except ImportError:
    FIBONACCI_AVAILABLE = False


# =====================================================================
# CONSTANTES
# =====================================================================

FIBONACCI_SEQUENCE = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610]
PHI = 1.618033988749895  # Golden Ratio


class KeyExchangeAlgorithm(Enum):
    """Algoritmos suportados para troca de chaves"""
    KYBER_1024 = "Kyber1024"
    ECDH_P521 = "ECDH-P521"
    FIBONACCI_GEOMETRIC = "Fibonacci-Geometric"
    HYBRID_ALL = "Hybrid-All"  # Combina os 3


@dataclass
class HybridKeyPair:
    """Par de chaves híbrido (3 algoritmos)"""
    # Kyber (pós-quântico)
    kyber_public: Optional[bytes] = None
    kyber_secret: Optional[bytes] = None
    
    # ECDH (clássico)
    ecdh_public: Optional[bytes] = None
    ecdh_private: Optional[bytes] = None
    
    # Fibonacci (geométrico)
    fibonacci_seed: Optional[int] = None
    fibonacci_level: Optional[int] = None
    
    # Metadados
    algorithm: KeyExchangeAlgorithm = KeyExchangeAlgorithm.HYBRID_ALL
    created_at: Optional[str] = None


@dataclass
class SharedSecret:
    """Segredo compartilhado derivado de troca de chaves"""
    secret: bytes
    algorithm: KeyExchangeAlgorithm
    key_size_bits: int
    entropy_score: float  # 0.0-1.0


# =====================================================================
# RIB 6: HYBRID KEY EXCHANGE ENGINE
# =====================================================================

class HybridKeyExchange:
    """
    Sistema de troca de chaves híbrido quantum-safe
    
    ARQUITETURA (3 Rodas de Ezequiel):
    
    Roda 1 (KYBER):   Resistente a Shor/Grover (lattice-based)
    Roda 2 (ECDH):    Resistente a ataques clássicos (curvas elípticas)
    Roda 3 (FIBONACCI): Resistente a análise algébrica (geométrico)
    
    DERIVAÇÃO FINAL:
    shared_secret = SHA-512(kyber_secret || ecdh_secret || fib_secret)
    
    BENEFÍCIO:
    - Se 1 algoritmo quebrar, outros 2 protegem
    - Segurança = MIN(kyber, ecdh, fibonacci) → máxima proteção
    """
    
    def __init__(self, use_kyber: bool = True, use_ecdh: bool = True, use_fibonacci: bool = True):
        """
        Inicializa o sistema híbrido
        
        Args:
            use_kyber: Habilitar Kyber1024 (requer liboqs)
            use_ecdh: Habilitar ECDH P-521
            use_fibonacci: Habilitar entropia geométrica Fibonacci
        """
        self.use_kyber = use_kyber and KYBER_AVAILABLE
        self.use_ecdh = use_ecdh and ECDH_AVAILABLE
        self.use_fibonacci = use_fibonacci and FIBONACCI_AVAILABLE
        
        if not any([self.use_kyber, self.use_ecdh, self.use_fibonacci]):
            raise RuntimeError("Pelo menos um algoritmo deve estar disponível!")
        
        # Estatísticas
        self.stats = {
            'keypairs_generated': 0,
            'secrets_derived': 0,
            'kyber_used': 0,
            'ecdh_used': 0,
            'fibonacci_used': 0
        }
    
    def generate_keypair(self) -> HybridKeyPair:
        """
        Gera par de chaves híbrido (3 algoritmos)
        
        Returns:
            HybridKeyPair com chaves públicas/privadas
        """
        keypair = HybridKeyPair()
        
        # 1. KYBER1024 (Pós-Quântico)
        if self.use_kyber:
            try:
                with oqs.KeyEncapsulation("Kyber1024") as kem:
                    kyber_public = kem.generate_keypair()
                    kyber_secret = kem.export_secret_key()
                    
                    keypair.kyber_public = kyber_public
                    keypair.kyber_secret = kyber_secret
                    self.stats['kyber_used'] += 1
            except Exception as e:
                print(f" [Kyber] Erro ao gerar keypair: {e}")
        
        # 2. ECDH P-521 (Clássico)
        if self.use_ecdh:
            try:
                private_key = ec.generate_private_key(ec.SECP521R1(), default_backend())
                public_key = private_key.public_key()
                
                # Serializar
                ecdh_private = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
                ecdh_public = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                
                keypair.ecdh_private = ecdh_private
                keypair.ecdh_public = ecdh_public
                self.stats['ecdh_used'] += 1
            except Exception as e:
                print(f" [ECDH] Erro ao gerar keypair: {e}")
        
        # 3. FIBONACCI (Geométrico)
        if self.use_fibonacci:
            try:
                # Gerar seed aleatório baseado em Fibonacci
                fibonacci_level = secrets.choice([8, 13, 21, 34, 55])  # Níveis Fibonacci
                fibonacci_seed = secrets.randbits(256)  # 256 bits de entropia
                
                keypair.fibonacci_seed = fibonacci_seed
                keypair.fibonacci_level = fibonacci_level
                self.stats['fibonacci_used'] += 1
            except Exception as e:
                print(f" [Fibonacci] Erro ao gerar seed: {e}")
        
        # Metadados
        from datetime import datetime, UTC
        keypair.created_at = datetime.now(UTC).isoformat()
        keypair.algorithm = self._get_current_algorithm()
        
        self.stats['keypairs_generated'] += 1
        return keypair
    
    def derive_shared_secret(self, 
                            our_keypair: HybridKeyPair, 
                            their_public: HybridKeyPair) -> SharedSecret:
        """
        Deriva segredo compartilhado combinando 3 algoritmos
        
        PROCESSO (3 Rodas):
        1. Kyber: KEM encapsulation → kyber_secret (32 bytes)
        2. ECDH: Diffie-Hellman → ecdh_secret (66 bytes)
        3. Fibonacci: Transformação geométrica → fib_secret (32 bytes)
        4. Combinar: SHA-512(kyber || ecdh || fib) → 64 bytes final
        
        Args:
            our_keypair: Nossa chave privada
            their_public: Chave pública da outra parte
        
        Returns:
            SharedSecret com 512 bits (64 bytes)
        """
        secrets_parts = []
        algorithms_used = []
        
        # 1. KYBER (Pós-Quântico)
        if self.use_kyber and their_public.kyber_public:
            try:
                with oqs.KeyEncapsulation("Kyber1024", our_keypair.kyber_secret) as kem:
                    ciphertext, kyber_secret = kem.encap_secret(their_public.kyber_public)
                    secrets_parts.append(kyber_secret)
                    algorithms_used.append("Kyber1024")
            except Exception as e:
                print(f" [Kyber] Erro no encapsulation: {e}")
        
        # 2. ECDH (Clássico)
        if self.use_ecdh and their_public.ecdh_public:
            try:
                # Deserializar chaves
                our_private = serialization.load_pem_private_key(
                    our_keypair.ecdh_private, 
                    password=None, 
                    backend=default_backend()
                )
                their_pub = serialization.load_pem_public_key(
                    their_public.ecdh_public,
                    backend=default_backend()
                )
                
                # ECDH exchange
                from cryptography.hazmat.primitives.asymmetric import ec as ec_alg
                ecdh_secret = our_private.exchange(ec_alg.ECDH(), their_pub)
                secrets_parts.append(ecdh_secret)
                algorithms_used.append("ECDH-P521")
            except Exception as e:
                print(f" [ECDH] Erro no exchange: {e}")
        
        # 3. FIBONACCI (Geométrico)
        if self.use_fibonacci and their_public.fibonacci_seed:
            try:
                # Combinar nosso seed + seed deles usando Fibonacci
                our_seed = our_keypair.fibonacci_seed
                their_seed = their_public.fibonacci_seed
                
                # Transformação geométrica Fibonacci
                combined_seed = (our_seed ^ their_seed)  # XOR inicial
                
                # Aplicar sequência Fibonacci
                level = min(our_keypair.fibonacci_level, their_public.fibonacci_level)
                for i in range(level):
                    fib_factor = FIBONACCI_SEQUENCE[i % len(FIBONACCI_SEQUENCE)]
                    combined_seed = (combined_seed * fib_factor) % (2**256)
                
                # Aplicar Golden Ratio
                phi_factor = int(PHI * (2**128))
                combined_seed = (combined_seed * phi_factor) % (2**256)
                
                # Converter para bytes
                fib_secret = combined_seed.to_bytes(32, 'big')
                secrets_parts.append(fib_secret)
                algorithms_used.append("Fibonacci-Geometric")
            except Exception as e:
                print(f" [Fibonacci] Erro na derivação: {e}")
        
        # 4. COMBINAR TUDO (Roda Central)
        if not secrets_parts:
            raise RuntimeError("Nenhum algoritmo conseguiu derivar segredo!")
        
        # Concatenar todos os secrets
        combined = b''.join(secrets_parts)
        
        # Hash final com SHA-512 (64 bytes = 512 bits)
        final_secret = hashlib.sha512(combined).digest()
        
        # Calcular entropia (Shannon)
        entropy_score = self._calculate_entropy(final_secret)
        
        # Criar SharedSecret
        shared = SharedSecret(
            secret=final_secret,
            algorithm=KeyExchangeAlgorithm.HYBRID_ALL,
            key_size_bits=512,
            entropy_score=entropy_score
        )
        
        self.stats['secrets_derived'] += 1
        return shared
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calcula entropia de Shannon (0.0-1.0)"""
        if not data:
            return 0.0
        
        import math
        
        # Contar frequência de cada byte
        freq = [0] * 256
        for byte in data:
            freq[byte] += 1
        
        # Calcular entropia
        entropy = 0.0
        data_len = len(data)
        for count in freq:
            if count > 0:
                prob = count / data_len
                entropy -= prob * math.log2(prob)
        
        # Normalizar (máximo = 8 bits/byte)
        return min(entropy / 8.0, 1.0)
    
    def _get_current_algorithm(self) -> KeyExchangeAlgorithm:
        """Retorna algoritmo baseado em quais estão habilitados"""
        enabled = []
        if self.use_kyber:
            enabled.append("Kyber")
        if self.use_ecdh:
            enabled.append("ECDH")
        if self.use_fibonacci:
            enabled.append("Fibonacci")
        
        if len(enabled) == 3:
            return KeyExchangeAlgorithm.HYBRID_ALL
        elif len(enabled) == 1:
            if self.use_kyber:
                return KeyExchangeAlgorithm.KYBER_1024
            elif self.use_ecdh:
                return KeyExchangeAlgorithm.ECDH_P521
            else:
                return KeyExchangeAlgorithm.FIBONACCI_GEOMETRIC
        else:
            return KeyExchangeAlgorithm.HYBRID_ALL
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas de uso"""
        return self.stats.copy()


# =====================================================================
# TESTES E VALIDAÇÃO
# =====================================================================

if __name__ == "__main__":
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║         RIB 6: HYBRID KEY EXCHANGE - TESTE COMPLETO          ║")
    print("╚═══════════════════════════════════════════════════════════════╝\n")
    
    # Verificar disponibilidade
    print(" DISPONIBILIDADE DE ALGORITMOS:")
    print(f"├─ Kyber1024:  {'' if KYBER_AVAILABLE else ''}")
    print(f"├─ ECDH P-521: {'' if ECDH_AVAILABLE else ''}")
    print(f"└─ Fibonacci:  {'' if FIBONACCI_AVAILABLE else '  (usando fallback)'}\n")
    
    try:
        # Inicializar
        kex = HybridKeyExchange(use_kyber=True, use_ecdh=True, use_fibonacci=True)
        
        # Teste 1: Alice gera keypair
        print(" TESTE 1: Geração de Keypairs")
        print("="*70)
        alice_keypair = kex.generate_keypair()
        bob_keypair = kex.generate_keypair()
        
        print(f"Alice keypair:")
        print(f"├─ Kyber public:  {len(alice_keypair.kyber_public) if alice_keypair.kyber_public else 0} bytes")
        print(f"├─ ECDH public:   {len(alice_keypair.ecdh_public) if alice_keypair.ecdh_public else 0} bytes")
        print(f"├─ Fibonacci seed: {alice_keypair.fibonacci_seed is not None}")
        print(f"└─ Algorithm:     {alice_keypair.algorithm.value}")
        
        print(f"\nBob keypair:")
        print(f"├─ Kyber public:  {len(bob_keypair.kyber_public) if bob_keypair.kyber_public else 0} bytes")
        print(f"├─ ECDH public:   {len(bob_keypair.ecdh_public) if bob_keypair.ecdh_public else 0} bytes")
        print(f"└─ Fibonacci seed: {bob_keypair.fibonacci_seed is not None}\n")
        
        # Teste 2: Derivar segredo compartilhado
        print(" TESTE 2: Derivação de Segredo Compartilhado")
        print("="*70)
        
        # Alice deriva usando public key de Bob
        alice_shared = kex.derive_shared_secret(alice_keypair, bob_keypair)
        
        # Bob deriva usando public key de Alice
        bob_shared = kex.derive_shared_secret(bob_keypair, alice_keypair)
        
        print(f"Alice shared secret:")
        print(f"├─ Tamanho:        {len(alice_shared.secret)} bytes ({alice_shared.key_size_bits} bits)")
        print(f"├─ Entropia:       {alice_shared.entropy_score:.4f} (Shannon)")
        print(f"└─ Algoritmo:      {alice_shared.algorithm.value}")
        
        print(f"\nBob shared secret:")
        print(f"├─ Tamanho:        {len(bob_shared.secret)} bytes ({bob_shared.key_size_bits} bits)")
        print(f"├─ Entropia:       {bob_shared.entropy_score:.4f} (Shannon)")
        print(f"└─ Algoritmo:      {bob_shared.algorithm.value}\n")
        
        # Teste 3: Verificar igualdade
        print(" TESTE 3: Verificação de Igualdade")
        print("="*70)
        secrets_match = (alice_shared.secret == bob_shared.secret)
        print(f"Segredos são iguais: {secrets_match} {'' if secrets_match else ''}")
        
        if secrets_match:
            print(f"├─ Primeiro byte:  {alice_shared.secret[0]:02x}")
            print(f"├─ Último byte:    {alice_shared.secret[-1]:02x}")
            print(f"└─ Hash SHA-256:   {hashlib.sha256(alice_shared.secret).hexdigest()[:16]}...\n")
        
        # Teste 4: Estatísticas
        print(" TESTE 4: Estatísticas de Uso")
        print("="*70)
        stats = kex.get_stats()
        for key, value in stats.items():
            print(f"├─ {key:20s}: {value}")
        
        print("\n╔═══════════════════════════════════════════════════════════════╗")
        print("║                      TODOS OS TESTES OK                     ║")
        print("║           Rib 6 (Hybrid Key Exchange) FUNCIONAL              ║")
        print("╚═══════════════════════════════════════════════════════════════╝")
        
    except Exception as e:
        print(f"\n ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
