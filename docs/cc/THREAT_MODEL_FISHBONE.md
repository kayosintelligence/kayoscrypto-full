# KayosCrypto Threat Model (Fishbone) — Pré-Auditoria CC

## 1. TOE e Escopo
- **TOE (Target of Evaluation)**: Módulo criptográfico KayosCryptoUltimate (Spine) com Ribs Fibonacci Direction, Ezekiel Concentric e Core System, implementado em Python 3.12 com extensões NumPy/Cython opcionais.
- **TOE Environment**: Servidor Linux (Ubuntu 24.04), hardware x86_64, operador humano autorizado, guardião MPC-N ativo.
- **Interfaces externas**: APIs `KayosCryptoUltimate.encrypt/decrypt`, scripts CLI (`kayoscrypto_cli.py`, `run_practrand_*`, `run_dieharder_whitened.sh`, etc.), arquivos de log (`practrand_logs/*`, `logs/*`), mecanismo MPC-N.
- **Ativos protegidos**: Chaves derivadas (SHA-256), dados plaintext/ciphertext temporários, fluxos de entropia, logs de diagnóstico e estado MPC-N.

## 2. Ameaças (Fishbone)
| Categoria (Rib) | Descrição | Controles existentes |
|-----------------|-----------|----------------------|
| **Fibonacci Direction (pré-processamento)** | Ataques na derivação direcional (forçar padrão previsível) | Sequência determinística baseada na chave, validação por PractRand whitening. |
| **Ezekiel Concentric (roda em roda)** | Desalinhamento de rodas → perda de reversibilidade | Testes unitários + `real_security_tests.py`, pipeline reversível 100%. |
| **Core System (Feistel/permutação)** | Falhas de permutação, avalanche insuficiente | `GeometricPermutationEngine`, `ReversibleAvalancheEngine`, métricas 47.80% avalanche. |
| **MPC-N Spine (operacional)** | Execuções fora de controle, ausência de rastreabilidade | `tools/mpcn_guard.py` com intents, heartbeats, traps; `mpcn_state.json` audita eventos. |
| **Streams/Entropy** | Fonte MatutoRegulatorio sofre bias → compromete SP 800-90B | Campanhas `practrand_raw_stream_*` até 1 TB; logs registram anomalias e correções. |
| **PQC/Quantum** | Ataques Shor/Grover; degradação de chaves | `docs/PQC_VALIDATION_REPORT_2025-11-24.md`, `reports/key_sensitivity_*.json`, Roadmap Rib4/5/6. |

## 3. Atores e Capacidades
| Ator | Capacidades | Mitigações |
|------|-------------|------------|
| Operador autorizado | Acesso shell, pode iniciar scripts | Checklists, guard MPC-N, logs imutáveis. |
| Atacante remoto | Não possui acesso shell; tenta explorar interface CLI | Inputs validados, sem serviços de rede expostos; CLI requer credenciais locais. |
| Atacante com acesso parcial | Pode editar arquivos ou interromper processos | Git history + MPC-N detectam alterações/erros; need-to-know para credenciais. |
| Auditor externo | Precisa validar controles | Documentação consolidada (DIAGNOSTICS_, PRE_AUDIT_, Security Policy). |

## 4. Análise STRIDE
| Categoria | Risco | Contramedidas |
|-----------|-------|----------------|
| Spoofing | Iniciar run sem guardião | MPC-N recusa intents sem heartbeat; logs registram `alerta` quando contexto obsoleto. |
| Tampering | Modificar scripts `run_*` | Git + revisão; plan future hash/signature; Security Policy proíbe execuções fora do Approved Mode. |
| Repudiation | Negar execução falha | `mpcn_state.json` guarda timestamps, exit codes, notas (queda de energia, Ctrl+C). |
| Information Disclosure | Vazamento de chaves | Chaves derivadas em memória volátil; CLI usa `getpass`; sem logs contendo plaintext. |
| Denial of Service | Interromper long run (energia, Ctrl+C) | Eventos `error` → reexecuções documentadas; alvo ISO 27001 A.16.1. |
| Elevation of Privilege | Inserir código malicioso | Barreiras Git + MPC-N; futuro: assinatura dos scripts e execuções em ambiente restrito. |

## 5. Requisitos Residenciais
1. Formalizar política de revocação/atualização das chaves (link com Incident Response).
2. Criar checklist de integridade (hashes) para scripts `run_*` antes de execuções críticas.
3. Adicionar testes de comportamento anômalo (fuzz CLI, fault injection) para AVA_VAN.

## 6. Evidências Relacionadas
- `docs/diagnostics/DIAGNOSTICS_MPCN_GUARD_2025-11-23.md`
- `mpcn_state.json`
- `docs/fips/SECURITY_POLICY_v0.md`
- `docs/diagnostics/PRE_AUDIT_FIPS_ISO_EXPECTATIVA_2025-11-26.md`
- `practrand_logs/*`, `reports/key_sensitivity_*.json`
