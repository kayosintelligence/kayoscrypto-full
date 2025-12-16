# TASK 11.0 – Quantum Resistance Manager Plan (24 Nov 2025)

##  Scope
- Registrar o estado pós-campanha PractRand 1.5 TB (-tf 2) e preparar o terreno para o Rib 4 (QuantumResistanceManager) rumo à meta 99.5% maturidade KAIOS.
- Definir requisitos funcionais, métricas-alvo, dependências e artefatos mínimos antes de iniciar a implementação.

---

## 1. Contexto Atual
- **Estabilidade estatística**: PractRand folding `-tf 2` executado até 1.5 TB sem anomalias (`practrand_logs/practrand_whitened_20251124_011640.log`).
- **Documentação**: `docs/diagnostics/DIAGNOSTICS_MPCN_GUARD_2025-11-23.md` atualizado com a campanha manchete e tabela de evidências.
- **Roadmap**: v6.0 QUANTUM exige elevar resistência quântica estimada de 75% → 95%+ com verificação formal (Rib 4 + Rib 5 + Rib 6).

---

## 2. Objetivos do QuantumResistanceManager (QRM)
1. **Avaliação**: calcular `shor_resistance`, `grover_resistance` e `entropy_score` por fase (Fibonacci, Ezekiel, Core) + score consolidado (`>=0.95` alvo v6.0).
2. **Detecção**: identificar vulnerabilidades (ex.: key-size insuficiente p/ Grover, acoplamento previsível entre rodas Ezekiel) e emitir relatório com severidade (//).
3. **Recomendações**: mapear ações concretas (duplicar comprimento de chave, randomizar seeds geométricas, integrar GeometricEntropyPool).
4. **Integração MPC-N**: cada avaliação gera evento `diagnostics.qrm:*` com caminhos dos relatórios e parâmetros usados.

---

## 3. Requisitos Funcionais
- `class QuantumResistanceManager` em `src/core/quantum_resistance_manager.py` com:
  - `assess_vulnerability(level: int) -> VulnerabilityReport`
  - `recommend_improvements(report: VulnerabilityReport) -> List[Action]`
  - `export_tensor() -> Dict[str, Any]` (espelha Filosofia Ezequiel: tensor multidimensional).
- `VulnerabilityReport` deve conter:
  - `phase_scores`: dict com fases {"fibonacci", "ezekiel", "core"}
  - `aggregate_score`
  - `risk_flags`: lista com {id, description, severity, detection_method}
  - `evidence_refs`: caminhos de logs/tests (PractRand, Dieharder, etc.).
- CLI/Spine hook: `KayosCryptoUltimate` aceita `use_qrm=True` e expõe `cipher.qrm_report(password=..., level=3)`.

---

## 4. Métricas e Benchmarks
| Métrica | Baseline (v5.0.1) | Target QRM | Observações |
|--------|--------------------|------------|-------------|
| Shor Resistance | 0.85 | ≥0.95 | depende de novo key schedule + análise modular |
| Grover Resistance | 0.70 | ≥0.95 | exige avaliação sobre duplicação de key-size e GeometricEntropyPool |
| Geometric Entropy Score | 0.70 (estimado) | ≥0.96 | precisa métricas numéricas a partir das rodas (phi, fibonacci, beta spiral) |
| Audit Coverage | Estatístico 100% | + Formal (≥2 provas) | combinar execuções MPC-N com relatórios matemáticos |

---

## 5. Dependências & Inputs
- `src/core/kayoscrypto_ultimate.py`: precisa de ponto de injeção do QRM.
- `docs/ribs/` → criar `RIB_4_QUANTUM_RESISTANCE_MANAGER.md` após primeira implementação.
- `tests/security/` → adicionar suíte `test_quantum_resistance_manager.py` cobrindo:
  - determinismo (mesmo input → mesmo relatório)
  - sensibilidade (alterar chave +1 bit deve derrubar score ≥0.02)
  - reversibilidade intacta (QRM nunca altera dados criptografados).
- Dados externos: baseline 1 TB/1.5 TB PractRand, Dieharder, TestU01, rngtest; esses logs serão citados como evidência inicial.

---

## 6. Artefatos Previstos
1. **Código**: `src/core/quantum_resistance_manager.py` + hook na Spine.
2. **Tests**: `tests/security/test_quantum_resistance_manager.py` + entrada em `make test-security`.
3. **Docs**: `docs/ribs/RIB_4_QUANTUM_RESISTANCE_MANAGER.md` + atualização em `docs/INDEX.md` e `docs/technical/ARCHITECTURE.md`.
4. **Checkpoint futuro**: `docs/checkpoints/TASK_11.1_QRM_IMPLEMENTATION_COMPLETE.md` (quando código & testes estiverem 100%).

---

## 7. Cronograma Sugerido
1. **Semana 1**: protótipo da classe + relatório fake baseado nos logs existentes (sem alterar pipeline). Validar formato com docs.
2. **Semana 2**: integrar cálculos reais (fórmulas para Shor/Grover). Conectar a `KayosCryptoUltimate` e criar testes.
3. **Semana 3**: preparar documentação Rib 4 + rodar `make test-security` + PractRand spot-check 64 GB.
4. **Semana 4**: revisão executiva + publicação do checkpoint TASK 11.1.

---

## 8. Estado MPC-N Pós-Marco PractRand
- Guard `run_practrand_whitened` finalizado com `diagnostics.practrand:complete` às 04:42 UTC.
- Antes de iniciar desenvolvimento do QRM, emitir heartbeat `log_event(actor='qrm_dev', action='heartbeat', details={'intent':'roadmap.rib4'})` quando o trabalho migrar para código, garantindo rastreabilidade.

> _Checkpoint gerado automaticamente após o run PractRand 1.5 TB para manter a Memória Persistente ativa e liberar o próximo Rib._
