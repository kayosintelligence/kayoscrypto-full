# SNAPSHOT_EMULATOR_V6.0.md

> Data: 2025-11-26 • Responsável: Nascimento • Objetivo: congelar o estado do emulador TRNG após a campanha PractRand ≥32 GB e revalidação executiva.

## 1. Contexto Operacional
- Stack validado: `kayos-trng-emulator` (Rust) → PyO3 bindings → `EmulatorDiagnosticsSuite` (Python) → `diagnostics_cli`.
- CLI e bindings executados com `PYTHONPATH=src .venv/bin/python`, garantindo carregamento da versão atualizada do KayosCryptoFinal e dos otimizadores.
- Pré-requisitos GLASSÉ: FibonacciAlignmentOptimizer corrigido (sem constante φ), CLI tests específicos passam (HMAC/Ed25519/tamper) e `test_quantum_optimization.py` cobre o regresso "perfect alignment".

## 2. Métricas Congeladas (kayos_entropy_stream.bin)
| Domínio | Métrica | Valor | Status |
|---------|---------|-------|--------|
| Quantum Validation | Fibonacci Direction Alignment | **0.354** | Pass (<0.62)
| | Ezekiel Wheel Tensor Balance | **0.979** | Pass (>0.60)
| | SATOR Cube Entropy | **0.998** | Pass (>0.92)
| Hardware Emulation | Ring Oscillator | stability=0.961, confidence=0.931 | Estável
| | Thermal Noise | stability=0.972, confidence=0.856 | Estável
| | Clock Jitter | stability=0.967, confidence=0.924 | Estável
| | Conditioning | stability=0.983, confidence=0.869 | Estável
| Exec. Demo | `emulator_executive_report.json` | Score global 0.9329 • 4/4 subsistemas PASS | 
| Diagnostics CLI | `tests/validation/test_external_diagnostics.py` | 4/4 passando (0.74 s) | 
| Statistical Pipeline | `./run_rngtest.sh --tests 200000` | 199 810 PASS / 190 FAIL (FIPS Monobit/Poker/Runs/LongRun) | (investigação)
| NIST STS | `run_nist_auto.sh` (1000 streams) | Dataset 125 MB executado; relatório `AlgorithmTesting/finalAnalysisReport.txt` mostrou 0/1000 PASS em todos os testes → revisar configuração | (diagnóstico) |
| Regression | `tests/validation/test_quantum_optimization.py::test_pipeline_forces_correction_on_perfect_alignment` | 1/1 passando (warning SciPy conhecido) | 

## 3. Evidências de Correção Fibonacci
```
 DADOS REAIS (kayos_entropy_stream.bin) → 0.354361
 DADOS ALEATÓRIOS → 0.353028
 DADOS CONSTANTES → 0.000000
 SEQUÊNCIA LINEAR → 0.153172
```
- `scripts/enterprise_fibonacci.py` retornou 0.357878 com estratégia `correcao_agressiva`.
- `scripts/debug_fibonacci.py --test` exibiu pares original/otimizado distintos (0.353108 → 0.359363).

## 4. Estado dos Testes Relacionados
- `pytest tests/cli/test_cli_signatures.py` → 4/4 (execução interativa, confirma PW workflows e detecta KayosCryptoFinal correto).
- `pytest tests/validation/test_quantum_optimization.py -k fibonacci` → 1/1 (warnings de precisão mantidos).
- `./run_rngtest.sh --tests 200000 kayos_entropy_stream.bin` → 190 falhas FIPS (Monobit 28, Poker 25, Runs 71, Long Run 66, Continuous 0). MPC-N evento `run_rngtest_whitened` marcado como `completed_with_failures`; análise em andamento para exportar blocos problemáticos.
- `run_nist_auto.sh` → executado com `STREAM_COUNT=1000` após atualização do script. Log `sts-2_1_2/nist_output_full_1000streams_20251126_221255.log`; `finalAnalysisReport.txt` acusa `0/1000` aprovações para todos os testes, indicando provável desconfiguração (ex.: STS ainda tratando dataset como único stream). Dataset permanece válido (`data/kayoscrypto_sequences.bin`, 125 MB) e deve ser reutilizado após corrigir o preset.
- Suites restantes (security/performance) aguardam execução após PractRand ≥32 GB.

## 5. Riscos e Dependências
1. **Safety/Security (Prioridade GLASSÉ)**: PractRand ≥32 GB complete , porém rngtest continua apontando 0.095 % de falhas; investigar chunk/whitening antes do hand-off executivo. BigCrush infinito ainda pendente.
2. **State (Memória Persistente)**: `system_state.json` e `CONTINUITY_GUIDE.md` seguem ausentes; este snapshot serve como mitigação temporária.
3. **NIST STS**: automação atualizada para 1000 streams, porém o `finalAnalysisReport` retornou `0/1000` aprovações (aparente falha de configuração/parse). Precisamos inspecionar `experiments/AlgorithmTesting/input_1000seq.txt` e parâmetros do `assess` para confirmar se o STS está mapeando corretamente as 1000 sequências.
4. **Infra**: `tests/cli` dependem do `.venv/bin/python`; garantir uso do virtualenv nas automações de alto volume.

## 6. Próximas Ações Obrigatórias
1. **PractRand ≥32 GB** realizado em 26/11/2025 usando `run_practrand.sh --tlmax 32G` (log `practrand_logs/practrand_whitened_20251126_193838.log`).
2. **rngtest**: capturar blocos reprovados (usar `--blockstats`/`--pipe` + hexdump) e validar se falhas desaparecem com chunk maior ou com dataset recém-gerado.
3. **NIST STS**: depurar configuração do `assess` (ex.: `input_1000seq.txt`, parâmetros `gen`, `numOfBitStreams`) para explicar o `0/1000` observado. Reexecutar após ajustar e anexar novo relatório + entrada MPC-N `diagnostics.nist:complete` com status .
4. **Preparar pipeline BigCrush** e demais baterias (Dieharder completo, Rabbit/Alphabit/Crush) usando o mesmo fluxo ChaCha20.
5. **Restaurar Memória Persistente** (`system_state.json`, `CONTINUITY_GUIDE.md`) para que futuros snapshots não dependam apenas deste documento.

---
Este snapshot é o baseline oficial para a etapa de alto volume. Qualquer regressão detectada após a execução do PractRand deve ser comparada contra estes números antes de alterar o pipeline.
