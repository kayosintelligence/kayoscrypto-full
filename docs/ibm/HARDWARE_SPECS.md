# Especificações do Hardware IBM Quantum

## Processadores Disponíveis

### Visão Geral da Frota

| QPU | Qubits | Arquitetura | Status | Erro 2Q | CLOPS |
|-----|--------|-------------|--------|---------|-------|
| ibm_fez | 156 | Heron r2 | Online | 2.67E-3 | 220k |
| ibm_pittsburgh | 156 | Heron r3 | Online | 1.68E-3 | 250k |
| ibm_boston | 156 | Heron r3 | Online | 1.17E-3 | 245k |
| ibm_marrakesh | 156 | Heron r2 | Online | 2.47E-3 | 200k |
| ibm_torino | 133 | Heron r1 | Online | 2.58E-3 | 220k |
| ibm_kingston | 156 | Heron r2 | Paused | 2.04E-3 | 250k |

---

## IBM Quantum ibm_fez (Utilizado)

### Especificações Gerais

| Parâmetro | Valor |
|-----------|-------|
| **Nome** | ibm_fez |
| **Arquitetura** | Heron r2 |
| **Número de Qubits** | 156 |
| **Conectividade** | Heavy-hex |
| **Temperatura** | ~15 mK (-273.135°C) |
| **Localização** | IBM Data Center |
| **Região API** | us-east (Washington DC) |

### Métricas de Qualidade

| Métrica | Valor | Descrição |
|---------|-------|-----------|
| Erro 2Q (mediana) | 2.67 × 10⁻³ | Taxa de erro para portas de 2 qubits |
| Erro de leitura (mediana) | 9.155 × 10⁻³ | Taxa de erro na medição |
| Erro 2Q (em camadas) | 4.92 × 10⁻³ | Erro para portas paralelas |
| CLOPS | 220,000 | Circuit Layer Operations Per Second |

### Tempos de Coerência

| Parâmetro | Valor Típico | Descrição |
|-----------|--------------|-----------|
| T1 | ~300 μs | Tempo de relaxação (energia) |
| T2 | ~200 μs | Tempo de decoerência (fase) |
| Tempo de porta 1Q | ~30 ns | Duração de porta de 1 qubit |
| Tempo de porta 2Q | ~300 ns | Duração de porta ECR |
| Tempo de medição | ~1 μs | Duração da medição |

### Conjunto de Portas Nativas

| Porta | Símbolo | Descrição |
|-------|---------|-----------|
| ID | I | Identidade |
| RZ | Rz(θ) | Rotação em Z |
| SX | √X | Raiz quadrada de X |
| X | X | Pauli-X |
| ECR | ECR | Echoed Cross-Resonance |

### Conectividade (Heavy-Hex)

```
Topologia Heavy-Hex:
    0 ─ 1 ─ 2 ─ 3 ─ 4
    │       │       │
   14 ─ 15 ─ 16 ─ 17 ─ 18
        │       │       
       ...     ...
       
(156 qubits em arranjo heavy-hex)
```

---

## Comparativo de Arquiteturas

### Heron r1 vs r2 vs r3

| Característica | Heron r1 | Heron r2 | Heron r3 |
|----------------|----------|----------|----------|
| Qubits máx | 133 | 156 | 156 |
| Erro 2Q típico | 2.5E-3 | 2.5E-3 | 1.5E-3 |
| CLOPS | 220k | 220k | 250k |
| Disponibilidade | 2024 | 2024 | 2025 |

### Evolução da Tecnologia IBM

```
2019: Falcon (27 qubits)
2020: Hummingbird (65 qubits)
2021: Eagle (127 qubits)
2023: Osprey (433 qubits)
2024: Heron (133-156 qubits, melhor qualidade)
2025: Flamingo (planejado)
```

---

## Limitações e Considerações

### Decoerência

```
Tempo de execução < T2 (~200 μs)

Para nosso circuito:
- Profundidade: 21 camadas
- Tempo estimado: ~5-10 μs
- Margem: >95% do tempo de coerência disponível ✓
```

### Erros Típicos

| Fonte | Taxa | Impacto |
|-------|------|---------|
| Porta 1Q | ~0.03% | Baixo |
| Porta 2Q (ECR) | ~0.27% | Médio |
| Medição | ~0.9% | Médio |
| Crosstalk | Variável | Baixo-Médio |
| Decoerência | Exponencial | Depende da profundidade |

### Filas e Disponibilidade

| Período | Tempo na fila típico |
|---------|----------------------|
| Horário comercial (US) | 1-5 minutos |
| Fora do horário | < 1 minuto |
| Alta demanda | 10-30 minutos |

---

## Acesso e Autenticação

### Credenciais

| Campo | Valor |
|-------|-------|
| Conta | kayos intelligence |
| User ID | IBMid-693001ALCG |
| Instância | open-instance |
| Plano | open |
| Canal | ibm_quantum_platform |

### Limites do Plano Open

| Recurso | Limite |
|---------|--------|
| Tempo de execução mensal | 10 minutos |
| Jobs simultâneos | 5 |
| Shots por job | 100,000 |
| Qubits | Todos disponíveis |

### Código de Conexão

```python
from qiskit_ibm_runtime import QiskitRuntimeService

service = QiskitRuntimeService(
    channel='ibm_quantum_platform',
    token='YOUR_API_TOKEN'
)

# Listar backends disponíveis
backends = service.backends()

# Selecionar o menos ocupado
backend = service.least_busy(
    operational=True,
    simulator=False
)
```

---

## Monitoramento

### Dashboard IBM Quantum

URL: https://quantum.ibm.com/computers

### Métricas em Tempo Real

- Status do backend (Online/Offline/Paused)
- Tarefas pendentes na fila
- Calibrações recentes
- Histórico de disponibilidade

### Alertas

- Manutenção programada
- Calibração em andamento
- Degradação de performance

---

## Referências

1. IBM Quantum Documentation: https://quantum.ibm.com/docs/
2. Qiskit Documentation: https://qiskit.org/documentation/
3. IBM Quantum Network: https://www.ibm.com/quantum/network
4. Heron Processor: https://research.ibm.com/blog/ibm-quantum-roadmap-2025

---

*Documento atualizado em 2 de Dezembro de 2025*
