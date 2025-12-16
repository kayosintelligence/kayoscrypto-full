# KayosCrypto Security Policy v0 (Pré-Auditoria FIPS 140-3)

## 1. Introdução
Este documento descreve, em nível preliminar, como o módulo criptográfico KayosCrypto (versão 5.0.1 Ultimate) atende aos requisitos da Security Policy exigida pelo FIPS 140-3/ISO 19790. Ele será refinado junto ao laboratório acreditado, mas já define o escopo, os modos aprovados e os mecanismos de controle operacional usados durante as campanhas de diagnóstico.

## 2. Escopo do Módulo
- **Tipo**: Software-only, nível de validação alvo 1-2.
- **Limites do módulo**: pipeline Python `KayosCryptoUltimate` (Spine) + Ribs (Fibonacci Direction, Ezekiel Concentric, Core System) executando no ambiente Linux x86_64 (Ubuntu 24.04 LTS) com Python 3.12, NumPy e extensões Cython opcionais.
- **Dependências externas**: NumPy, hashlib (SHA-256) e ChaCha20 do módulo whitening (quando ativado). Nenhum hardware dedicado de proteção física é reivindicado nesta fase.

## 3. Modos Operacionais
| Modo | Descrição | Estado | Evidência |
|------|-----------|--------|-----------|
| **Approved Mode A** | KayosCryptoUltimate com whitening ChaCha20 (`stream_kayos_sequences.py -w`), PractRand/Dieharder/TestU01 coordenados pelo MPC-N, logs armazenados em `practrand_logs/` e `logs/`. | Ativo | `docs/diagnostics/DIAGNOSTICS_MPCN_GUARD_2025-11-23.md`, `mpcn_state.json`, `practrand_logs/practrand_whitened_*`. |
| **Approved Mode B** | KayosCryptoUltimate sem whitening (MatutoRegulatorio bruto) para análise SP 800-90B; pipeline `run_practrand_raw_stream`. Usa o mesmo controle MPC-N. | Ativo apenas para testes de entropia. | `practrand_logs/practrand_raw_stream_20251125_*`, eventos `diagnostics.practrand_raw:*`. |
| **Non-Approved Mode** | Qualquer uso fora das combinações acima (ex.: desativar MPC-N, modificar scripts `run_*` sem checklist). Não reivindicado para validação. | Deve ser evitado em ambientes certificados. | Políticas internas (este documento + MPC-N). |

## 4. Serviços
| Serviço | Interface | Descrição | Regras |
|---------|----------|-----------|--------|
| **Encrypt/Decrypt** | API `KayosCryptoUltimate.encrypt/decrypt` | Executa fluxo Spine (Fibonacci → Ezekiel → Core). | Disponível apenas em modos Approved A/B. Dependem de senha transformada via SHA-256. |
| **Streams Diagnósticos** | Scripts `run_practrand_whitened.sh`, `run_practrand_raw_stream`, `run_dieharder_whitened.sh` etc. | Gera dados estatísticos e logs para monitoramento contínuo. | Sempre rodar sob guardião MPC-N com intents `diagnostics.*`. |
| **MPC-N Guard** | `tools/mpcn_guard.py`, `kayoscrypto.mpcn.context.log_event` | Registra eventos (start, error, complete, heartbeat). | Deve ser executado antes de qualquer campanha longa e ao final para comprovar atividade. |

## 5. Regras de Segurança
1. **Controle de Acesso Lógico**: Apenas operadores autorizados podem iniciar scripts `run_*`. O MPC-N exige intents específicos (`diagnostics.practrand`, `diagnostics.dieharder`, etc.) e rejeita execuções com mais de 60 min de inatividade sem heartbeat.
2. **Proteção de Chaves/Senhas**: Chaves derivadas com SHA-256 não são armazenadas. Ao usar CLI, senhas são capturadas via `getpass` e descartadas após uso.
3. **Autotestes**: Antes de cada release, executar `make test`, `make test-security`, `make test-performance` e suites externas (PractRand 1.5 TB, TestU01, Dieharder). Falhas registradas no MPC-N disparam investigação.
4. **Eventos de Falha**: Qualquer interrupção (queda de energia, Ctrl+C acidental) deve ser registrada via `log_event(... action='failed'/'error')` com tentativa subsequente documentada.
5. **Integridade da Fonte de Entropia**: Campanhas `run_practrand_raw_stream` devem usar gerador MatutoRegulatorio com buffer de 1 TB para evitar EOF prematuro. Logs e notas ficam disponíveis para SP 800-90B.

## 6. Mitigações Requeridas (Próximas Etapas)
- Documentar explicitamente que o módulo depende da plataforma anfitriã para proteção física (FIPS §4.6), classificando como “Software module”.
- Adicionar descrição formal de mitigação de tamper lógico (verificações de integridade dos scripts, assinatura opcional dos logs).
- Expandir seção de serviços com tabelas FIPS (entrada/saída, rol de chaves criticas) após revisão do laboratório.

## 7. Referências
- `docs/diagnostics/DIAGNOSTICS_MPCN_GUARD_2025-11-23.md`
- `docs/diagnostics/PRE_AUDIT_FIPS_ISO_EXPECTATIVA_2025-11-26.md`
- `mpcn_state.json`
- `practrand_logs/` (whitened e raw)
- `docs/PQC_VALIDATION_REPORT_2025-11-24.md`
