# KayosCrypto - Documentação de Código

**Versão**: v5.0.1 ULTIMATE  
**Data**: 2 de Dezembro de 2025  
**Autor**: K6D-S (Kayos Digital Signature)  
**Status**: Produção (Baixo/Médio Risco)

---

## 1. Visão Geral da Base de Código

O KayosCrypto é um sistema criptográfico geométrico implementado em Python com otimizações Cython para performance crítica.

### Estatísticas do Repositório

```
Linguagem Principal: Python 3.8+
Linhas de Código: ~15.000+ (core)
Módulos Core: 12
Testes: 100% passando (9/9)
Cobertura: Módulos críticos validados
```

---

## 2. Estrutura de Diretórios

```
KayosCrypto/
├── src/
│   └── core/                    # Núcleo criptográfico
│       ├── kayoscrypto_ultimate.py    # Entry point (Spine)
│       ├── kayoscrypto_final.py       # Core System (Rib 3)
│       ├── ezekiel_concentric.py      # Multi-layer Rotation (Rib 2)
│       ├── fibonacci_direction.py     # Fibonacci Direction (Rib 1)
│       ├── geometric_permutation.py   # Permutações geométricas
│       ├── reversible_avalanche.pyx   # Avalanche (Cython)
│       ├── quantum_resistance_manager.py  # Resistência PQC (Rib 4)
│       ├── geometric_entropy_pool.py      # Pool de entropia (Rib 5)
│       └── palindrome_signature_system.py # Assinaturas (Rib 7)
│
├── demo/
│   └── live_demo/               # Demonstrações IBM Quantum
│       ├── quantum_teleportation_ALICE_TO_BOB.py
│       ├── quantum_teleportation_BOB_TO_ALICE.py
│       ├── quantum_relay_network.py
│       ├── quantum_relay_5hop.py
│       └── bell_state_teleportation.py
│
├── tests/
│   ├── security/                # Testes de segurança
│   └── performance/             # Testes de performance
│
├── logs/
│   └── ibm_quantum_jobs/        # Logs de execuções IBM Quantum
│
└── docs/                        # Documentação técnica
```

---

## 3. Módulos Core

### 3.1 Spine: `kayoscrypto_ultimate.py`

**Responsabilidade**: Orquestração do pipeline de 3 fases

```python
class KayosCryptoUltimate:
    """
    Coordenador central (Spine) da Arquitetura Fishbone.
    Orquestra 3 Ribs especializados em sequência.
    """
    
    def __init__(self, use_concentric=True, use_direction=True):
        self.rib1_fibonacci = FibonacciDirectionFixed()
        self.rib2_ezekiel = EzekielConcentricEngine()
        self.rib3_core = KayosCryptoFinal()
    
    def encrypt(self, plaintext: bytes, password: str, level: int = 3) -> bytes:
        """Pipeline: Rib1 → Rib2 → Rib3"""
        data = plaintext
        if level >= 1: data = self.rib1_fibonacci.apply(data, password)
        if level >= 2: data = self.rib2_ezekiel.apply(data, password)
        if level >= 3: data = self.rib3_core.encrypt(data, password)
        return data
    
    def decrypt(self, ciphertext: bytes, password: str, level: int = 3) -> bytes:
        """Pipeline inverso: Rib3 → Rib2 → Rib1"""
        data = ciphertext
        if level >= 3: data = self.rib3_core.decrypt(data, password)
        if level >= 2: data = self.rib2_ezekiel.reverse(data, password)
        if level >= 1: data = self.rib1_fibonacci.reverse(data, password)
        return data
```

### 3.2 Rib 1: `fibonacci_direction.py`

**Responsabilidade**: Transformações direcionais baseadas em Fibonacci

```python
class FibonacciDirectionFixed:
    """
    Pré-processamento usando sequência Fibonacci.
    Resultado isolado: 51.12% avalanche, 100% reversível.
    """
    
    FIBONACCI = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377]
    
    def determine_mode_from_key(self, key: bytes) -> int:
        """Deriva modo determinístico da chave."""
        return sum(key) % len(self.FIBONACCI)
    
    def apply(self, data: bytes, password: str) -> bytes:
        """Aplica transformação direcional Fibonacci."""
        # Implementação completa no arquivo
        pass
    
    def reverse(self, data: bytes, password: str) -> bytes:
        """Reverte transformação (100% reversível)."""
        pass
```

### 3.3 Rib 2: `ezekiel_concentric.py`

**Responsabilidade**: Três rotações perpendiculares sincronizadas

```python
class EzekielConcentricEngine:
    """
    Sistema de rodas concêntricas inspirado em Ezequiel.
    Três camadas: Main, Alpha (φ), Beta (espiral).
    Resultado isolado: 49.22% avalanche, gimbal-lock free.
    """
    
    PHI = 1.618033988749895  # Golden Ratio (alta precisão)
    
    def __init__(self):
        self.main_wheel = FibonacciWheel()
        self.alpha_wheel = GoldenRatioWheel(self.PHI)
        self.beta_wheel = SpiralWheel()
    
    def apply(self, data: bytes, password: str) -> bytes:
        """Aplica 3 rotações perpendiculares."""
        data = self.main_wheel.rotate(data)
        data = self.alpha_wheel.rotate(data)
        data = self.beta_wheel.rotate(data)
        return data
```

### 3.4 Rib 3: `kayoscrypto_final.py`

**Responsabilidade**: Base criptográfica sólida

```python
class KayosCryptoFinal:
    """
    Core System com primitivas criptográficas comprovadas.
    Componentes: GeometricPermutation + Feistel + ReversibleAvalanche.
    Garantia: 100% reversibilidade.
    """
    
    def __init__(self):
        self.permutation = GeometricPermutationEngine()
        self.feistel = FeistelNetwork(rounds=16)
        self.avalanche = ReversibleAvalancheEngine()
```

---

## 4. Compilação Cython

Módulos críticos têm versões Cython para performance:

```bash
# Compilar extensões Cython
python setup_cython.py build_ext --inplace

# Arquivos gerados:
# - ezekiel_concentric.cpython-312-x86_64-linux-gnu.so
# - fibonacci_direction.cpython-312-x86_64-linux-gnu.so
# - kayoscrypto_final.cpython-312-x86_64-linux-gnu.so
```

**Performance**:
- Python puro: 351 KB/s
- Com Cython: 500+ KB/s

---

## 5. Padrão de Importação

Todos os módulos usam fallback para compatibilidade:

```python
# Padrão universal de importação
try:
    from core.kayoscrypto_final import KayosCryptoFinal
except ImportError:
    from kayoscrypto_final import KayosCryptoFinal  # Fallback
```

---

## 6. Derivação de Chaves

Padrão consistente em todos os módulos:

```python
def _derive_key(self, password: str, length: int) -> bytes:
    """SHA-256 based key derivation."""
    key = hashlib.sha256(password.encode()).digest()
    return (key * (length // 32 + 1))[:length]
```

---

## 7. Garantias de Código

### 7.1 Reversibilidade (NÃO-NEGOCIÁVEL)

```python
# SEMPRE usar operações reversíveis:
✅ np.roll(data, shift)           # Circular shift
✅ data[permutation_indices]      # Index permutation
✅ data ^ key                     # XOR

# NUNCA usar operações lossy:
❌ data % modulo                  # Perda de informação
❌ hash(data)                     # One-way
❌ data // divisor                # Integer division
```

### 7.2 Determinismo

```python
# Toda operação deve ser determinística:
# Mesma entrada + mesma chave = mesma saída (sempre)

assert cipher.encrypt(data, key) == cipher.encrypt(data, key)
assert cipher.decrypt(cipher.encrypt(data, key), key) == data
```

---

## 8. Execução de Testes

```bash
# Suite completa
make test

# Testes de segurança (5/5 devem passar)
python3 tests/security/real_security_tests.py

# Testes de performance
python3 tests/performance/real_performance_tests_fixed.py

# Smoke test rápido
python3 src/core/kayoscrypto_ultimate.py
```

---

## 9. Métricas de Qualidade

| Métrica | Valor | Target |
|---------|-------|--------|
| Testes | 9/9 (100%) | 100% |
| Avalanche | 47.80% | >35% |
| Reversibilidade | 100% | 100% |
| Performance | 351-500 KB/s | >350 KB/s |
| Score Geral | 96.7% | >95% |

---

## 10. Dependências

```toml
# pyproject.toml
[project]
dependencies = [
    "numpy>=1.21.0",
    "cryptography>=3.4.0",
]

[project.optional-dependencies]
quantum = [
    "qiskit>=2.0.0",
    "qiskit-ibm-runtime>=0.40.0",
]
dev = [
    "pytest>=7.0.0",
    "cython>=3.0.0",
]
```

---

**Documento gerado automaticamente pelo sistema MPC-N**  
**Hash de integridade**: SHA256 do commit atual
