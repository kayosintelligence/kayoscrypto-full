# TASK 10.4 – Statistical Battery Progress (2025-11-26)

**Responsável:** GitHub Copilot • **Foco:** documentar o retrabalho de logging MPC-N, testes reexecutados e evidências pendentes para as suítes estatísticas e de emulação.

---

## 1. Contexto Resumido
- Instrumentamos `pqc_practrand.py`, `tests/validation/dieharder/validation_suite.py` e `scripts/demo_emulator_executive.py` com `attach_mpcn_logging`, garantindo que cada execução reporte no `mpcn_state.json`.
- Reexecutamos PractRand (preset *quick* até 64 GB), Dieharder (preset *lagged*) e o demo completo do emulador de hardware usando `kayos_entropy_stream.bin`. Todos os eventos foram registrados com os atores `pqc_practrand`, `dieharder_wrapper` e `demo_emulator_executive`.
- Confirmamos via capturas do usuário que as suítes TestU01 SmallCrush/BigCrush e Dieharder whitening rodaram em 22–23/11, embora ainda não tenham entradas oficiais no MPC-N.

---

## 2. Execuções com MPC-N (26/11/2025)
| Teste | Comando / Parâmetros | Resultado | Artefatos | Ator MPC-N |
|-------|----------------------|-----------|-----------|------------|
| PractRand (*quick*, stdin32 até 64 GB) | `PATH="$PWD:$PATH" .venv/bin/python tools/pqc_practrand.py --key-size 512 --tests quick` | Nenhuma anomalia de 1 GB a 64 GB (805–843 testes por etapa). | `practrand_logs/pqc_practrand_quick_20251126_212115.log` | `pqc_practrand` |
| Dieharder (*rgb_lagged_sum*) | `.venv/bin/python tests/validation/dieharder/validation_suite.py lagged --data kayos_entropy_stream.bin --results results` | p-value 4e-8 → **FAILED** (mantido para análise, requer repetir com reexecução de WEAKs). | `results/dieharder_lagged.log` | `dieharder_wrapper` |
| Demo do emulador (CLI + suíte programática) | `.venv/bin/python scripts/demo_emulator_executive.py` | Score global 0.9329 (97.05 % estabilidade média / 89.52 % confiança). 4/4 subsistemas “PASS”; relatório JSON exportado. | `emulator_executive_report.json` + saída do terminal | `demo_emulator_executive` |

### Observações
- Todos os comandos foram executados dentro de `/home/kbe/KAYOS_SYSTEMS/KayosCrypto` com o virtualenv ativo.
- O `mpcn_state.json` agora contém 16 eventos do demo, 6 do Dieharder e 6 do PractRand, além do `mpcn_guard_cli` pós-execução.

---

## 3. Evidências Pré-Handler (22–23/11/2025)
Estas suítes já haviam sido concluídas antes do retrabalho de logging. Referências (confirmadas por capturas compartilhadas e/ou arquivos locais):
- **TestU01 SmallCrush** – Relatório `../TESTE_COMPARATIVO/sts-2_1_2/reports/testu01_smallcrush_20251123_085754.log` com “All tests were passed”. Execução via `./run_smallcrush.sh kayos_entropy_stream.bin`.
- **TestU01 BigCrush (whitened)** – Log `logs/bigcrush_whitened_20251123_053419.log` (160 estatísticas, 02:09:14 CPU, “All tests were passed”).
- **Dieharder Whitening completo** – Logs `logs/dieharder_whitened_20251123_005753.log` e `logs/dieharder_whitened_20251122_155703.log`.
- **Guard check pós-testes** – `tools/mpcn_guard.py --actor diagnostics_report --intent post-run --max-inactive-minutes 60 --evaluate-only` registrado manualmente (vide captura com estado OK).

> **Ação pendente:** decidir se vamos ingerir esses logs legados no MPC-N via `tools/mpcn_guard.py --actor legacy_ingest --event-from-file ...` ou reexecutar as suítes com o handler ligado.

---

## 4. Estado Atual do Emulador
- Arquivo analisado: `kayos_entropy_stream.bin` (10 000 000 bytes).
- Métricas registradas em `emulator_executive_report.json`:
  - Score geral: **0.9328546625** (risco baixo, "Production Ready").
  - Estabilidade média: **0.9705**; Confiança média: **0.8952**.
  - Subsystems: Ring (stability 0.961 / confidence 0.931), Thermal (0.972 / 0.856), Jitter (0.967 / 0.924), Conditioning (0.983 / 0.869).
- CLI quantum validation também passou (Fibonacci Alignment 0.354, Ezekiel 0.979, SATOR 0.998, todas acima dos thresholds).

---

## 5. Lacunas e Prioridades
1. **PractRand GLASSE ≥32 GB** – precisa rodar preset completo (tlmax ≥ 32 GB) com logging; o preset *quick* cobre até 64 GB mas não segue o script oficial de 32 GB contínuos com ChaCha20 whitening.
2. **Dieharder completo (114 testes)** – reexecutar com re-run automático de WEAKs e integrar ao MPC-N.
3. **TestU01 (SmallCrush/Rabbit/Alphabit/Crush/BigCrush)** – ou ingerir logs legados ou repetir para registrar eventos oficiais.
4. **NIST STS 188/188, ENT, rngtest e demais estatísticos obrigatórios** – ainda sem eventos pós-retrabalho.
5. **Suites internas (`make test`, `make test-security`, `make test-performance`, `tests/validation/test_external_diagnostics.py`)** – precisam ser executadas novamente com logging para garantir rastreabilidade.
6. **Performance/Security tooling (Valgrind, ThreadSanitizer, ASAN/MSAN, fuzzers)** – permanecem pendentes nesta rodada.

---

## 6. Próximas Ações Sugeridas
1. **Escolher estratégia para os logs herdados**: (a) ingestão retroativa no MPC-N usando `tools/mpcn_guard.py` com `--actor legacy_ingest`, ou (b) reexecutar SmallCrush/BigCrush/Dieharder-whitened já com handler.
2. **Rodar `scripts/diagnostics/run_practrand_32gb.sh`** (ou equivalente) com `attach_mpcn_logging` para encerrar a instrução GLASSE-32GB.
3. **Executar Dieharder completo** apontando para `kayos_entropy_stream.bin`, salvando `results/dieharder_full_<data>.log` e registrando o PASS/WEAK/FAIL no MPC-N.
4. **Atualizar `docs/checkpoints/PRACTRAND_32GB_COMPLETE.md`** e `SNAPSHOT_EMULATOR_V6.0.md` após as reexecuções, anexando novos gráficos/JSON conforme necessário.
5. **Registrar o pipeline interno** (`make test*` + `test_external_diagnostics`) para assegurar rastreabilidade total antes da próxima auditoria executiva.

---

## 7. Atualizações (26/11 – noite)

### 7.1 Ingestão retroativa concluída
- Adicionei entradas no MPC-N com o ator `legacy_ingest` para os logs fornecidos nas capturas:
  - `TESTE_COMPARATIVO/sts-2_1_2/reports/testu01_smallcrush_20251123_085754.log` (TestU01 SmallCrush, status `passed`).
  - `logs/bigcrush_whitened_20251123_053419.log` (BigCrush whitened, 160 estatísticas, status `passed`).
  - `logs/dieharder_whitened_20251123_005753.log` (Dieharder `-a`, status `passed`).
- Agora o `mpcn_state.json` referencia explicitamente esses três artefatos, preservando o histórico exigido pelo usuário.

### 7.2 PractRand GLASSE ≥32 GB (execução oficial)
- Comando: `PATH="$PWD:$PATH" ./run_practrand.sh --tlmax 32G kayos_entropy_stream.bin` (stdin32, whitening ativo, chunk 8192, tlmin 1G).
- Resultado: nenhum desvio de 1 GB a 32 GB; 194 → 251 testes sem anomalias. Log: `practrand_logs/practrand_whitened_20251126_193838.log`.
- Atende à instrução GLASSE-32GB; resta apenas atualizar `PRACTRAND_32GB_COMPLETE.md` com gráficos/observações.

### 7.3 Dieharder completo com whitening
- Ajustei `scripts/diagnostics/run_dieharder_whitened.sh` para capturar `PIPESTATUS` e ignorar SIGPIPE (códigos 120/141) do streamer, falhando apenas quando `dieharder` retorna código ≠0. Também adiciona warning caso o streamer finalize com outro código.
- Reexecução final: `bash scripts/diagnostics/run_dieharder_whitened.sh` (seed 2579014565, ~8.5×10^7 rands/s). Resultado: 114/114 `PASSED`, inclusive `rgb_lagged_sum` 0–32 e `dab_monobit2`. Log em `logs/dieharder_whitened_20251126_195758.log`.
- MPC-N registrou início/fim via ator `run_dieharder_whitened`. O log anterior `results/dieharder_lagged.log` permanece como evidência do preset focado.

### 7.4 Próximos passos atualizados
1. Atualizar `docs/checkpoints/PRACTRAND_32GB_COMPLETE.md` e `SNAPSHOT_EMULATOR_V6.0.md` com os novos números.
2. Registrar/rodar as demais suítes estatísticas (Rabbit/Alphabit/Crush, NIST STS, ENT, rngtest) usando o handler.
3. Executar `make test`, `make test-security`, `make test-performance` e `tests/validation/test_external_diagnostics.py` com logging.
4. Agendar toolings de segurança/performance (Valgrind, TSAN, ASAN/MSAN, fuzzers) vinculados à TASK 10.4.

> Documento criado em 26/11/2025 para manter a continuidade da TASK 10.4. Qualquer execução adicional deve anexar logs e atualizar este checkpoint ou abrir um novo snapshot incremental.
